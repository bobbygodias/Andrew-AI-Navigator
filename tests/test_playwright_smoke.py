from __future__ import annotations

import asyncio

import pytest

pytest.importorskip("playwright.async_api")

from andrew_ai_navigator.engines.playwright import PlaywrightEngine
from andrew_ai_navigator.navigator import Navigator


async def _smoke(tmp_path) -> None:
    engine = PlaywrightEngine(
        identity="ci-testing",
        runtime_root=tmp_path,
        headless=True,
        viewport_width=1000,
        viewport_height=700,
    )
    navigator = Navigator(engine)

    await navigator.start()
    try:
        tab = await navigator.new_tab("smoke-session")
        page = engine._get_page(tab)  # implementation-specific smoke harness
        await page.set_content(
            """
            <!doctype html>
            <html lang="pt-BR">
              <body>
                <form id="login" onsubmit="event.preventDefault(); document.getElementById('status').textContent='submitted'">
                  <label for="user">Usuário</label>
                  <input id="user" name="username" autocomplete="username">

                  <label for="pass">Senha</label>
                  <input id="pass" name="password" type="password" autocomplete="current-password">

                  <button type="submit">Entrar</button>
                  <p id="status"></p>
                </form>
              </body>
            </html>
            """
        )

        first = await navigator.observe_surface(tab)
        assert first.screenshot_ref
        assert await engine.surface_png(tab, first.generation)
        assert len(await navigator.list_tabs("smoke-session")) == 1

        username = next(
            obj for obj in first.objects
            if obj.metadata.get("autocomplete") == "username"
        )
        await navigator.fill(first, username.id, "andrew")
        assert await page.locator("#user").input_value() == "andrew"

        second = await navigator.observe_surface(tab)
        password = next(
            obj for obj in second.objects
            if obj.metadata.get("input_type") == "password"
        )
        secret = "navigator-smoke-secret"
        await navigator.fill(
            second,
            password.id,
            secret,
            sensitive=True,
            explicit_authorization=True,
        )
        assert await page.locator("#pass").input_value() == secret

        third = await navigator.observe_surface(tab)
        flattened_evidence = "\n".join(
            evidence.value
            for obj in third.objects
            for evidence in obj.evidence
        )
        flattened_channels = "\n".join(third.channel_payloads.values())
        assert secret not in flattened_evidence
        assert secret not in flattened_channels

        submit = next(
            obj for obj in third.objects
            if any(ev.kind == "name" and ev.value == "Entrar" for ev in obj.evidence)
        )
        await navigator.activate(third, submit.id)
        assert await page.locator("#status").inner_text() == "submitted"
    finally:
        await navigator.stop()


def test_real_chromium_login_like_surface_flow(tmp_path) -> None:
    asyncio.run(_smoke(tmp_path))


async def _cookie_persistence(tmp_path) -> None:
    identity = "persistent-cookie-test"

    first = PlaywrightEngine(identity=identity, runtime_root=tmp_path, headless=True)
    await first.start()
    try:
        assert first._context is not None
        await first._context.add_cookies(
            [
                {
                    "name": "navigator_persistence_probe",
                    "value": "survives-restart",
                    "url": "https://example.com/",
                    "expires": 2_000_000_000,
                    "httpOnly": True,
                    "secure": True,
                    "sameSite": "Lax",
                }
            ]
        )
    finally:
        await first.stop()

    second = PlaywrightEngine(identity=identity, runtime_root=tmp_path, headless=True)
    await second.start()
    try:
        assert second._context is not None
        cookies = await second._context.cookies("https://example.com/")
        probe = next(cookie for cookie in cookies if cookie["name"] == "navigator_persistence_probe")
        assert probe["value"] == "survives-restart"
        assert probe["httpOnly"] is True
        assert probe["secure"] is True
    finally:
        await second.stop()


def test_persistent_identity_retains_cookie_across_restart(tmp_path) -> None:
    asyncio.run(_cookie_persistence(tmp_path))


async def _disguised_sensitive_inputs_do_not_expose_aria(tmp_path) -> None:
    engine = PlaywrightEngine(
        identity="sensitive-aria-test",
        runtime_root=tmp_path,
        headless=True,
    )
    navigator = Navigator(engine)
    await navigator.start()
    try:
        tab = await navigator.new_tab("sensitive-aria")
        page = engine._get_page(tab)

        # Some sites implement a password field with type=text (for example,
        # when a visibility toggle changes the input type). Its semantic
        # name must still suppress the raw AI-oriented ARIA snapshot.
        await page.set_content(
            '<label for="credential">Password</label>'
            '<input id="credential" name="account_password" type="text" '
            'value="do-not-leak-password">'
        )
        frame = await navigator.observe_surface(tab)
        assert not any("accessibility" in str(key).lower() for key in frame.channel_payloads)

        # Verification codes can also use type=text without autocomplete.
        await page.set_content(
            '<input id="verification" name="login_otp" type="text" '
            'value="do-not-leak-otp">'
        )
        frame = await navigator.observe_surface(tab)
        assert not any("accessibility" in str(key).lower() for key in frame.channel_payloads)

        # Even a normal search field can contain private user-entered text.
        # The accessibility channel must be suppressed without returning its
        # value to Python.
        await page.set_content(
            '<input id="search" type="search" aria-label="Search" '
            'value="private-search-query">'
        )
        frame = await navigator.observe_surface(tab)
        assert not any("accessibility" in str(key).lower() for key in frame.channel_payloads)
        assert "private-search-query" not in "\\n".join(frame.channel_payloads.values())

        # Rich text editors are often contenteditable divs, not inputs.
        # Their typed content must not enter either DOM evidence or raw ARIA.
        await page.set_content(
            '<p>Public page information</p>'
            '<div role="textbox" contenteditable="true" aria-label="Notes">'
            'private-editor-draft</div>'
        )
        frame = await navigator.observe_surface(tab)
        assert not any("accessibility" in str(key).lower() for key in frame.channel_payloads)
        flattened_evidence = "\\n".join(
            evidence.value for obj in frame.objects for evidence in obj.evidence
        )
        assert "private-editor-draft" not in flattened_evidence
        compact = await engine.observe(tab)
        assert "private-editor-draft" not in compact.text
        assert "Public page information" in compact.text

        # Textareas can also hold user data with no password/OTP label.
        await page.set_content(
            '<textarea aria-label="Message">private-message-draft</textarea>'
        )
        frame = await navigator.observe_surface(tab)
        assert not any("accessibility" in str(key).lower() for key in frame.channel_payloads)

        # The protection must inspect embedded frames, not just the top DOM.
        await page.set_content(
            '<iframe srcdoc="&lt;input id=&quot;secret&quot; '
            'type=&quot;password&quot; value=&quot;iframe-secret&quot;&gt;"></iframe>'
        )
        await page.frame_locator("iframe").locator("#secret").wait_for()
        frame = await navigator.observe_surface(tab)
        assert not any("accessibility" in str(key).lower() for key in frame.channel_payloads)
    finally:
        await navigator.stop()


def test_disguised_sensitive_inputs_suppress_aria_snapshots(tmp_path) -> None:
    asyncio.run(_disguised_sensitive_inputs_do_not_expose_aria(tmp_path))
