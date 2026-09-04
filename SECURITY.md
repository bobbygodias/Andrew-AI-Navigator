# Andrew AI Navigator — Security Model

**Target:** v0.2.0-alpha

Andrew AI Navigator is intended to hold durable browser identities and operate the real Web. Security therefore has to protect powerful capability without redefining the Web as only the subset easiest to sandbox.

## 1. Core separation

Navigator keeps three questions distinct:

1. **Perception:** what exists on the browser surface?
2. **Capability:** what can the engine physically do?
3. **Policy:** what may be done in the current context?

Security policy must not be implemented as artificial sensory blindness.

## 2. Secrets and persistent identities

Browser identity state belongs to runtime storage, never source control.

The repository must not contain:

- passwords;
- cookie databases or cookie dumps;
- authentication/session tokens;
- authorization headers;
- recovery codes;
- one-time authentication codes;
- passkey private material;
- browser profile databases;
- private certificate keys.

The first Playwright engine stores one identity under a dedicated runtime profile directory. Separate identities must use separate profile directories.

Observation code deliberately does not read form `value` content merely because a field contains typed text. This prevents a password or OTP from becoming ordinary DOM evidence.

Raw perception channels must be treated as potentially sensitive as well. Screenshots and accessibility representations can contain private on-screen information even when they do not expose secret storage directly.

## 3. TLS and Certificate Authorities

Normal browser TLS validation stays enabled.

Navigator must not silently disable:

- certificate-chain validation;
- hostname validation;
- certificate validity periods;
- normal browser/system trust behavior.

A future custom-CA feature may trust an additional CA only through explicit local configuration for legitimate controlled environments. Generic remote `ignore all TLS errors` capability is not part of the normal browsing surface.

## 4. Network destination safety

The current Core rejects obvious protected targets during public HTTP/HTTPS navigation, including private, loopback, link-local, multicast, unspecified and reserved IP ranges.

The first Playwright engine also applies a best-effort BrowserContext request-routing guard and resolves intercepted HTTP/HTTPS requests before continuing them.

### Known limitation

Playwright request routing is not a complete network sandbox. In particular, browser routing does not provide a perfect boundary for every Service Worker request and cannot by itself eliminate DNS time-of-check/time-of-use races.

Therefore the current routing guard is **defense in depth, not the final SSRF boundary**.

A stronger deployment should add a lower-layer egress component such as a controlled proxy or host/network namespace policy capable of enforcing destination rules after DNS resolution and across browser subsystems.

Navigator must preserve Service Worker support for normal Web compatibility; disabling an entire Web capability merely to make filtering easier is not accepted as the final architecture.

## 5. Redirects

Initial destinations are validated before navigation. The Playwright engine also validates the resulting top-level HTTP/HTTPS URL after navigation.

Post-navigation validation can detect an unsafe final target but cannot retroactively prevent a request that a lower layer already allowed. Strong redirect safety is therefore part of the same planned lower-layer egress boundary described above.

## 6. Web content and authority

Web content is `WEB_UNTRUSTED` input.

A page may contain instructions, prompts, scripts or text that attempts to influence an AI client. Content does not gain Navigator policy authority merely by being rendered.

A Web page cannot by itself:

- expand identity permissions;
- enable host desktop I/O;
- authorize sensitive input;
- change local policy;
- convert Web-originated text into operator authority.

This is the Core boundary against Web-originated prompt injection.

## 7. JavaScript

Normal site JavaScript remains enabled because it is part of the modern Web platform.

This is separate from exposing arbitrary JavaScript execution to remote clients.

Navigator may use bounded internal evaluation inside an engine to inspect browser state or build observations, but a generic remote `eval_javascript(script)` capability is deliberately absent from the public Core contract.

## 8. Mouse and keyboard

Pointer and keyboard capability are first-class because a general browser operator cannot depend on DOM selectors alone.

Coordinates are bound to session, tab, viewport and observation generation. Actions against stale coordinate frames are rejected by the engine when detected.

Dynamic surfaces such as animated canvas/WebGL can change without a convenient DOM mutation signal. Strong visual-staleness detection remains an open engineering problem; clients should obtain a fresh observation when spatial state may have changed materially.

## 9. Visual perception

Screenshot capture and screenshot understanding are separate capabilities.

`VisualPerceptor` is provider-independent. Implementations may use local computer vision, local multimodal models, remote services or hybrids, but the Navigator Core must not require one vendor.

Visual observations may reveal private information displayed on screen. Retention, logging and remote transmission of screenshots must therefore be independently configurable.

## 10. Accessibility channel

Accessibility snapshots are a perception channel, not a privilege boundary.

They may contain information that is not obvious from plain DOM text. They must be handled as potentially sensitive observation data and must not be dumped into audit logs by default.

## 11. Host desktop I/O

Host desktop I/O is outside ordinary page-surface authority.

If implemented, it must be:

- optional;
- disabled by default;
- separately policy-gated;
- bounded to explicit pointer/keyboard/window primitives;
- isolated from arbitrary shell execution.

## 12. Audit logging

Audit events may record structural facts such as:

- action type;
- timestamp;
- tab/session identity;
- destination origin;
- policy decision;
- outcome.

Audit logging must not record raw passwords, cookies, tokens, authorization headers, OTPs, recovery codes or complete sensitive form values.

## 13. Reporting security issues

During the alpha stage, security findings should be opened through the repository's GitHub issue/discussion process only when disclosure is appropriate. Sensitive vulnerabilities should not be published with live credentials, private session material or exploitable secrets.
