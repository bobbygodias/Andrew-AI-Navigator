from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol, Sequence, runtime_checkable

from .input import CoordinateFrame, MouseButton, Point
from .models import Observation, TabRef
from .perception import ObservationFrame


@dataclass(frozen=True, slots=True)
class EngineCapabilities:
    semantic_click: bool = False
    semantic_fill: bool = False
    semantic_select: bool = False
    semantic_focus: bool = False
    pointer_move: bool = False
    pointer_click: bool = False
    pointer_drag: bool = False
    pointer_wheel: bool = False
    keyboard_keys: bool = False
    keyboard_text: bool = False
    screenshots: bool = False
    dom_observation: bool = False
    accessibility_observation: bool = False
    geometry_observation: bool = False
    frame_observation: bool = False
    browser_state_observation: bool = False
    javascript: bool = False
    cookies_storage: bool = False
    tls_validation: bool = True
    host_io: bool = False

    @property
    def interactive_browser(self) -> bool:
        return (
            self.pointer_move
            and self.pointer_click
            and self.pointer_wheel
            and self.keyboard_keys
            and self.keyboard_text
        )

    @property
    def surface_observer(self) -> bool:
        return self.screenshots and self.geometry_observation

    @property
    def real_web_runtime(self) -> bool:
        return self.javascript and self.cookies_storage and self.tls_validation


@runtime_checkable
class BrowserEngine(Protocol):
    @property
    def capabilities(self) -> EngineCapabilities: ...

    async def start(self) -> None: ...
    async def stop(self) -> None: ...

    async def new_tab(self, session_id: str) -> TabRef: ...
    async def list_tabs(self, session_id: str) -> Sequence[TabRef]: ...
    async def close_tab(self, tab: TabRef) -> None: ...
    async def navigate(self, tab: TabRef, url: str) -> None: ...

    # Compact semantic observation retained for simple clients.
    async def observe(self, tab: TabRef) -> Observation: ...

    # Multi-channel surface observation used by the general Navigator core.
    async def observe_surface(self, tab: TabRef) -> ObservationFrame: ...

    # Pixels for one exact observation generation.
    async def surface_png(self, tab: TabRef, generation: int) -> bytes: ...

    async def click_element(self, tab: TabRef, element_id: str) -> None: ...
    async def fill_element(self, tab: TabRef, element_id: str, value: str) -> None: ...
    async def focus_element(self, tab: TabRef, element_id: str) -> None: ...
    async def select_element(self, tab: TabRef, element_id: str, value: str) -> None: ...

    async def pointer_move(self, tab: TabRef, frame: CoordinateFrame, point: Point) -> None: ...
    async def pointer_click(
        self,
        tab: TabRef,
        frame: CoordinateFrame,
        point: Point,
        button: MouseButton = MouseButton.LEFT,
        click_count: int = 1,
    ) -> None: ...
    async def pointer_down(self, tab: TabRef, button: MouseButton = MouseButton.LEFT) -> None: ...
    async def pointer_up(self, tab: TabRef, button: MouseButton = MouseButton.LEFT) -> None: ...
    async def pointer_wheel(self, tab: TabRef, delta_x: float, delta_y: float) -> None: ...
    async def pointer_drag(
        self,
        tab: TabRef,
        frame: CoordinateFrame,
        start: Point,
        end: Point,
    ) -> None: ...

    async def key_down(self, tab: TabRef, key: str) -> None: ...
    async def key_up(self, tab: TabRef, key: str) -> None: ...
    async def key_press(self, tab: TabRef, key: str) -> None: ...
    async def key_chord(self, tab: TabRef, keys: Sequence[str]) -> None: ...
    async def type_text(self, tab: TabRef, text: str) -> None: ...

    async def screenshot(self, tab: TabRef) -> bytes: ...
