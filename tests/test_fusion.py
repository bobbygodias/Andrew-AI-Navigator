from andrew_ai_navigator.fusion import fuse_surface_objects, overlap_score
from andrew_ai_navigator.perception import (
    PerceptionChannel,
    Rect,
    SurfaceEvidence,
    SurfaceObject,
)


def test_overlap_score_handles_nested_visual_text_box() -> None:
    button = Rect(100, 100, 200, 80)
    label = Rect(150, 120, 100, 30)
    assert overlap_score(button, label) == 1.0


def test_visual_evidence_fuses_into_structural_target() -> None:
    structural = SurfaceObject(
        id="e1",
        generation=4,
        evidence=(SurfaceEvidence(PerceptionChannel.DOM, "role", "button"),),
        rect=Rect(100, 100, 200, 80),
        actionable=True,
    )
    visual = SurfaceObject(
        id="temporary",
        generation=4,
        evidence=(SurfaceEvidence(PerceptionChannel.PIXELS, "text", "Continue", 0.95),),
        rect=Rect(150, 120, 100, 30),
    )

    result = fuse_surface_objects((structural,), (visual,), generation=4)

    assert len(result) == 1
    assert result[0].id == "e1"
    assert result[0].channels == frozenset(
        {PerceptionChannel.DOM, PerceptionChannel.PIXELS}
    )


def test_visual_only_object_survives_without_dom_match() -> None:
    visual = SurfaceObject(
        id="whatever",
        generation=2,
        evidence=(SurfaceEvidence(PerceptionChannel.PIXELS, "visual_control", "canvas knob"),),
        rect=Rect(500, 300, 40, 40),
        actionable=True,
    )

    result = fuse_surface_objects((), (visual,), generation=2)

    assert len(result) == 1
    assert result[0].id == "v1"
    assert result[0].actionable is True
