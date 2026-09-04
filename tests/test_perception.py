from andrew_ai_navigator.models import TabRef, Viewport
from andrew_ai_navigator.perception import (
    ObservationFrame,
    PerceptionChannel,
    Rect,
    SurfaceEvidence,
    SurfaceObject,
)


def test_pixel_only_control_is_valid_surface_object() -> None:
    obj = SurfaceObject(
        id="e1",
        generation=3,
        evidence=(
            SurfaceEvidence(
                channel=PerceptionChannel.PIXELS,
                kind="visual_control",
                value="Continue",
                confidence=0.93,
            ),
        ),
        rect=Rect(100, 200, 120, 40),
        actionable=True,
    )

    assert obj.actionable is True
    assert obj.channels == frozenset({PerceptionChannel.PIXELS})


def test_fused_object_preserves_all_evidence_channels() -> None:
    obj = SurfaceObject(
        id="e2",
        generation=1,
        evidence=(
            SurfaceEvidence(PerceptionChannel.DOM, "role", "button"),
            SurfaceEvidence(PerceptionChannel.ACCESSIBILITY, "name", "Continue"),
            SurfaceEvidence(PerceptionChannel.PIXELS, "visible_text", "Continue", 0.98),
            SurfaceEvidence(PerceptionChannel.GEOMETRY, "hit_test", "visible"),
        ),
        rect=Rect(10, 20, 80, 30),
        actionable=True,
    )

    assert obj.channels == frozenset(
        {
            PerceptionChannel.DOM,
            PerceptionChannel.ACCESSIBILITY,
            PerceptionChannel.PIXELS,
            PerceptionChannel.GEOMETRY,
        }
    )
    assert len(obj.evidence_from(PerceptionChannel.PIXELS)) == 1


def test_observation_frame_rejects_stale_generation_objects() -> None:
    obj = SurfaceObject(
        id="e3",
        generation=1,
        evidence=(SurfaceEvidence(PerceptionChannel.DOM, "role", "link"),),
    )

    try:
        ObservationFrame(
            tab=TabRef(session_id="s1", tab_id="t1"),
            generation=2,
            viewport=Viewport(1280, 720),
            objects=(obj,),
        )
    except ValueError as exc:
        assert "generation" in str(exc)
    else:
        raise AssertionError("expected mismatched generation to be rejected")


def test_rect_geometry_can_drive_pointer_targeting() -> None:
    rect = Rect(100, 50, 200, 100)
    assert rect.center == (200.0, 100.0)
    assert rect.contains(200, 100)
    assert not rect.contains(99, 100)
