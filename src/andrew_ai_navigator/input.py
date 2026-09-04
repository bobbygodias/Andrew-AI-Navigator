from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum


class MouseButton(StrEnum):
    LEFT = "left"
    MIDDLE = "middle"
    RIGHT = "right"


class Key(StrEnum):
    ENTER = "Enter"
    TAB = "Tab"
    ESCAPE = "Escape"
    BACKSPACE = "Backspace"
    DELETE = "Delete"
    HOME = "Home"
    END = "End"
    PAGE_UP = "PageUp"
    PAGE_DOWN = "PageDown"
    ARROW_UP = "ArrowUp"
    ARROW_DOWN = "ArrowDown"
    ARROW_LEFT = "ArrowLeft"
    ARROW_RIGHT = "ArrowRight"
    CONTROL = "Control"
    ALT = "Alt"
    SHIFT = "Shift"
    META = "Meta"


@dataclass(frozen=True, slots=True)
class Point:
    x: float
    y: float


@dataclass(frozen=True, slots=True)
class CoordinateFrame:
    """Binds coordinates to the observation that made them meaningful."""

    session_id: str
    tab_id: str
    generation: int
    viewport_width: int
    viewport_height: int
    device_scale_factor: float = 1.0

    def __post_init__(self) -> None:
        if self.generation < 0:
            raise ValueError("generation cannot be negative")
        if self.viewport_width <= 0 or self.viewport_height <= 0:
            raise ValueError("viewport dimensions must be positive")
        if self.device_scale_factor <= 0:
            raise ValueError("device_scale_factor must be positive")

    def contains(self, point: Point) -> bool:
        return 0 <= point.x < self.viewport_width and 0 <= point.y < self.viewport_height
