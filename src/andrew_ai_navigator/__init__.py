"""Andrew AI Navigator core contracts.

The core is intentionally provider-agnostic: AI platforms are clients,
not dependencies.
"""

from .engine import BrowserEngine, EngineCapabilities
from .input import Key, MouseButton, Point
from .models import Observation, Provenance, TabRef
from .policy import ActionContext, Decision, PolicyEngine

__all__ = [
    "ActionContext",
    "BrowserEngine",
    "Decision",
    "EngineCapabilities",
    "Key",
    "MouseButton",
    "Observation",
    "Point",
    "PolicyEngine",
    "Provenance",
    "TabRef",
]

__version__ = "0.2.0a0"
