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

@pytest.mark.asyncio
async def test_failed_navigation_invalidates_previous_targets(monkeypatch):
    from types import SimpleNamespace
    from unittest.mock import AsyncMock
    import andrew_ai_navigator.engines.playwright as module
    engine = PlaywrightEngine(identity="testing")
    page = SimpleNamespace(goto=AsyncMock(side_effect=TimeoutError("navigation timed out")))
    monkeypatch.setattr(engine, "_get_page", lambda tab: page)
    monkeypatch.setattr(module, "resolve_public_http_target", lambda url: None)
    engine._generation["t"] = 4
    engine._targets["t"] = {"old": object()}
    engine._screenshots["t"] = (4, b"old")
    with pytest.raises(TimeoutError):
        await engine.navigate(SimpleNamespace(tab_id="t"), "https://example.com")
    assert engine._generation["t"] > 4
    assert not engine._targets["t"]
    assert "t" not in engine._screenshots


@pytest.mark.asyncio
async def test_malformed_route_aborts(monkeypatch):
    from types import SimpleNamespace
    from unittest.mock import AsyncMock
    route = SimpleNamespace(request=SimpleNamespace(url="http://[broken"),
                            abort=AsyncMock(), continue_=AsyncMock())
    await PlaywrightEngine(identity="testing")._route_guard(route)
    route.abort.assert_awaited_once_with("blockedbyclient")
    route.continue_.assert_not_awaited()
