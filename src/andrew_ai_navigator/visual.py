from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol, Sequence, runtime_checkable

from .models import TabRef, Viewport
from .perception import SurfaceObject


@dataclass(frozen=True, slots=True)
class VisualFrame:
    """Raw rendered pixels plus the coordinate frame they belong to."""

    tab: TabRef
    generation: int
    viewport: Viewport
    image_bytes: bytes
    media_type: str = "image/png"

    def __post_init__(self) -> None:
        if self.generation < 0:
            raise ValueError("generation cannot be negative")
        if not self.image_bytes:
            raise ValueError("visual frame cannot be empty")


@runtime_checkable
class VisualPerceptor(Protocol):
    """Provider-independent contract for understanding rendered pixels.

    Implementations may use classical computer vision, OCR, local multimodal
    models, remote models, or hybrids. The Navigator Core depends only on this
    contract and must not require any specific AI vendor.
    """

    @property
    def name(self) -> str: ...

    async def perceive(self, frame: VisualFrame) -> Sequence[SurfaceObject]: ...
