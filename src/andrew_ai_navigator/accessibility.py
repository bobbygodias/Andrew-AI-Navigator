from __future__ import annotations

import re
from typing import Sequence

from .perception import Rect


_BOX_RE = re.compile(
    r"\[box=(-?\d+(?:\.\d+)?),(-?\d+(?:\.\d+)?),"
    r"(-?\d+(?:\.\d+)?),(-?\d+(?:\.\d+)?)\]"
)


def _indent_width(line: str) -> int:
    return len(line) - len(line.lstrip(" "))


def _same_box(a: Rect, b: Rect, tolerance: float) -> bool:
    return (
        abs(a.x - b.x) <= tolerance
        and abs(a.y - b.y) <= tolerance
        and abs(a.width - b.width) <= tolerance
        and abs(a.height - b.height) <= tolerance
    )


def redact_sensitive_accessibility_snapshot(
    snapshot: str,
    sensitive_rects: Sequence[Rect],
    *,
    tolerance: float = 1.5,
) -> str:
    """Collapse accessibility nodes whose rendered boxes are sensitive.

    This deliberately uses geometry rather than reading the field's value in
    order to learn what must be removed. Playwright ARIA snapshots may include
    textbox values; a password/OTP control is therefore correlated with the
    DOM/geometry channel and replaced as a whole.

    Child lines indented beneath a matched sensitive node are discarded until
    the snapshot returns to the same or a shallower indentation level.
    """

    if tolerance < 0:
        raise ValueError("tolerance cannot be negative")
    if not snapshot or not sensitive_rects:
        return snapshot

    output: list[str] = []
    suppress_children_of_indent: int | None = None

    for line in snapshot.splitlines():
        indent = _indent_width(line)

        if suppress_children_of_indent is not None:
            if indent > suppress_children_of_indent:
                continue
            suppress_children_of_indent = None

        match = _BOX_RE.search(line)
        if match is None:
            output.append(line)
            continue

        box = Rect(*(float(value) for value in match.groups()))
        if not any(_same_box(box, sensitive, tolerance) for sensitive in sensitive_rects):
            output.append(line)
            continue

        indentation = line[:indent]
        output.append(
            f"{indentation}- sensitive-control {match.group(0)}: [REDACTED]"
        )
        suppress_children_of_indent = indent

    return "\n".join(output)
