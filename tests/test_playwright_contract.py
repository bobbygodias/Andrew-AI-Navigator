from pathlib import Path

import pytest

from andrew_ai_navigator.engines.playwright import PlaywrightEngine


def test_playwright_engine_import_does_not_require_playwright_package() -> None:
    engine = PlaywrightEngine(identity="testing", runtime_root=Path("/tmp/navigator-test"))
    assert engine.identity == "testing"
    assert engine.capabilities.interactive_browser is True
    assert engine.capabilities.surface_observer is True
    assert engine.capabilities.real_web_runtime is True
    assert engine.capabilities.accessibility_observation is True


def test_identity_name_is_path_safe() -> None:
    with pytest.raises(ValueError):
        PlaywrightEngine(identity="../../escape")
