# Andrew AI Navigator — Architecture

**Target:** v0.2.0-alpha

## 1. Purpose

Andrew AI Navigator is a standalone Web-operating subsystem for AI agents.

The core architectural rule is simple:

> AI platforms are clients, not dependencies.

The system must remain useful if OpenAI, ChatGPT, MCP, Gemini, or any single browser engine is removed.

A second rule follows from the first:

> A browser operator must be able to perceive and act beyond the happy path of a clean DOM.

Structured semantic actions are preferred, but pointer and keyboard input are first-class capabilities, not afterthoughts.

## 2. Layer model

### 2.1 Core

The Core owns concepts that must survive changes in vendors and transports:

- Navigator lifecycle;
- identities;
- sessions;
- tabs;
- observations;
- ephemeral element references;
- semantic actions;
- pointer input;
- keyboard input;
- authority policy;
- provenance labels;
- audit events.

The Core must not import OpenAI-specific or MCP-specific packages.

### 2.2 Browser engines

Browser engines implement a narrow contract such as:

- start/stop;
- create or restore a session;
- list/create/close tabs;
- navigate;
- observe;
- click an observed element;
- fill an observed field;
- move the pointer;
- click/double-click/right-click by coordinate;
- hover;
- scroll/wheel;
- drag and drop;
- press/release keyboard keys;
- type text;
- send key chords and special keys;
- capture a screenshot.

The first implementation uses Playwright with Chromium because the v0.1 prototype proved that path. The contract must allow future Firefox/Gecko and WebKit implementations.

### 2.3 Input subsystem

Navigator has a dedicated input subsystem because DOM-level automation alone cannot operate the whole Web reliably.

Input is divided into three levels.

#### Level 1 — Semantic interaction

Preferred when the page exposes a reliable structured target:

- `click(element_ref)`
- `fill(element_ref, value)`
- `select(element_ref, value)`
- `focus(element_ref)`

Semantic interaction is easiest to audit and most resilient when accessibility and DOM information are good.

#### Level 2 — Browser-surface pointer and keyboard

Used when an action is visible and human-operable but not represented cleanly enough for semantic targeting.

Pointer primitives include:

- absolute move to `(x, y)`;
- relative move;
- hover;
- left/middle/right click;
- double click;
- button down/up;
- wheel/scroll on both axes;
- drag from one coordinate to another;
- coordinate click against the current screenshot/viewport generation.

Keyboard primitives include:

- `key_down(key)` / `key_up(key)`;
- `press(key)`;
- `chord(keys...)`;
- text entry;
- Enter, Tab, Escape, Backspace, Delete;
- arrow/navigation keys;
- modifiers such as Ctrl, Alt, Shift and Meta;
- function keys where supported.

Pointer coordinates are always bound to a specific tab, viewport, device scale and observation generation. A stale screenshot must not silently remain a valid coordinate authority after navigation or major layout change.

Text entry and keyboard events are distinct operations. Text entry inserts intended characters; key events model physical/special-key behavior. Engines may implement them differently.

#### Level 3 — Optional host desktop I/O bridge

Some interactions escape the browser page entirely: native file pickers, browser permission prompts, certain password-manager surfaces, external authentication windows, certificate dialogs or other OS-level UI.

Navigator therefore permits an optional, separately packaged host-I/O bridge with its own policy boundary.

The Core does not require this bridge. It must be disabled by default and explicitly enabled locally. The bridge must expose bounded pointer/keyboard/window primitives rather than arbitrary shell execution.

This level exists so the architecture does not pretend every browser task ends at the DOM boundary.

### 2.4 Identity store

An identity is durable runtime state, not a password in source code.

Examples:

- `andrew`
- `andrew-google`
- `anonymous`
- `testing`

Each identity has isolated browser state and its own policy context.

The repository never contains passwords, cookie dumps, browser databases, recovery codes, or authentication tokens.

### 2.5 Observation model

A page observation is a bounded snapshot of what Navigator can currently perceive.

It may contain:

- URL and title;
- principal readable text;
- links;
- buttons;
- fields;
- menus;
- images and useful alt text;
- download candidates;
- accessibility metadata;
- viewport dimensions and device scale;
- screenshot references;
- ephemeral interactive-element IDs.

Example:

```text
e17  button  "Send"
e18  textbox "Search"
e19  link    "Mariana"
```

Element references are valid only for the observation generation that produced them. This prevents a client from treating stale DOM coordinates as durable authority.

Screenshots and coordinate actions follow the same generation rule.

### 2.6 Action model

