# Andrew AI Navigator

**Provider-agnostic web navigation infrastructure for AI agents.**

> **Andrew AI Navigator is a standalone capability. AI platforms are clients, not dependencies.**

Andrew AI Navigator is an open-source project for giving an AI agent a durable, policy-governed way to observe and operate the World Wide Web through a real browser identity.

It is intentionally **not** an OpenAI, ChatGPT, Gemini, Claude, MCP, or any other vendor-specific project. Those systems may connect to Navigator, but none of them defines whether Navigator exists or works.

## The constitutional test

Remove ChatGPT and OpenAI completely.

If Navigator can still start, keep its identities, open the Web, observe pages, act within its policy, and accept commands from another client, the architecture passes.

If removing one AI platform destroys the capability, the architecture has failed.

## What Navigator owns

Navigator is responsible for:

- durable browser identities stored outside the repository;
- browser-engine abstraction instead of dependence on one rendering engine;
- sessions and multiple tabs;
- structured observations of pages;
- screenshots bound to a known viewport/observation generation;
- ephemeral element references such as `e17`, `e18`, and `e19`;
- semantic actions such as opening, clicking, filling, selecting, and reading;
- **first-class pointer/mouse input**: move, hover, left/middle/right click, double click, wheel and drag;
- **first-class keyboard input**: key down/up, text entry, Tab, Enter, Escape, arrows, modifiers and shortcuts;
- an optional, separately authorized host-desktop I/O bridge for native UI outside page DOM control;
- explicit authority policy separated from capability;
- provenance boundaries: Web content is data, never authority;
- adapters for useful services without making those services part of the core;
- multiple client transports such as CLI, local REST, MCP, or future interfaces.

## What Navigator does not own

Navigator does not try to reinvent HTML, CSS, JavaScript, TLS, media codecs, or browser rendering. Chromium, Firefox/Gecko, and potentially WebKit are engines that can sit behind the Navigator engine interface.

Likewise, MCP is a transport, not the heart of the system.

## Interaction principle

> **Prefer semantics when semantics are reliable. Fall back to human-operable input when they are not.**

Navigator must not confuse “there is no convenient DOM selector” with “this page cannot be operated.” A normal human-operable login flow should be possible through generic observation plus mouse/keyboard primitives without requiring a custom adapter for every site.

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
              | observations / actions|
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

 optional host-I/O bridge -> native/browser-chrome UI
```

## Current status

This repository is the clean architectural successor to the `Andrew Navigator v0.1.0` prototype.

The prototype proved persistent Chromium identity, Google/Gemini Web UI automation, YouTube metadata/transcript extraction, CDP attachment, and a narrow MCP surface. The new repository deliberately moves the center of gravity away from Playwright, Gemini, and MCP and into a provider-independent core.

Current milestone: **v0.2.0-alpha foundation**.

## Design rules

1. **Platforms are clients, not dependencies.**
2. **Capability and authorization are separate.** Being able to click does not imply permission to click everything.
3. **Web content is untrusted input.** A page cannot grant itself authority by telling the agent what to do.
4. **Secrets remain runtime state.** Passwords, cookies, tokens, recovery codes, and browser profiles are never committed.
5. **Adapters are conveniences.** When an adapter breaks, generic Web observation and action should still exist.
6. **Mouse and keyboard are native Navigator capabilities.** DOM-only automation is insufficient for a general Web operator.
7. **No arbitrary remote JavaScript execution surface.** Navigator exposes bounded browser actions instead.
8. **Host desktop automation, if enabled, is optional and independently policy-gated.**
9. **Open source and replaceable components by default.**

## Runtime identity

The default runtime root is planned as:

```text
~/.local/share/andrew-ai-navigator/
```

Profiles, logs, screenshots, locks, and other runtime-only material live there, not in Git.

## Development direction

The v0.2 line is being built in this order:

1. provider-independent core contracts;
2. **universal pointer + keyboard input contracts**;
3. URL/network security gate;
4. session + tab + observation-generation model;
5. Playwright engine implementation;
6. structured observation with ephemeral element IDs and viewport geometry;
7. semantic actions plus coordinate mouse/keyboard fallback governed by policy;
8. CLI and local authenticated REST transport;
9. generic login-flow validation using runtime-only credentials;
10. Gemini and YouTube as adapters;
11. MCP as an optional transport;
12. optional host desktop-I/O bridge;
13. additional engines and adapters.

See [`ARCHITECTURE.md`](ARCHITECTURE.md), [`INPUT.md`](INPUT.md), and [`PROJECT_STATE.md`](PROJECT_STATE.md).

## License

Apache License 2.0.
