from __future__ import annotations

import argparse
import json
from dataclasses import asdict
from pathlib import Path

from . import __version__
from .engines.playwright import PlaywrightEngine


def _default_runtime_root() -> Path:
    return Path.home() / ".local" / "share" / "andrew-ai-navigator"


def _capabilities_dict(engine: PlaywrightEngine) -> dict[str, object]:
    raw = asdict(engine.capabilities)
    raw["interactive_browser"] = engine.capabilities.interactive_browser
    raw["surface_observer"] = engine.capabilities.surface_observer
    raw["real_web_runtime"] = engine.capabilities.real_web_runtime
    return raw


def _doctor(args: argparse.Namespace) -> int:
    engine = PlaywrightEngine(
        identity=args.identity,
        runtime_root=args.runtime_root,
        headless=args.headless,
    )

    playwright_installed = True
    playwright_version: str | None = None
    try:
        from importlib.metadata import version

        playwright_version = version("playwright")
    except Exception:
        playwright_installed = False

    report = {
        "name": "Andrew AI Navigator",
        "version": __version__,
        "standalone": True,
        "constitutional_invariant": "AI platforms are clients, not dependencies.",
        "identity": engine.identity,
        "runtime_root": str(engine.runtime_root),
        "profile_dir": str(engine.profile_dir),
        "engine": "playwright-chromium",
        "playwright_installed": playwright_installed,
        "playwright_version": playwright_version,
        "capabilities": _capabilities_dict(engine),
    }

    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="andrew-navigator",
        description="Standalone, provider-agnostic Web navigation infrastructure for AI agents.",
    )
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")

    subparsers = parser.add_subparsers(dest="command", required=True)

    doctor = subparsers.add_parser(
        "doctor",
        help="Report local Navigator identity, runtime and engine capabilities.",
    )
    doctor.add_argument("--identity", default="andrew")
    doctor.add_argument(
        "--runtime-root",
        type=Path,
        default=_default_runtime_root(),
    )
    doctor.add_argument("--headless", action="store_true")
    doctor.set_defaults(func=_doctor)

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return int(args.func(args))


if __name__ == "__main__":
    raise SystemExit(main())
