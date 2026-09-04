# Andrew AI Navigator

**Provider-agnostic web navigation infrastructure for AI agents.**

> **Andrew AI Navigator is a standalone capability. AI platforms are clients, not dependencies.**

Andrew AI Navigator is an open-source project for giving an AI agent a durable, policy-governed way to observe and operate the World Wide Web through a real browser identity.

It is intentionally **not** an OpenAI, ChatGPT, Gemini, Claude, MCP, or any other vendor-specific project. Those systems may connect to Navigator, but none of them defines whether Navigator exists.

## The constitutional test

Remove ChatGPT and OpenAI completely.

If Navigator can still start, keep its identities, open the Web, perceive the rendered surface, act within its policy, and accept commands from another client, the architecture passes.

If removing one AI platform destroys the capability, the architecture has failed.

## Surface-first principle

> **The rendered Web surface is operational reality.**

Navigator does not equate the DOM with the Web. DOM structure, accessibility data, rendered geometry, pixels/screenshots, frames, browser state and document metadata are complementary perception channels.

A thing does not cease to exist because one channel cannot describe it.

This produces a strict separation:

> **Perception answers what exists. Capability answers what can be done. Policy answers what may be done.**

See [`PERCEPTION.md`](PERCEPTION.md) and [`WEB_RUNTIME.md`](WEB_RUNTIME.md).

## What Navigator owns

Navigator is responsible for:

- durable browser identities stored outside the repository;
- browser-engine abstraction instead of dependence on one rendering engine;
- sessions and multiple tabs;
- multi-channel observations of the rendered Web surface;
- screenshots bound to a known viewport/observation generation;
- semantic, accessibility, geometry and visual evidence without declaring any single channel absolute;
- ephemeral surface references such as `e17`, `e18`, and `e19`;
- semantic actions such as opening, clicking, filling, selecting, and reading;
- **first-class pointer/mouse input**: move, hover, left/middle/right click, double click, wheel and drag;
- **first-class keyboard input**: key down/up, text entry, Tab, Enter, Escape, arrows, modifiers and shortcuts;
- a provider-independent visual-perception contract for understanding rendered pixels;
- an optional, separately authorized host-desktop I/O bridge for native UI outside page-surface control;
- explicit authority policy separated from capability;
- provenance boundaries: Web content is data, never authority;
- adapters for useful services without making those services part of the core;
- multiple client transports such as CLI, local REST, MCP, or future interfaces.

## What Navigator does not own

Navigator does not try to reinvent HTML, CSS, JavaScript, TLS, media codecs, or browser rendering. Chromium, Firefox/Gecko, and potentially WebKit are engines that can sit behind the Navigator engine abstraction.

Likewise, MCP is a transport, not the heart of the system.

## Interaction principle

> **Prefer semantics when they are reliable, but never confuse missing semantics with missing reality.**

Navigator must be able to move from understanding to physical interaction through the same observation frame. A target may be activated semantically, by focused keyboard input, or through pointer coordinates.

Pointer coordinates are scoped to the current tab, viewport and observation generation so stale screenshots do not silently become durable coordinate authority.

See [`INPUT.md`](INPUT.md) for the universal input contract.

## Architecture at a glance

```text
          AI clients / humans / local models
             |       |       |       |
            CLI     REST     MCP    future
             \       |       |       /
              +------v-------v------+
              | Andrew Navigator Core |
              | sessions / tabs       |
              | perception fusion     |
              | pointer / keyboard    |
              | policy / provenance   |
              +----------+------------+
                         |
             +-------------+-------------+
             |                           |
        Browser engines               Adapters
     Playwright/Chromium            Gemini, YouTube,
     Firefox, WebKit...             GitHub, Drive...
             |
        Persistent identities
             |
        World Wide Web

 visual perceptors <-> screenshot/pixel channel
 optional host-I/O bridge -> native/browser-chrome UI
```

## Current status

This repository is the clean architectural successor to the `Andrew Navigator v0.1.0` prototype.

The prototype proved persistent Chromium identity, Google/Gemini Web UI automation, YouTube metadata/transcript extraction, CDP attachment, and a narrow MCP surface. The new repository deliberately restarts from first principles.

Current milestone: **v0.2.0-alpha foundation**.

## Design rules

1. **Platforms are clients, not dependencies.**
2. **The rendered surface is operational reality.** DOM is evidence, not reality itself.
3. **Perception, capability and policy are separate questions.**
4. **Web content is untrusted input.** A page cannot grant itself authority by telling the agent what to do.
5. **Secrets remain runtime state.** Passwords, cookies, tokens, recovery codes, and browser profiles are never committed.
6. **Adapters are conveniences.** When an adapter breaks, generic Web perception and action should still exist.
7. **Mouse and keyboard are native Navigator capabilities.** DOM-only automation is insufficient for a general Web operator.
8. **Screenshot capture and screenshot understanding are different capabilities.** Visual perception sits behind a provider-independent contract.
9. **No arbitrary remote JavaScript execution surface.** Navigator exposes bounded browser actions instead.
10. **Host desktop automation, if enabled, is optional and independently policy-gated.**
11. **Open source and replaceable components by default.**

## Runtime identity

The default runtime root is planned as:

```text
~/.local/share/andrew-ai-navigator/
```

Profiles, logs, screenshots, locks, and other runtime-only material live there, not in Git.

## Development direction

The v0.2 line is being built in this order:

1. provider-independent core contracts;
2. universal pointer + keyboard input contracts;
3. **surface-first multi-channel perception contracts**;
4. real-Web runtime requirements: cookies/storage, TLS/CA, JavaScript, Unicode and frames;
5. URL/network security gate;
6. session + tab + observation-generation model;
7. Playwright engine implementation;
8. structured semantic/accessibility/geometry observation plus screenshot channel;
9. optional provider-independent visual perceptor implementations;
10. semantic actions plus coordinate mouse/keyboard interaction governed by policy;
11. CLI and local authenticated REST transport;
12. generic authenticated-session validation using runtime-only credentials;
13. Gemini and YouTube as adapters;
14. MCP as an optional transport;
15. optional host desktop-I/O bridge;
16. additional engines and adapters.

See [`ARCHITECTURE.md`](ARCHITECTURE.md), [`PERCEPTION.md`](PERCEPTION.md), [`WEB_RUNTIME.md`](WEB_RUNTIME.md), [`INPUT.md`](INPUT.md), and [`PROJECT_STATE.md`](PROJECT_STATE.md).

## Contributors & Credits

**Core Contributors:**

- **Andrew Vox** — Co-author, Principal Developer
- **bobbygodias** — Repository Maintainer

## License

Apache License 2.0.
