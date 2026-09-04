# Andrew AI Navigator — Project State

**Date:** 2026-09-04  
**Milestone:** `0.2.0-alpha` foundation  
**Status:** provider-independent repository initialized; universal input requirement promoted to core architecture.

## Why this repository exists

The `Andrew Navigator v0.1.0` prototype proved the feasibility of a persistent-browser identity and useful service adapters. It also revealed an architectural problem: Playwright, Gemini, and MCP were too close to the center of the system.

This repository corrects that.

Andrew AI Navigator is being rebuilt so that its Web capability exists independently of any AI platform.

## Constitutional invariant

**Andrew AI Navigator is a standalone capability. AI platforms are clients, not dependencies.**

A build that requires ChatGPT/OpenAI merely to exist fails this invariant.

## Proven by v0.1

The previous prototype demonstrated:

- persistent Chromium profile state;
- local persistent browser mode;
- optional remote Chromium/CDP attachment;
- Google browser identity without embedding account passwords in code;
- Gemini Web UI conversation access;
- YouTube metadata and transcript extraction;
- URL safety checks;
- MCP exposure;
- automated tests for core persistence/security behavior.

These results are treated as experimental evidence, not as immutable architecture.

## v0.2 architectural decisions

- Core is provider-agnostic.
- MCP is optional transport only.
- Gemini and YouTube are adapters only.
- Browser engines sit behind a replaceable interface.
- Identity belongs to Navigator runtime state.
- Sessions and tabs replace the single-active-page model.
- Page observations produce ephemeral element references.
- Generic actions are semantic; arbitrary JavaScript execution is not part of the remote action surface.
- **Pointer/mouse and keyboard input are first-class Navigator capabilities.**
- Semantic targeting is preferred, but the Navigator must fall back to human-operable coordinate and key input when DOM/accessibility targeting is insufficient.
- Coordinate actions are bound to tab, viewport and observation generation to reduce stale-target errors.
- A generic human-operable login flow must not require a site-specific adapter merely because the page needs pointer/keyboard interaction.
- Native UI outside browser-page control may later be handled by an optional, separately authorized host desktop-I/O bridge.
- Capability and authorization are separate.
- Web content is untrusted data and cannot grant itself authority.
- Network filtering must include DNS resolution and redirect/subresource defenses, not only literal IP checks.

## Universal input requirement

The input contract is now a foundation requirement, not a future enhancement.

Browser-surface pointer support must cover at least:

- move/hover;
- left, middle and right click;
- double click;
- button down/up;
- wheel/scroll;
- drag.

Browser-surface keyboard support must cover at least:

- key down/up;
- text entry;
- Enter, Tab, Escape, Backspace and Delete;
- arrows/navigation keys;
- modifiers and chords/shortcuts;
- other engine-supported special keys.

See `INPUT.md`.

## Current implementation step

Foundation files are being added in this order:

1. documentation and architectural contracts;
2. universal input contracts;
3. package metadata;
4. core data models;
5. policy engine;
6. network target security;
7. browser-engine protocol including semantic + pointer + keyboard capability reporting;
8. first Playwright implementation;
9. Navigator orchestration core;
10. tests;
11. transports and service adapters.

## Immediate acceptance criteria

The alpha foundation is considered useful when a local host can:

1. install the package;
2. start Navigator without OpenAI/MCP packages;
3. create a named browser identity;
4. open a public HTTPS page through the Playwright engine;
5. create multiple tabs;
6. obtain a structured observation and screenshot geometry;
7. receive ephemeral element IDs;
8. click/fill through policy-approved semantic actions;
9. move/click/scroll/drag through pointer input;
10. type text and operate navigation/special keys through keyboard input;
11. complete an ordinary generic login interaction where site policy and authentication requirements permit it;
12. reject protected/private network destinations by default;
13. keep passwords/tokens/runtime secrets out of repository and audit logs;
14. shut down without leaking runtime secrets into the repository.

## Next adapters

Only after the generic path works:

- Gemini / Mariana;
- YouTube;
- optional MCP transport;
- local authenticated REST transport.

## Visual identity

Logo/icon has intentionally **not** been chosen yet. The visual identity remains a joint design decision before implementation.
