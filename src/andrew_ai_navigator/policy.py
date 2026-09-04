from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from urllib.parse import urlsplit

from .models import Provenance


class Decision(StrEnum):
    ALLOW = "allow"
    DENY = "deny"
    REQUIRE_EXPLICIT_AUTHORIZATION = "require_explicit_authorization"


class ActionKind(StrEnum):
    READ = "read"
    NAVIGATE = "navigate"
    POINTER = "pointer"
    KEYBOARD = "keyboard"
    FORM_SUBMIT = "form_submit"
    SENSITIVE_INPUT = "sensitive_input"
    HOST_IO = "host_io"


@dataclass(frozen=True, slots=True)
class ActionContext:
    kind: ActionKind
    destination_url: str | None
    provenance: Provenance
    explicit_authorization: bool = False


class PolicyEngine:
    """Small default policy foundation.

    Navigation policy and surface-interaction policy are deliberately separate.
    A URL scheme may be forbidden as a navigation target without making an
    already-rendered browser surface incapable of receiving pointer/keyboard
    input.
    """

    def decide(self, context: ActionContext) -> Decision:
        if context.provenance is Provenance.WEB_UNTRUSTED and context.kind in {
            ActionKind.HOST_IO,
            ActionKind.SENSITIVE_INPUT,
        }:
            return Decision.DENY

        if context.kind is ActionKind.HOST_IO:
            return (
                Decision.ALLOW
                if context.explicit_authorization
                else Decision.REQUIRE_EXPLICIT_AUTHORIZATION
            )

        if context.kind in {ActionKind.FORM_SUBMIT, ActionKind.SENSITIVE_INPUT}:
            return (
                Decision.ALLOW
                if context.explicit_authorization
                else Decision.REQUIRE_EXPLICIT_AUTHORIZATION
            )

        # Scheme restrictions govern creation of a network/navigation target.
        # They do not redefine whether an already-rendered surface can receive
        # mouse or keyboard input. about:blank/data/browser-created documents
        # may legitimately exist inside a session without being legal remote
        # navigation destinations.
        if context.kind is ActionKind.NAVIGATE and context.destination_url:
            scheme = urlsplit(context.destination_url).scheme.lower()
            if scheme not in {"http", "https"}:
                return Decision.DENY

        return Decision.ALLOW
