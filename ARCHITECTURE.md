# Andrew AI Navigator — Architecture

**Target:** v0.2.0-alpha

## 1. Purpose

Andrew AI Navigator is a standalone Web-operating subsystem for AI agents.

The core architectural rule is simple:

> AI platforms are clients, not dependencies.

The system must remain useful if OpenAI, ChatGPT, MCP, Gemini, or any single browser engine is removed.

## 2. Layer model

### 2.1 Core

The Core owns concepts that must survive changes in vendors and transports:

- Navigator lifecycle;
- identities;
- sessions;
- tabs;
- observations;
- ephemeral element references;
- actions;
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
- capture a screenshot.

The first implementation uses Playwright with Chromium because the v0.1 prototype proved that path. The contract must allow future Firefox/Gecko and WebKit implementations.

### 2.3 Identity store

An identity is durable runtime state, not a password in source code.

Examples:

- `andrew`
- `andrew-google`
- `anonymous`
- `testing`

Each identity has isolated browser state and its own policy context.

The repository never contains passwords, cookie dumps, browser databases, recovery codes, or authentication tokens.

### 2.4 Observation model

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
- screenshot references;
- ephemeral interactive-element IDs.

Example:

```text
e17  button  "Send"
e18  textbox "Search"
e19  link    "Mariana"
```

Element references are valid only for the observation generation that produced them. This prevents a client from treating stale DOM coordinates as durable authority.

### 2.5 Action model

Generic actions are semantic rather than arbitrary code execution:

- `open(url)`
- `observe()`
- `click(element_ref)`
- `fill(element_ref, value)`
- `back()` / `forward()`
- `new_tab()` / `close_tab()`
- `screenshot()`

There is deliberately no generic `eval_javascript(script)` remote capability.

### 2.6 Policy engine

Capability is not authorization.

Policy decides whether an otherwise supported action may run for a given identity, destination, provenance, and client.

Policy examples:

- public Web reading: allow;
- unknown-site form submission: deny by default;
- Gemini conversation: allow configured conversational action;
- Gmail send: require explicit authorization policy;
- local/private network: deny unless local configuration explicitly permits it.

Policies are local configuration and can evolve independently of browser engines.

### 2.7 Provenance boundary

Navigator distinguishes instruction/data origins conceptually:

- `OPERATOR`
- `AGENT`
- `CLIENT`
- `WEB_UNTRUSTED`
- `LOCAL_CONFIG`

A Web page is always `WEB_UNTRUSTED` unless transformed by an explicitly trusted local mechanism.

A page saying "ignore previous instructions" is page content. It does not alter Navigator policy, identity permissions, or client authority.

This is the architectural boundary against Web-originated prompt injection.

### 2.8 Adapters

Adapters provide stable, high-level operations for useful services while depending on generic Navigator capabilities.

Examples:

- Gemini;
- YouTube;
- GitHub;
- Google Drive;
- Google Scholar.

Adapters are optional. A broken Gemini adapter must not destroy generic browsing.

### 2.9 Transports

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
identity -> session -> tab -> observation generation -> element refs
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
- policy decision;
- outcome.

Audit logs must not record passwords, cookies, authorization headers, raw tokens, recovery codes, or complete sensitive form values.

## 6. Dependency rule

Dependencies point inward toward stable contracts.

```text
transports -> core <- adapters
               ^
               |
             engines
```

The Core does not import transports, service adapters, or vendor SDKs.

## 7. Success criterion

The architecture succeeds when all of the following are true:

1. Navigator starts without ChatGPT/OpenAI.
2. Navigator can operate through at least one browser engine.
3. A different AI client can connect without changing the Core.
4. Persistent identities remain owned by Navigator runtime state.
5. Web content cannot promote itself into policy authority.
6. Replacing MCP, Gemini, or Chromium does not require redesigning the Core.
