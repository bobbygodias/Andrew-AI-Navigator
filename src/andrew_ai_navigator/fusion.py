from __future__ import annotations

from dataclasses import replace
from typing import Iterable, Sequence

from .perception import Rect, SurfaceEvidence, SurfaceObject


def _area(rect: Rect) -> float:
    return max(rect.width, 0.0) * max(rect.height, 0.0)


def overlap_score(a: Rect, b: Rect) -> float:
    """Return containment-friendly overlap in the range 0..1.

    Intersection-over-union is poor for a visual text box contained inside a
    much larger button. Dividing by the smaller area recognizes that both
    rectangles may describe the same surface object at different granularity.
    """

    left = max(a.x, b.x)
    top = max(a.y, b.y)
    right = min(a.x + a.width, b.x + b.width)
    bottom = min(a.y + a.height, b.y + b.height)
    if right <= left or bottom <= top:
        return 0.0

    intersection = (right - left) * (bottom - top)
    denominator = min(_area(a), _area(b))
    if denominator <= 0:
        return 0.0
    return max(0.0, min(1.0, intersection / denominator))


def _dedupe_evidence(items: Iterable[SurfaceEvidence]) -> tuple[SurfaceEvidence, ...]:
    result: list[SurfaceEvidence] = []
    seen: set[tuple[str, str, str]] = set()
    for item in items:
        key = (item.channel.value, item.kind, item.value)
        if key in seen:
            continue
        seen.add(key)
        result.append(item)
    return tuple(result)


def merge_surface_objects(primary: SurfaceObject, secondary: SurfaceObject) -> SurfaceObject:
    if primary.generation != secondary.generation:
        raise ValueError("cannot fuse objects from different generations")

    if primary.frame_id and secondary.frame_id and primary.frame_id != secondary.frame_id:
        raise ValueError("cannot fuse objects from different frames")

    metadata = dict(primary.metadata)
    for key, value in secondary.metadata.items():
        metadata.setdefault(key, value)

    return replace(
        primary,
        evidence=_dedupe_evidence((*primary.evidence, *secondary.evidence)),
        rect=primary.rect or secondary.rect,
        frame_id=primary.frame_id or secondary.frame_id,
        actionable=primary.actionable or secondary.actionable,
        occluded=primary.occluded or secondary.occluded,
        metadata=metadata,
    )


def fuse_surface_objects(
    structural: Sequence[SurfaceObject],
    visual: Sequence[SurfaceObject],
    *,
    generation: int,
    overlap_threshold: float = 0.55,
) -> tuple[SurfaceObject, ...]:
    """Fuse visual evidence into structural objects without erasing provenance.

    Structural IDs are preserved when a visual object is matched. Visual-only
    objects receive `vN` IDs so a missing DOM representation never makes them
    disappear from the surface model.
    """

    if not 0.0 <= overlap_threshold <= 1.0:
        raise ValueError("overlap_threshold must be between 0 and 1")

    fused = list(structural)
    for item in fused:
        if item.generation != generation:
            raise ValueError("structural object generation mismatch")

    visual_only_index = 0
    for incoming in visual:
        if incoming.generation != generation:
            raise ValueError("visual object generation mismatch")

        best_index: int | None = None
        best_score = 0.0
        if incoming.rect is not None:
            for index, existing in enumerate(fused):
                if existing.rect is None:
                    continue
                if existing.frame_id and incoming.frame_id and existing.frame_id != incoming.frame_id:
                    continue
                score = overlap_score(existing.rect, incoming.rect)
                if score > best_score:
                    best_index = index
                    best_score = score

        if best_index is not None and best_score >= overlap_threshold:
            fused[best_index] = merge_surface_objects(fused[best_index], incoming)
            continue

        visual_only_index += 1
        fused.append(replace(incoming, id=f"v{visual_only_index}"))

    return tuple(fused)
