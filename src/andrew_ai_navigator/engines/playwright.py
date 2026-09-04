from __future__ import annotations

import asyncio
import re
from pathlib import Path
from typing import Any, Sequence
from urllib.parse import urlsplit
from uuid import uuid4

from ..engine import EngineCapabilities
from ..input import CoordinateFrame, MouseButton, Point
from ..models import ElementRef, Observation, TabRef, Viewport
from ..perception import (
    ObservationFrame,
    PerceptionChannel,
    Rect,
    SurfaceEvidence,
    SurfaceObject,
)
from ..security import UnsafeTarget, resolve_public_http_target


class PlaywrightUnavailable(RuntimeError):
    pass


class EngineNotStarted(RuntimeError):
    pass


class UnknownTab(KeyError):
    pass


class StaleTarget(RuntimeError):
    pass


class StaleCoordinateFrame(RuntimeError):
    pass


_SAFE_IDENTITY = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]{0,63}$")
_INTERACTIVE_SELECTOR = (
    'a,button,input,textarea,select,summary,[role],[tabindex],'
    '[contenteditable="true"]'
)


class PlaywrightEngine:
    """Persistent Chromium implementation of the Navigator browser contract.

    One engine instance owns one durable Navigator identity. The AI platform is
    not part of this class: profiles live in Navigator runtime state and the
    engine may be driven by any client through the Core.
    """

    capabilities = EngineCapabilities(
        semantic_click=True,
        semantic_fill=True,
        pointer_move=True,
        pointer_click=True,
        pointer_drag=True,
        pointer_wheel=True,
        keyboard_keys=True,
        keyboard_text=True,
        screenshots=True,
        dom_observation=True,
        accessibility_observation=False,
        geometry_observation=True,
        frame_observation=True,
        browser_state_observation=True,
        javascript=True,
        cookies_storage=True,
        tls_validation=True,
        host_io=False,
    )

    def __init__(
        self,
        *,
        identity: str = "andrew",
        runtime_root: str | Path | None = None,
        headless: bool = False,
        viewport_width: int = 1440,
        viewport_height: int = 900,
        browser_channel: str | None = None,
    ) -> None:
        if not _SAFE_IDENTITY.fullmatch(identity):
            raise ValueError("identity must use only letters, digits, dot, underscore or dash")
        if viewport_width <= 0 or viewport_height <= 0:
            raise ValueError("viewport dimensions must be positive")

        self.identity = identity
        self.runtime_root = Path(runtime_root).expanduser() if runtime_root else (
            Path.home() / ".local" / "share" / "andrew-ai-navigator"
        )
        self.headless = headless
        self.viewport_width = viewport_width
        self.viewport_height = viewport_height
        self.browser_channel = browser_channel

        self._pw: Any | None = None
        self._context: Any | None = None
        self._pages: dict[str, Any] = {}
        self._sessions: dict[str, set[str]] = {}
        self._generation: dict[str, int] = {}
        self._targets: dict[str, dict[str, Any]] = {}
        self._screenshots: dict[str, tuple[int, bytes]] = {}
        self._target_cache: dict[str, tuple[str, ...]] = {}

    @property
    def profile_dir(self) -> Path:
        return self.runtime_root / "identities" / self.identity / "profile"

    async def start(self) -> None:
        if self._context is not None:
            return

        try:
            from playwright.async_api import async_playwright
        except ImportError as exc:
            raise PlaywrightUnavailable(
                "Playwright is optional. Install andrew-ai-navigator[playwright] "
                "and install a Playwright browser engine."
            ) from exc

        self.profile_dir.mkdir(parents=True, exist_ok=True)
        self._pw = await async_playwright().start()

        launch_kwargs: dict[str, Any] = {
            "user_data_dir": str(self.profile_dir),
            "headless": self.headless,
            "viewport": {"width": self.viewport_width, "height": self.viewport_height},
            "ignore_https_errors": False,
            "accept_downloads": True,
        }
        if self.browser_channel:
            launch_kwargs["channel"] = self.browser_channel

        self._context = await self._pw.chromium.launch_persistent_context(**launch_kwargs)
        await self._context.route("**/*", self._route_guard)

        # Persistent contexts may create an initial blank page. Navigator only
        # exposes pages that belong to explicit sessions.
        for page in tuple(self._context.pages):
            try:
                await page.close()
            except Exception:
                pass

        self._context.on("page", self._page_created)

    async def stop(self) -> None:
        if self._context is not None:
            await self._context.close()
        if self._pw is not None:
            await self._pw.stop()

        self._pw = None
        self._context = None
        self._pages.clear()
        self._sessions.clear()
        self._generation.clear()
        self._targets.clear()
        self._screenshots.clear()

    async def new_tab(self, session_id: str) -> TabRef:
        context = self._require_context()
        if not session_id:
            raise ValueError("session_id cannot be empty")

        page = await context.new_page()
        tab_id = f"t_{uuid4().hex}"
        self._register_page(session_id, tab_id, page)
        return TabRef(session_id=session_id, tab_id=tab_id)

    async def list_tabs(self, session_id: str) -> tuple[TabRef, ...]:
        return tuple(
            TabRef(session_id=session_id, tab_id=tab_id)
            for tab_id in sorted(self._sessions.get(session_id, ()))
            if tab_id in self._pages
        )

    async def close_tab(self, tab: TabRef) -> None:
        page = self._get_page(tab)
        await page.close()
        self._forget_tab(tab)

    async def navigate(self, tab: TabRef, url: str) -> None:
        page = self._get_page(tab)
        await asyncio.to_thread(resolve_public_http_target, url)
        await page.goto(url, wait_until="domcontentloaded")
        self._invalidate(tab.tab_id)

    async def observe(self, tab: TabRef) -> Observation:
        frame = await self.observe_surface(tab)
        page = self._get_page(tab)
        try:
            text = await page.locator("body").inner_text(timeout=3000)
        except Exception:
            text = ""

        elements: list[ElementRef] = []
        for obj in frame.objects:
            role = self._evidence_value(obj, "role")
            name = self._evidence_value(obj, "name") or self._evidence_value(obj, "text")
            elements.append(ElementRef(id=obj.id, role=role, name=name))

        return Observation(
            tab=tab,
            generation=frame.generation,
            url=page.url,
            title=await page.title(),
            viewport=frame.viewport,
            text=text,
            elements=tuple(elements),
            metadata={
                "identity": self.identity,
                "perception": "surface",
                "screenshot_ref": frame.screenshot_ref or "",
            },
        )

    async def observe_surface(self, tab: TabRef) -> ObservationFrame:
        page = self._get_page(tab)
        generation = self._generation.get(tab.tab_id, 0) + 1
        self._generation[tab.tab_id] = generation

        viewport = await self._viewport(page)
        screenshot = await page.screenshot(type="png", full_page=False)
        self._screenshots[tab.tab_id] = (generation, screenshot)

        objects: list[SurfaceObject] = []
        target_map: dict[str, Any] = {}
        counter = 0

        for frame_index, browser_frame in enumerate(page.frames):
            frame_id = f"f{frame_index}"
            try:
                locator_set = browser_frame.locator(_INTERACTIVE_SELECTOR)
                count = min(await locator_set.count(), 300)
            except Exception:
                continue

            for index in range(count):
                locator = locator_set.nth(index)
                try:
                    data = await locator.evaluate(
                        """el => ({
                            tag: (el.tagName || '').toLowerCase(),
                            role: el.getAttribute('role') || '',
                            aria: el.getAttribute('aria-label') || '',
                            placeholder: el.getAttribute('placeholder') || '',
                            title: el.getAttribute('title') || '',
                            value: typeof el.value === 'string' ? el.value : '',
                            text: (el.innerText || el.textContent || '').trim().slice(0, 500),
                            disabled: Boolean(el.disabled) || el.getAttribute('aria-disabled') === 'true'
                        })"""
                    )
                    visible = await locator.is_visible()
                    box = await locator.bounding_box()
                except Exception:
                    continue

                if not visible or not box or box["width"] <= 0 or box["height"] <= 0:
                    continue

                counter += 1
                object_id = f"e{counter}"
                evidence: list[SurfaceEvidence] = [
                    SurfaceEvidence(PerceptionChannel.DOM, "tag", str(data.get("tag", ""))),
                    SurfaceEvidence(PerceptionChannel.FRAME, "frame", frame_id),
                    SurfaceEvidence(PerceptionChannel.GEOMETRY, "visible", "true"),
                ]

                role = str(data.get("role") or "")
                if role:
                    evidence.append(SurfaceEvidence(PerceptionChannel.DOM, "role", role))

                name = (
                    str(data.get("aria") or "")
                    or str(data.get("placeholder") or "")
                    or str(data.get("title") or "")
                    or str(data.get("text") or "")
                    or str(data.get("value") or "")
                )
                if name:
                    evidence.append(SurfaceEvidence(PerceptionChannel.DOM, "name", name[:500]))
                    evidence.append(SurfaceEvidence(PerceptionChannel.DOM, "text", name[:500]))

                rect = Rect(
                    x=float(box["x"]),
                    y=float(box["y"]),
                    width=float(box["width"]),
                    height=float(box["height"]),
                )
                actionable = not bool(data.get("disabled"))

                objects.append(
                    SurfaceObject(
                        id=object_id,
                        generation=generation,
                        evidence=tuple(evidence),
                        rect=rect,
                        frame_id=frame_id,
                        actionable=actionable,
                        metadata={"frame_url": browser_frame.url},
                    )
                )
                target_map[object_id] = locator

        self._targets[tab.tab_id] = target_map
        return ObservationFrame(
            tab=tab,
            generation=generation,
            viewport=viewport,
            objects=tuple(objects),
            screenshot_ref=f"memory://{tab.tab_id}/{generation}/surface.png",
            metadata={
                "identity": self.identity,
                "url": page.url,
                "frame_count": str(len(page.frames)),
            },
        )

    async def click_element(self, tab: TabRef, element_id: str) -> None:
        locator = self._get_target(tab, element_id)
        await locator.click()
        self._invalidate(tab.tab_id)

    async def fill_element(self, tab: TabRef, element_id: str, value: str) -> None:
        locator = self._get_target(tab, element_id)
        await locator.fill(value)
        self._invalidate(tab.tab_id)

    async def pointer_move(self, tab: TabRef, frame: CoordinateFrame, point: Point) -> None:
        page = self._get_page(tab)
        await self._validate_coordinate_frame(tab, frame, point)
        await page.mouse.move(point.x, point.y)

    async def pointer_click(
        self,
        tab: TabRef,
        frame: CoordinateFrame,
        point: Point,
        button: MouseButton = MouseButton.LEFT,
        click_count: int = 1,
    ) -> None:
        if click_count <= 0:
            raise ValueError("click_count must be positive")
        page = self._get_page(tab)
        await self._validate_coordinate_frame(tab, frame, point)
        await page.mouse.click(point.x, point.y, button=button.value, click_count=click_count)
        self._invalidate(tab.tab_id)

    async def pointer_down(self, tab: TabRef, button: MouseButton = MouseButton.LEFT) -> None:
        page = self._get_page(tab)
        await page.mouse.down(button=button.value)

    async def pointer_up(self, tab: TabRef, button: MouseButton = MouseButton.LEFT) -> None:
        page = self._get_page(tab)
        await page.mouse.up(button=button.value)
        self._invalidate(tab.tab_id)

    async def pointer_wheel(self, tab: TabRef, delta_x: float, delta_y: float) -> None:
        page = self._get_page(tab)
        await page.mouse.wheel(delta_x, delta_y)
        self._invalidate(tab.tab_id)

    async def pointer_drag(
        self,
        tab: TabRef,
        frame: CoordinateFrame,
        start: Point,
        end: Point,
    ) -> None:
        page = self._get_page(tab)
        await self._validate_coordinate_frame(tab, frame, start)
        await self._validate_coordinate_frame(tab, frame, end)
        await page.mouse.move(start.x, start.y)
        await page.mouse.down(button=MouseButton.LEFT.value)
        await page.mouse.move(end.x, end.y, steps=12)
        await page.mouse.up(button=MouseButton.LEFT.value)
        self._invalidate(tab.tab_id)

    async def key_down(self, tab: TabRef, key: str) -> None:
        page = self._get_page(tab)
        await page.keyboard.down(key)

    async def key_up(self, tab: TabRef, key: str) -> None:
        page = self._get_page(tab)
        await page.keyboard.up(key)
        self._invalidate(tab.tab_id)

    async def key_press(self, tab: TabRef, key: str) -> None:
        page = self._get_page(tab)
        await page.keyboard.press(key)
        self._invalidate(tab.tab_id)

    async def key_chord(self, tab: TabRef, keys: Sequence[str]) -> None:
        if not keys:
            raise ValueError("keys cannot be empty")
        page = self._get_page(tab)
        await page.keyboard.press("+".join(keys))
        self._invalidate(tab.tab_id)

    async def type_text(self, tab: TabRef, text: str) -> None:
        page = self._get_page(tab)
        await page.keyboard.insert_text(text)
        self._invalidate(tab.tab_id)

    async def screenshot(self, tab: TabRef) -> bytes:
        page = self._get_page(tab)
        image = await page.screenshot(type="png", full_page=False)
        generation = self._generation.get(tab.tab_id, 0)
        self._screenshots[tab.tab_id] = (generation, image)
        return image

    async def latest_surface_png(self, tab: TabRef, generation: int) -> bytes:
        self._get_page(tab)
        cached = self._screenshots.get(tab.tab_id)
        if cached is None or cached[0] != generation:
            raise StaleTarget("no screenshot exists for that observation generation")
        return cached[1]

    async def _route_guard(self, route: Any) -> None:
        url = route.request.url
        scheme = urlsplit(url).scheme.lower()

        if scheme in {"data", "blob", "about"}:
            await route.continue_()
            return
        if scheme not in {"http", "https"}:
            await route.abort("blockedbyclient")
            return

        try:
            await asyncio.to_thread(self._resolve_cached, url)
        except UnsafeTarget:
            await route.abort("blockedbyclient")
            return
        await route.continue_()

    def _resolve_cached(self, url: str) -> None:
        parsed = urlsplit(url)
        origin = f"{parsed.scheme.lower()}://{parsed.hostname}:{parsed.port or (443 if parsed.scheme == 'https' else 80)}"
        if origin in self._target_cache:
            return
        target = resolve_public_http_target(url)
        self._target_cache[origin] = target.addresses

    def _page_created(self, page: Any) -> None:
        try:
            asyncio.get_running_loop().create_task(self._adopt_popup(page))
        except RuntimeError:
            return

    async def _adopt_popup(self, page: Any) -> None:
        try:
            opener = await page.opener()
        except Exception:
            opener = None
        if opener is None:
            return

        for parent_tab_id, known_page in tuple(self._pages.items()):
            if known_page is opener:
                session_id = self._session_for_tab(parent_tab_id)
                if session_id is None:
                    return
                tab_id = f"t_{uuid4().hex}"
                self._register_page(session_id, tab_id, page)
                return

    def _register_page(self, session_id: str, tab_id: str, page: Any) -> None:
        self._pages[tab_id] = page
        self._sessions.setdefault(session_id, set()).add(tab_id)
        self._generation[tab_id] = 0
        self._targets[tab_id] = {}

    def _forget_tab(self, tab: TabRef) -> None:
        self._pages.pop(tab.tab_id, None)
        self._generation.pop(tab.tab_id, None)
        self._targets.pop(tab.tab_id, None)
        self._screenshots.pop(tab.tab_id, None)
        session_tabs = self._sessions.get(tab.session_id)
        if session_tabs is not None:
            session_tabs.discard(tab.tab_id)
            if not session_tabs:
                self._sessions.pop(tab.session_id, None)

    def _session_for_tab(self, tab_id: str) -> str | None:
        for session_id, tabs in self._sessions.items():
            if tab_id in tabs:
                return session_id
        return None

    def _get_page(self, tab: TabRef) -> Any:
        page = self._pages.get(tab.tab_id)
        if page is None or self._session_for_tab(tab.tab_id) != tab.session_id:
            raise UnknownTab(tab.tab_id)
        return page

    def _get_target(self, tab: TabRef, element_id: str) -> Any:
        self._get_page(tab)
        locator = self._targets.get(tab.tab_id, {}).get(element_id)
        if locator is None:
            raise StaleTarget(
                "element reference is absent or stale; obtain a new surface observation"
            )
        return locator

    def _invalidate(self, tab_id: str) -> None:
        self._generation[tab_id] = self._generation.get(tab_id, 0) + 1
        self._targets[tab_id] = {}
        self._screenshots.pop(tab_id, None)

    async def _viewport(self, page: Any) -> Viewport:
        data = await page.evaluate(
            """() => ({
                width: window.innerWidth,
                height: window.innerHeight,
                dpr: window.devicePixelRatio || 1,
                scrollX: window.scrollX || 0,
                scrollY: window.scrollY || 0
            })"""
        )
        return Viewport(
            width=int(data["width"]),
            height=int(data["height"]),
            device_scale_factor=float(data["dpr"]),
            scroll_x=float(data["scrollX"]),
            scroll_y=float(data["scrollY"]),
        )

    async def _validate_coordinate_frame(
        self,
        tab: TabRef,
        frame: CoordinateFrame,
        point: Point,
    ) -> None:
        page = self._get_page(tab)
        if frame.session_id != tab.session_id or frame.tab_id != tab.tab_id:
            raise StaleCoordinateFrame("coordinate frame belongs to another tab")
        if frame.generation != self._generation.get(tab.tab_id, 0):
            raise StaleCoordinateFrame("coordinate frame belongs to a stale observation")
        if not frame.contains(point):
            raise StaleCoordinateFrame("point falls outside the recorded viewport")

        viewport = await self._viewport(page)
        if (
            frame.viewport_width != viewport.width
            or frame.viewport_height != viewport.height
            or abs(frame.device_scale_factor - viewport.device_scale_factor) > 1e-6
        ):
            raise StaleCoordinateFrame("viewport changed since the coordinate frame was observed")

    def _require_context(self) -> Any:
        if self._context is None:
            raise EngineNotStarted("start the Playwright engine before using it")
        return self._context

    @staticmethod
    def _evidence_value(obj: SurfaceObject, kind: str) -> str | None:
        for item in obj.evidence:
            if item.kind == kind and item.value:
                return item.value
        return None
