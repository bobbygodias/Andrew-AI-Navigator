from __future__ import annotations

from dataclasses import replace

from .engine import BrowserEngine
from .fusion import fuse_surface_objects
from .input import CoordinateFrame, MouseButton, Point
from .models import Provenance, TabRef
from .perception import ObservationFrame, PerceptionChannel, Rect, SurfaceObject
from .policy import ActionContext, ActionKind, Decision, PolicyEngine
from .visual import VisualFrame, VisualPerceptor


class NavigatorPolicyDenied(PermissionError):
    pass


class SurfaceTargetUnavailable(RuntimeError):
    pass


class Navigator:
    """Provider-independent orchestration layer for Web perception and action."""

    def __init__(
        self,
        engine: BrowserEngine,
        *,
        policy: PolicyEngine | None = None,
        visual_perceptor: VisualPerceptor | None = None,
        strict_visual: bool = False,
    ) -> None:
        self.engine = engine
        self.policy = policy or PolicyEngine()
        self.visual_perceptor = visual_perceptor
        self.strict_visual = strict_visual

    async def start(self) -> None:
        await self.engine.start()

    async def stop(self) -> None:
        await self.engine.stop()

    async def new_tab(self, session_id: str) -> TabRef:
        return await self.engine.new_tab(session_id)

    async def list_tabs(self, session_id: str) -> tuple[TabRef, ...]:
        return tuple(await self.engine.list_tabs(session_id))

    async def close_tab(self, tab: TabRef) -> None:
        await self.engine.close_tab(tab)

    async def navigate(
        self,
        tab: TabRef,
        url: str,
        *,
        provenance: Provenance = Provenance.AGENT,
        explicit_authorization: bool = False,
    ) -> None:
        self._authorize(
            ActionKind.NAVIGATE,
            destination_url=url,
            provenance=provenance,
            explicit_authorization=explicit_authorization,
        )
        await self.engine.navigate(tab, url)

    async def observe_surface(self, tab: TabRef) -> ObservationFrame:
        base = await self.engine.observe_surface(tab)
        if self.visual_perceptor is None:
            return base

        try:
            pixels = await self.engine.surface_png(tab, base.generation)
            visual_frame = VisualFrame(
                tab=tab,
                generation=base.generation,
                viewport=base.viewport,
                image_bytes=pixels,
            )
            visual_objects = tuple(await self.visual_perceptor.perceive(visual_frame))
            fused = fuse_surface_objects(
                base.objects,
                visual_objects,
                generation=base.generation,
            )
        except Exception as exc:
            if self.strict_visual:
                raise
            metadata = dict(base.metadata)
            metadata["visual_perceptor"] = self.visual_perceptor.name
            metadata["visual_status"] = "error"
            metadata["visual_error_type"] = type(exc).__name__
            return replace(base, metadata=metadata)

        metadata = dict(base.metadata)
        metadata["visual_perceptor"] = self.visual_perceptor.name
        metadata["visual_status"] = "ok"
        return replace(base, objects=fused, metadata=metadata)

    async def activate(
        self,
        observation: ObservationFrame,
        object_id: str,
        *,
        provenance: Provenance = Provenance.AGENT,
        explicit_authorization: bool = False,
    ) -> None:
        obj = self._object(observation, object_id)
        self._authorize(
            ActionKind.POINTER,
            destination_url=observation.metadata.get("url"),
            provenance=provenance,
            explicit_authorization=explicit_authorization,
        )

        if (
            PerceptionChannel.DOM in obj.channels
            and self.engine.capabilities.semantic_click
            and object_id.startswith("e")
        ):
            await self.engine.click_element(observation.tab, object_id)
            return

        point = self._visible_center(obj.rect, observation)
        await self.engine.pointer_click(
            observation.tab,
            self.coordinate_frame(observation),
            point,
            MouseButton.LEFT,
            1,
        )

    async def focus(
        self,
        observation: ObservationFrame,
        object_id: str,
        *,
        provenance: Provenance = Provenance.AGENT,
        explicit_authorization: bool = False,
    ) -> None:
        obj = self._object(observation, object_id)
        self._authorize(
            ActionKind.POINTER,
            destination_url=observation.metadata.get("url"),
            provenance=provenance,
            explicit_authorization=explicit_authorization,
        )

        if (
            PerceptionChannel.DOM in obj.channels
            and self.engine.capabilities.semantic_focus
            and object_id.startswith("e")
        ):
            await self.engine.focus_element(observation.tab, object_id)
            return

        point = self._visible_center(obj.rect, observation)
        await self.engine.pointer_click(
            observation.tab,
            self.coordinate_frame(observation),
            point,
            MouseButton.LEFT,
            1,
        )

    async def fill(
        self,
        observation: ObservationFrame,
        object_id: str,
        value: str,
        *,
        sensitive: bool = False,
        provenance: Provenance = Provenance.AGENT,
        explicit_authorization: bool = False,
    ) -> None:
        obj = self._object(observation, object_id)
        self._authorize(
            ActionKind.SENSITIVE_INPUT if sensitive else ActionKind.KEYBOARD,
            destination_url=observation.metadata.get("url"),
            provenance=provenance,
            explicit_authorization=explicit_authorization,
        )

        if (
            PerceptionChannel.DOM in obj.channels
            and self.engine.capabilities.semantic_fill
            and object_id.startswith("e")
        ):
            await self.engine.fill_element(observation.tab, object_id, value)
            return

        await self.focus(
            observation,
            object_id,
            provenance=provenance,
            explicit_authorization=explicit_authorization,
        )
        await self.engine.type_text(observation.tab, value)

    async def type_text(
        self,
        tab: TabRef,
        text: str,
        *,
        destination_url: str | None = None,
        sensitive: bool = False,
        provenance: Provenance = Provenance.AGENT,
        explicit_authorization: bool = False,
    ) -> None:
        self._authorize(
            ActionKind.SENSITIVE_INPUT if sensitive else ActionKind.KEYBOARD,
            destination_url=destination_url,
            provenance=provenance,
            explicit_authorization=explicit_authorization,
        )
        await self.engine.type_text(tab, text)

    async def key_press(
        self,
        tab: TabRef,
        key: str,
        *,
        destination_url: str | None = None,
        provenance: Provenance = Provenance.AGENT,
        explicit_authorization: bool = False,
    ) -> None:
        self._authorize(
            ActionKind.KEYBOARD,
            destination_url=destination_url,
            provenance=provenance,
            explicit_authorization=explicit_authorization,
        )
        await self.engine.key_press(tab, key)

    @staticmethod
    def coordinate_frame(observation: ObservationFrame) -> CoordinateFrame:
        return CoordinateFrame(
            session_id=observation.tab.session_id,
            tab_id=observation.tab.tab_id,
            generation=observation.generation,
            viewport_width=observation.viewport.width,
            viewport_height=observation.viewport.height,
            device_scale_factor=observation.viewport.device_scale_factor,
        )

    def _authorize(
        self,
        kind: ActionKind,
        *,
        destination_url: str | None,
        provenance: Provenance,
        explicit_authorization: bool,
    ) -> None:
        decision = self.policy.decide(
            ActionContext(
                kind=kind,
                destination_url=destination_url,
                provenance=provenance,
                explicit_authorization=explicit_authorization,
            )
        )
        if decision is Decision.ALLOW:
            return
        raise NavigatorPolicyDenied(f"policy decision: {decision.value}")

    @staticmethod
    def _object(observation: ObservationFrame, object_id: str) -> SurfaceObject:
        obj = observation.get(object_id)
        if obj is None:
            raise SurfaceTargetUnavailable(f"surface object not found: {object_id}")
        if not obj.actionable:
            raise SurfaceTargetUnavailable(f"surface object is not actionable: {object_id}")
        return obj

    @staticmethod
    def _visible_center(rect: Rect | None, observation: ObservationFrame) -> Point:
        if rect is None:
            raise SurfaceTargetUnavailable("surface object has no actionable geometry")

        left = max(0.0, rect.x)
        top = max(0.0, rect.y)
        right = min(float(observation.viewport.width), rect.x + rect.width)
        bottom = min(float(observation.viewport.height), rect.y + rect.height)
        if right <= left or bottom <= top:
            raise SurfaceTargetUnavailable("surface object is outside the current viewport")

        return Point((left + right) / 2.0, (top + bottom) / 2.0)