Generic actions are explicit capabilities rather than arbitrary code execution.

Semantic examples:

- `open(url)`
- `observe()`
- `click(element_ref)`
- `fill(element_ref, value)`
- `back()` / `forward()`
- `new_tab()` / `close_tab()`
- `screenshot()`

Input examples:

- `pointer_move(x, y)`
- `pointer_click(x, y, button)`
- `pointer_drag(from, to)`
- `wheel(dx, dy)`
- `key_press(key)`
- `key_chord(keys)`
- `type_text(text)`

There is deliberately no generic `eval_javascript(script)` remote capability.

### 2.7 Policy engine

Capability is not authorization.

Policy decides whether an otherwise supported action may run for a given identity, destination, provenance, client and interaction level.

Policy examples:

- public Web reading: allow;
- pointer movement/hover: generally low impact;
- unknown-site form submission: deny by default;
- Gemini conversation: allow configured conversational action;
- Gmail send: require explicit authorization policy;
- host desktop I/O: disabled unless locally enabled;
- local/private network: deny unless local configuration explicitly permits it.

Policies are local configuration and can evolve independently of browser engines.

Sensitive input must be redacted from logs. Password text, one-time codes, recovery codes, tokens and equivalent secrets must never be echoed into audit events merely because Navigator typed them.

### 2.8 Provenance boundary

Navigator distinguishes instruction/data origins conceptually:

- `OPERATOR`
- `AGENT`
- `CLIENT`
- `WEB_UNTRUSTED`
- `LOCAL_CONFIG`

A Web page is always `WEB_UNTRUSTED` unless transformed by an explicitly trusted local mechanism.

A page saying "ignore previous instructions" is page content. It does not alter Navigator policy, identity permissions, input authority, or client authority.

This is the architectural boundary against Web-originated prompt injection.

### 2.9 Adapters

Adapters provide stable, high-level operations for useful services while depending on generic Navigator capabilities.

Examples:

- Gemini;
- YouTube;
- GitHub;
- Google Drive;
- Google Scholar.

Adapters are optional. A broken Gemini adapter must not destroy generic browsing.

### 2.10 Transports

Transports expose the Core to clients:

- CLI;
- authenticated local REST;
- MCP;
- WebSocket/event stream;
- future Android or local-agent interfaces.

Deleting the MCP package must not stop Navigator from starting or navigating.

## 3. Session and tab model

v0.1 kept one active page. v0.2 replaces that with explicit identifiers:

```text
identity -> session -> tab -> observation generation -> element refs / coordinate frame
```

This permits, for example, keeping Gemini open in one tab while researching another site in a second tab without conflating page state.

## 4. Network security

The v0.1 literal-host check is not sufficient for the long term.

The v0.2 security layer must defend against:

- localhost and loopback;
- RFC1918/private addresses;
- link-local addresses;
- unspecified and multicast ranges;
- hostnames resolving to private/local addresses;
- redirects into forbidden destinations;
- browser subresource requests that unexpectedly target protected networks.

The first implementation should validate both the requested URL and resolved addresses and should intercept browser requests where the engine permits it.

## 5. Audit model

Audit logs may record:

- timestamp;
- client identity;
- Navigator identity;
- action name;
- destination origin;
- interaction level;
- policy decision;
- outcome.

Audit logs must not record passwords, cookies, authorization headers, raw tokens, recovery codes, one-time authentication codes, or complete sensitive form values.

For coordinate actions, logs may retain bounded structural metadata such as tab ID and coordinate pair, but not a secret-bearing screenshot unless local policy explicitly requests screenshot retention.

## 6. Dependency rule

Dependencies point inward toward stable contracts.

```text
transports -> core <- adapters
               ^
               |
             engines
               ^
               |
       optional host-I/O bridge
```

The Core does not import transports, service adapters, vendor SDKs or host automation packages.

## 7. Success criterion

The architecture succeeds when all of the following are true:

1. Navigator starts without ChatGPT/OpenAI.
2. Navigator can operate through at least one browser engine.
3. A different AI client can connect without changing the Core.
4. Persistent identities remain owned by Navigator runtime state.
5. Web content cannot promote itself into policy authority.
6. Replacing MCP, Gemini, or Chromium does not require redesigning the Core.
7. Navigator can use both semantic targeting and browser-surface pointer/keyboard input.
8. A human-operable login flow is not blocked merely because a control lacks a convenient DOM selector.
9. Optional OS-level UI automation remains a separate, explicitly authorized capability rather than silently expanding browser authority.
