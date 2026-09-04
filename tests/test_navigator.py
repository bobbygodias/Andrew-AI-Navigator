from __future__ import annotations

from dataclasses import dataclass

from andrew_ai_navigator.engine import EngineCapabilities
from andrew_ai_navigator.models import TabRef, Viewport
from andrew_ai_navigator.navigator import Navigator
from andrew_ai_navigator.perception import (
    ObservationFrame,
    PerceptionChannel,
    Rect,
    SurfaceEvidence,
    SurfaceObject,
)
from andrew_ai_navigator.visual import VisualFrame


class FakeEngine:
    capabilities = EngineCapabilities(
        semantic_click=True,
        semantic_focus=True,
        semantic_fill=True,
        pointer_move=True,
        pointer_click=True,
        pointer_wheel=True,
        keyboard_keys=True,
        keyboard_text=True,
        screenshots=True,
        geometry_observation=True,
    )

    def __init__(self, base_objects=()):
        self.tab = TabRef("s1", "t1")
        self.base_objects = tuple(base_objects)
        self.semantic_clicks: list[str] = []
        self.pointer_clicks: list[tuple[float, float]] = []

    async def start(self):
        pass

    async def stop(self):
        pass

    async def new_tab(self, session_id):
        return self.tab

    async def list_tabs(self, session_id):
        return (self.tab,)

    async def close_tab(self, tab):
        pass

    async def navigate(self, tab, url):
        pass

    async def observe_surface(self, tab):
        return ObservationFrame(
            tab=self.tab,
            generation=1,
            viewport=Viewport(800, 600),
            objects=self.base_objects,
            screenshot_ref="memory://surface.png",
            metadata={"url": "https://example.com"},
        )

    async def surface_png(self, tab, generation):
        return b"png"

    async def click_element(self, tab, element_id):
        self.semantic_clicks.append(element_id)

    async def pointer_click(self, tab, frame, point, button, click_count):
        self.pointer_clicks.append((point.x, point.y))

    async def focus_element(self, tab, element_id):
        pass

    async def fill_element(self, tab, element_id, value):
        pass

    async def type_text(self, tab, text):
        pass

    async def key_press(self, tab, key):
        pass


@dataclass
class FakeVisualPerceptor:
    name: str = "fake-vision"

    async def perceive(self, frame: VisualFrame):
        return (
            SurfaceObject(
                id="raw-visual-id",
                generation=frame.generation,
                evidence=(
                    SurfaceEvidence(
                        PerceptionChannel.PIXELS,
                        "visual_control",
                        "canvas control",
                    ),
                ),
                rect=Rect(100, 200, 80, 40),
                actionable=True,
            ),
        )


async def test_visual_only_surface_object_is_clickable_by_geometry():
    engine = FakeEngine()
    navigator = Navigator(engine, visual_perceptor=FakeVisualPerceptor())

    observation = await navigator.observe_surface(engine.tab)
    assert observation.get("v1") is not None

    await navigator.activate(observation, "v1")
    assert engine.pointer_clicks == [(140.0, 220.0)]
    assert engine.semantic_clicks == []


async def test_dom_surface_object_prefers_semantic_click():
    dom = SurfaceObject(
        id="e1",
        generation=1,
        evidence=(SurfaceEvidence(PerceptionChannel.DOM, "role", "button"),),
        rect=Rect(10, 20, 100, 40),
        actionable=True,
    )
    engine = FakeEngine((dom,))
    navigator = Navigator(engine)

    observation = await navigator.observe_surface(engine.tab)
    await navigator.activate(observation, "e1")

    assert engine.semantic_clicks == ["e1"]
    assert engine.pointer_clicks == []
