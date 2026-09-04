from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum
from typing import Mapping, Sequence

from .models import TabRef, Viewport


class PerceptionChannel(StrEnum):
    """Independent evidence channels describing one rendered browser surface."""

    DOM = "dom"
    ACCESSIBILITY = "accessibility"
    GEOMETRY = "geometry"
    PIXELS = "pixels"
    FRAME = "frame"
    NAVIGATION = "navigation"
    LANGUAGE = "language"
    NETWORK_METADATA = "network_metadata"
    BROWSER_STATE = "browser_state"


@dataclass(frozen=True, slots=True)
class Rect:
    x: float
    y: float
    width: float
    height: float

    def __post_init__(self) -> None:
        if self.width < 0 or self.height < 0:
            raise ValueError("rect dimensions cannot be negative")

    @property
    def center(self) -> tuple[float, float]:
        return (self.x + self.width / 2.0, self.y + self.height / 2.0)

    def contains(self, x: float, y: float) -> bool:
        return self.x <= x <= self.x + self.width and self.y <= y <= self.y + self.height


@dataclass(frozen=True, slots=True)
class SurfaceEvidence:
    """One piece of evidence about a perceived surface object.

    Evidence is intentionally channel-labelled so clients can distinguish, for
    example, DOM text from text recognized visually on a rendered canvas.
    """

    channel: PerceptionChannel
    kind: str
    value: str
    confidence: float = 1.0
    metadata: Mapping[str, str] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.kind:
            raise ValueError("evidence kind cannot be empty")
        if not 0.0 <= self.confidence <= 1.0:
            raise ValueError("confidence must be between 0 and 1")


@dataclass(frozen=True, slots=True)
class SurfaceObject:
    """An ephemeral object perceived on one observation generation."""

    id: str
    generation: int
    evidence: Sequence[SurfaceEvidence]
    rect: Rect | None = None
    frame_id: str | None = None
    actionable: bool = False
    occluded: bool = False
    metadata: Mapping[str, str] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.id:
            raise ValueError("surface object id cannot be empty")
        if self.generation < 0:
            raise ValueError("generation cannot be negative")
        if not self.evidence:
            raise ValueError("surface object requires at least one evidence item")

    @property
    def channels(self) -> frozenset[PerceptionChannel]:
        return frozenset(item.channel for item in self.evidence)

    def evidence_from(self, channel: PerceptionChannel) -> tuple[SurfaceEvidence, ...]:
        return tuple(item for item in self.evidence if item.channel is channel)


@dataclass(frozen=True, slots=True)
class ObservationFrame:
    """Immutable multi-channel perception frame for one tab generation.

    `objects` stores normalized actionable/perceived objects. `channel_payloads`
    retains useful raw channel representations that should not be flattened
    prematurely, such as an accessibility snapshot.
    """

    tab: TabRef
    generation: int
    viewport: Viewport
    objects: Sequence[SurfaceObject] = field(default_factory=tuple)
    screenshot_ref: str | None = None
    channel_payloads: Mapping[PerceptionChannel, str] = field(default_factory=dict)
    metadata: Mapping[str, str] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if self.generation < 0:
            raise ValueError("generation cannot be negative")
        for obj in self.objects:
            if obj.generation != self.generation:
                raise ValueError("surface object generation must match observation frame")

    def get(self, object_id: str) -> SurfaceObject | None:
        for obj in self.objects:
            if obj.id == object_id:
                return obj
        return None

    @property
    def channels(self) -> frozenset[PerceptionChannel]:
        object_channels = {channel for obj in self.objects for channel in obj.channels}
        return frozenset((*object_channels, *self.channel_payloads.keys()))
