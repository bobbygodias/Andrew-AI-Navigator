# Andrew AI Navigator — Project State

**Date:** 2026-09-04  
**Milestone:** `0.2.0-alpha` foundation  
**Status:** provider-independent repository initialized; universal input and surface-first perception promoted to core architecture.

## Why this repository exists

The `Andrew Navigator v0.1.0` prototype proved the feasibility of a persistent-browser identity and useful service adapters. It also revealed an architectural problem: Playwright, Gemini, and MCP were too close to the center of the system.

This repository corrects that.

Andrew AI Navigator is being rebuilt so that its Web capability exists independently of any AI platform.

## Constitutional invariants

**Andrew AI Navigator is a standalone capability. AI platforms are clients, not dependencies.**

A build that requires ChatGPT/OpenAI merely to exist fails this invariant.

A second invariant now governs perception:

**The rendered Web surface is operational reality.**

DOM, accessibility data, geometry, pixels, frames and browser state are perception channels. None alone is allowed to redefine the Web as only the portion easiest to automate.

The project therefore keeps three questions distinct:

1. **Perception:** what exists on the browser surface?
2. **Capability:** what actions can the Navigator physically perform?
3. **Policy:** which available actions are authorized in the current context?

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
- Page observations are generation-scoped.
- Surface perception fuses multiple channels rather than treating DOM as reality.
- Pixel/screenshot capture and visual understanding are separate capabilities.
- Visual understanding sits behind a provider-independent `VisualPerceptor` contract.
- Surface objects can exist with weak or absent DOM semantics if other channels perceive them.
- Generic actions are bounded; arbitrary remote JavaScript execution is not part of the public action surface.
- **Pointer/mouse and keyboard input are first-class Navigator capabilities.**
- Semantic targeting is preferred when reliable, but coordinate and keyboard input remain native capabilities over the same surface.
- Coordinate actions are bound to tab, viewport and observation generation to reduce stale-target errors.
- A generic authenticated browsing flow must not require a site-specific adapter merely because the surface needs pointer/keyboard interaction.
- Native UI outside browser-page control may later be handled by an optional, separately authorized host desktop-I/O bridge.
- Capability and authorization are separate.
- Web content is untrusted data and cannot grant itself authority.
- Network filtering must include DNS resolution and redirect/subresource defenses, not only literal IP checks.
- Real-Web runtime requirements include browser-native cookies/storage, normal TLS/CA validation, JavaScript, Unicode, frames and popup handling.

## Universal input requirement

The input contract is a foundation requirement, not a future enhancement.

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

## Surface perception requirement

The perception model is defined in `PERCEPTION.md`.

Current code now includes:

- `PerceptionChannel`;
- `SurfaceEvidence`;
- `SurfaceObject`;
- `Rect`;
- `ObservationFrame`;
- `VisualFrame`;
- provider-independent `VisualPerceptor` protocol.

The BrowserEngine contract now distinguishes compact semantic observation from full multi-channel surface observation and reports observation/runtime capabilities explicitly.

A pixel-only perceived object is valid. That rule exists specifically to prevent future implementations from silently collapsing the browser back into a DOM scraper.

## Real-Web runtime requirement

See `WEB_RUNTIME.md`.

The selected browser engine is expected to preserve ordinary Web behavior including:

- browser-native cookie/storage continuity;
- identity isolation;
- standards-compliant TLS/CA validation;
- JavaScript and modern Web application execution;
- Unicode and mixed writing systems;
- frames, tabs, popups and modal browsing contexts;
- canvas/SVG/WebGL/custom-rendered surfaces as perceivable browser reality.

## Current implementation step

Foundation work is now ordered as follows:

1. documentation and architectural contracts;
2. universal input contracts;
3. surface-first perception contracts;
4. package metadata;
5. core data models;
6. policy engine;
7. network target security;
8. browser-engine protocol with semantic + pointer + keyboard + perception capability reporting;
9. first Playwright implementation;
10. Navigator orchestration core;
11. CI and automated tests;
12. transports and service adapters.

## Immediate acceptance criteria

The alpha foundation is considered useful when a local host can:

1. install the package;
2. start Navigator without OpenAI/MCP packages;
3. create a named browser identity;
4. open a public HTTPS page through the Playwright engine;
5. create multiple tabs;
6. obtain a generation-scoped surface observation;
7. preserve semantic/accessibility/geometry evidence when available;
8. retain a screenshot/pixel channel tied to the same viewport;
9. represent a visible control even when useful DOM semantics are absent;
10. click/fill through policy-approved semantic actions;
11. move/click/scroll/drag through pointer input;
12. type text and operate navigation/special keys through keyboard input;
13. persist ordinary authenticated browser state without placing secrets in source control;
14. execute modern JavaScript applications normally;
15. preserve Unicode/multilingual content;
16. handle frame/popup/tab transitions without losing identity;
17. reject protected/private network destinations by default;
18. keep passwords/tokens/runtime secrets out of repository and audit logs;
19. shut down without leaking runtime secrets into the repository.

## Tests and CI

Foundation tests cover the original core contracts plus the new perception model, including a pixel-only surface object and generation-bound surface objects.

A GitHub Actions workflow for Python 3.11 and 3.12 has been added. At the time this state file was written, the workflow had been committed but GitHub had not yet reported a run through the connected API, so no CI result is claimed here.

## Next adapters

Only after the generic path works:

- Gemini / Mariana;
- YouTube;
- optional MCP transport;
- local authenticated REST transport.

## Visual identity

Logo/icon has intentionally **not** been chosen yet. The visual identity remains a joint design decision before implementation.
