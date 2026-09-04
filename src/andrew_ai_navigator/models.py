from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum
from typing import Mapping, Sequence


class Provenance(StrEnum):
    OPERATOR = "operator"
    AGENT = "agent"
    CLIENT = "client"
    WEB_UNTRUSTED = "web_untrusted"
    LOCAL_CONFIG = "local_config"


@dataclass(frozen=True, slots=True)
class TabRef:
    session_id: str
    tab_id: str


@dataclass(frozen=True, slots=True)
class ElementRef:
    id: str
    role: str | None = None
    name: str | None = None


@dataclass(frozen=True, slots=True)
class Viewport:
    width: int
    height: int
    device_scale_factor: float = 1.0
    scroll_x: float = 0.0
    scroll_y: float = 0.0

    def __post_init__(self) -> None:
        if self.width <= 0 or self.height <= 0:
            raise ValueError("viewport dimensions must be positive")
        if self.device_scale_factor <= 0:
            raise ValueError("device_scale_factor must be positive")


@dataclass(frozen=True, slots=True)
class Observation:
    tab: TabRef
    generation: int
    url: str
    title: str
    viewport: Viewport
    text: str = ""
    elements: Sequence[ElementRef] = field(default_factory=tuple)
    metadata: Mapping[str, str] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if self.generation < 0:
            raise ValueError("generation cannot be negative")
