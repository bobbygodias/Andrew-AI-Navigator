# Andrew AI Navigator — Project State

**Date:** 2026-09-04  
**Milestone:** `0.2.0-alpha` foundation  
**Status:** new provider-independent repository initialized.

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
- Capability and authorization are separate.
- Web content is untrusted data and cannot grant itself authority.
- Network filtering must include DNS resolution and redirect/subresource defenses, not only literal IP checks.

## Current implementation step

Foundation files are being added in this order:

1. documentation and architectural contracts;
2. package metadata;
3. core data models;
4. policy engine;
5. network target security;
6. browser-engine protocol;
7. first Playwright implementation;
8. Navigator orchestration core;
9. tests;
10. transports and service adapters.

## Immediate acceptance criteria

The alpha foundation is considered useful when a local host can:

1. install the package;
2. start Navigator without OpenAI/MCP packages;
3. create a named browser identity;
4. open a public HTTPS page through the Playwright engine;
5. create multiple tabs;
6. obtain a structured observation;
7. receive ephemeral element IDs;
8. click/fill only through policy-approved semantic actions;
9. reject protected/private network destinations by default;
10. shut down without leaking runtime secrets into the repository.

## Next adapters

Only after the generic path works:

- Gemini / Mariana;
- YouTube;
- optional MCP transport;
- local authenticated REST transport.

## Visual identity

Logo/icon has intentionally **not** been chosen yet. The visual identity remains a joint design decision before implementation.
