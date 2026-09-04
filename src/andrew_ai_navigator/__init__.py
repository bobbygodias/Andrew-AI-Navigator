"""Andrew AI Navigator core contracts.

The core is intentionally provider-agnostic: AI platforms are clients,
not dependencies.
"""

from .engine import BrowserEngine, EngineCapabilities
from .input import Key, MouseButton, Point
from .models import Observation, Provenance, TabRef
from .perception import (
    ObservationFrame,
    PerceptionChannel,
    Rect,
    SurfaceEvidence,
    SurfaceObject,
)
from .policy import ActionContext, Decision, PolicyEngine
from .visual import VisualFrame, VisualPerceptor

__all__ = [
    "ActionContext",
    "BrowserEngine",
    "Decision",
    "EngineCapabilities",
    "Key",
    "MouseButton",
    "Observation",
    "ObservationFrame",
    "PerceptionChannel",
    "Point",
    "PolicyEngine",
    "Provenance",
    "Rect",
    "SurfaceEvidence",
    "SurfaceObject",
    "TabRef",
    "VisualFrame",
    "VisualPerceptor",
]

__version__ = "0.2.0a0"
