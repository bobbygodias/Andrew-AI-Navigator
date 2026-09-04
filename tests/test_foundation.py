import pytest

from andrew_ai_navigator.engine import EngineCapabilities
from andrew_ai_navigator.input import CoordinateFrame, Point
from andrew_ai_navigator.models import Provenance
from andrew_ai_navigator.policy import ActionContext, ActionKind, Decision, PolicyEngine
from andrew_ai_navigator.security import UnsafeTarget, resolve_public_http_target


def test_coordinate_frame_rejects_invalid_geometry():
    with pytest.raises(ValueError):
        CoordinateFrame("s1", "t1", 0, 0, 800)


def test_coordinate_frame_contains_points():
    frame = CoordinateFrame("s1", "t1", 4, 1280, 720)
    assert frame.contains(Point(0, 0))
    assert frame.contains(Point(1279, 719))
    assert not frame.contains(Point(1280, 720))


def test_interactive_browser_requires_pointer_and_keyboard():
    full = EngineCapabilities(
        pointer_move=True,
        pointer_click=True,
        pointer_wheel=True,
        keyboard_keys=True,
        keyboard_text=True,
    )
    dom_only = EngineCapabilities(semantic_click=True, semantic_fill=True)
    assert full.interactive_browser
    assert not dom_only.interactive_browser


def test_web_content_cannot_authorize_sensitive_input():
    policy = PolicyEngine()
    decision = policy.decide(
        ActionContext(
            kind=ActionKind.SENSITIVE_INPUT,
            destination_url="https://example.com/login",
            provenance=Provenance.WEB_UNTRUSTED,
            explicit_authorization=True,
        )
    )
    assert decision is Decision.DENY


def test_sensitive_input_requires_explicit_authorization():
    policy = PolicyEngine()
    context = ActionContext(
        kind=ActionKind.SENSITIVE_INPUT,
        destination_url="https://example.com/login",
        provenance=Provenance.OPERATOR,
    )
    assert policy.decide(context) is Decision.REQUIRE_EXPLICIT_AUTHORIZATION


def test_non_http_scheme_is_denied_as_navigation_target():
    policy = PolicyEngine()
    context = ActionContext(
        kind=ActionKind.NAVIGATE,
        destination_url="about:blank",
        provenance=Provenance.AGENT,
    )
    assert policy.decide(context) is Decision.DENY


def test_existing_about_blank_surface_can_receive_keyboard_input():
    policy = PolicyEngine()
    context = ActionContext(
        kind=ActionKind.KEYBOARD,
        destination_url="about:blank",
        provenance=Provenance.AGENT,
    )
    assert policy.decide(context) is Decision.ALLOW


def test_existing_data_surface_can_receive_pointer_input():
    policy = PolicyEngine()
    context = ActionContext(
        kind=ActionKind.POINTER,
        destination_url="data:text/html,hello",
        provenance=Provenance.AGENT,
    )
    assert policy.decide(context) is Decision.ALLOW


@pytest.mark.parametrize(
    "url",
    [
        "file:///etc/passwd",
        "http://127.0.0.1/",
        "http://10.0.0.1/",
        "http://169.254.169.254/",
        "http://[::1]/",
    ],
)
def test_rejects_non_web_or_protected_targets(url):
    with pytest.raises(UnsafeTarget):
        resolve_public_http_target(url)
