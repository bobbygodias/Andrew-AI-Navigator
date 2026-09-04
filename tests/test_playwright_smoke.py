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
