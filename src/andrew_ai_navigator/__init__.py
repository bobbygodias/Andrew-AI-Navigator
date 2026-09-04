"""Andrew AI Navigator core contracts.

The core is intentionally provider-agnostic: AI platforms are clients,
not dependencies.
"""

from .engine import BrowserEngine, EngineCapabilities
from .fusion import fuse_surface_objects, overlap_score
from .input import Key, MouseButton, Point
from .models import Observation, Provenance, TabRef
from .navigator import Navigator, NavigatorPolicyDenied, SurfaceTargetUnavailable
from .perception import (
    ObservationFrame,
    PerceptionChannel,
    Rect,
    SurfaceEvidence,
    SurfaceObject,
)
from .policy import ActionContext, ActionKind, Decision, PolicyEngine
from .visual import VisualFrame, VisualPerceptor

__all__ = [
    "ActionContext",
    "ActionKind",
    "BrowserEngine",
    "Decision",
    "EngineCapabilities",
    "Key",
    "MouseButton",
    "Navigator",
    "NavigatorPolicyDenied",
    "Observation",
    "ObservationFrame",
    "PerceptionChannel",
    "Point",
    "PolicyEngine",
    "Provenance",
    "Rect",
    "SurfaceEvidence",
    "SurfaceObject",
    "SurfaceTargetUnavailable",
    "TabRef",
    "VisualFrame",
    "VisualPerceptor",
    "fuse_surface_objects",
    "overlap_score",
]

__version__ = "0.2.0a0"
