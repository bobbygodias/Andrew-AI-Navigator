# Andrew AI Navigator — Real Web Runtime

**Target:** v0.2.0-alpha

Andrew AI Navigator is intended to operate the real World Wide Web through a real browser engine. A usable Navigator cannot stop at DOM selectors or simplified HTTP fetches.

## 1. Runtime principle

> If a standards-compliant browser needs a Web capability to participate in a site, Navigator must preserve that capability unless local policy explicitly disables it.

A second principle governs perception:

> The rendered browser surface is operational reality. DOM, accessibility data, geometry, pixels and browser state are complementary evidence about that reality.

The Navigator Core does not reimplement the Web platform. Browser engines execute Web standards; Navigator governs identity, state, observation, input, policy, provenance and audit.

See `PERCEPTION.md` for the surface-first perception model.

## 2. Cookies and browser state

Persistent identities must preserve legitimate browser state required by ordinary Web sessions, including where supported by the selected engine:

- first-party cookies;
- SameSite behavior;
- Secure and HttpOnly cookie semantics;
- partitioned/site-scoped storage behavior;
- session cookies;
- localStorage and sessionStorage;
- IndexedDB;
- Cache Storage;
- service-worker state;
- ordinary browser permissions when explicitly granted;
- site preferences needed for continuity.

Navigator must not flatten this state into a home-grown cookie jar when the engine can maintain the browser profile natively.

Cookie values, storage databases and authentication artifacts are runtime identity state and must never be committed to the repository or emitted into normal audit logs.

Identity isolation is mandatory: state from one Navigator identity must not silently leak into another.

## 3. TLS, Certificate Authorities and secure transport

Navigator should inherit standards-compliant TLS behavior from its browser engine and operating environment.

Requirements include:

- normal certificate-chain validation;
- hostname validation;
- expiry/not-before validation;
- HSTS behavior where the engine supports it;
- modern TLS negotiation provided by the browser engine;
- ordinary system/browser CA trust stores;
- explicit reporting of certificate failures.

Certificate errors must not be silently ignored.

A locally controlled deployment may support an explicitly configured additional CA trust source for legitimate environments such as a private laboratory, development network or enterprise proxy. Such trust expansion must be local configuration, visible to the operator and disabled by default.

Navigator must never expose a generic remote command equivalent to "ignore all TLS errors" as an ordinary browsing capability.

## 4. JavaScript and modern Web execution

JavaScript execution is a browser-engine responsibility and must normally remain enabled for full browsing sessions.

Navigator should permit the engine to execute normal site code including, where supported:

- ECMAScript/JavaScript;
- modules;
- Web Workers;
- Service Workers;
- WebAssembly;
- Shadow DOM;
- Custom Elements;
- client-side routing;
- fetch/XHR;
- WebSocket and EventSource;
- ordinary media, canvas and WebGL APIs.

This does **not** imply that remote Navigator clients receive an unrestricted `eval_javascript()` capability. Page JavaScript execution and remote arbitrary-code execution are separate concepts.

The page may execute its own standards-compliant code inside the browser sandbox while Navigator continues to expose bounded observation, semantic, pointer and keyboard capabilities.

## 5. Web formats and less-common technologies

Observation must remain robust when information is represented through technologies beyond simple HTML text.

Relevant examples include:

- HTML/XHTML;
- CSS-generated visibility/state;
- SVG;
- MathML;
- XML-based documents rendered by the browser;
- JSON-backed client applications;
- canvas-based interfaces;
- accessibility trees;
- embedded documents and frames;
- Web components;
- WebAssembly-backed applications;
- WebGL/custom-rendered applications.

Navigator combines perception channels rather than treating one source as authoritative:

1. DOM/semantic structure;
2. accessibility information;
3. rendered geometry and hit testing;
4. screenshot/pixel observation;
5. frame/browsing-context state;
6. network/document metadata when policy permits.

A control presented on the rendered surface must not be considered nonexistent merely because it is absent from a convenient DOM selector path.

## 6. Natural languages, Unicode and writing systems

The Web is multilingual. Navigator observations must preserve Unicode text without lossy normalization and should expose useful language metadata where available.

The system should support pages containing:

- multiple languages in one document;
- right-to-left and left-to-right scripts;
- mixed writing directions;
- non-Latin alphabets;
- uncommon Unicode characters;
- locale-sensitive form controls;
- internationalized domain names.

The Core does not need to translate every language itself. Its responsibility is to preserve text, structure, visual context and language hints so the connected AI client or optional language component can understand or translate it.

Where text exists only visually, visual text recognition may supplement structured channels while retaining channel provenance.

## 7. Frames, popups and browsing contexts

Real sites use more than one document surface.

Navigator must model and observe:

- top-level pages;
- iframes, including cross-origin frames where the browser permits observation or input;
- popup windows;
- new tabs;
- OAuth/authentication windows;
- modal overlays;
- browser permission prompts where the engine exposes them.

A login or consent flow that changes browsing context must not be mistaken for navigation failure.

## 8. Surface capability and external site policy

The Navigator architecture does not create a special class of "human-only surface" that it is structurally unable to perceive.

If the browser renders a control, image, canvas object, challenge, dialog or other interactive surface, Navigator should attempt to represent what is present using its available perception channels and should retain ordinary pointer, keyboard and focus capability over that surface where the engine permits it.

This includes visually rendered interfaces whose meaning is weakly represented or absent in DOM/accessibility data.

A website may separately impose terms, authentication requirements, anti-automation rules, rate limits or other restrictions. Those are external policy questions. They do not redefine what exists on the browser surface and therefore must not be implemented as artificial sensory blindness in the Core.

The architectural separation is:

> **Perception answers what exists. Capability answers what can be done. Policy answers what may be done.**

## 9. Browser fidelity and feature detection

Navigator must prefer standards-compliant behavior over brittle site-specific emulation.

The engine layer should report capabilities such as:

- JavaScript available;
- cookies/storage available;
- pointer input available;
- keyboard input available;
- screenshot available;
- geometry/hit-test information available;
- service workers available;
- downloads/uploads available;
- popup/frame handling available;
- host-I/O bridge available or unavailable.

Adapters may rely on these declared capabilities but must not assume a specific browser vendor unless explicitly written for one.

## 10. Success criteria

A real-Web-capable engine integration is not considered complete until it can demonstrate at least the following without OpenAI-specific dependencies:

1. persist an ordinary authenticated browser session through native browser state;
2. retain cookie/storage continuity across Navigator restarts for the same identity;
3. isolate state between identities;
4. reject invalid TLS certificates by default;
5. execute a modern JavaScript application normally;
6. operate a page using semantic input and rendered pointer/keyboard input;
7. preserve Unicode and mixed-language page content in observations;
8. handle iframe/popup/tab transitions without losing session identity;
9. represent visible controls even when DOM/accessibility semantics are incomplete;
10. preserve the distinction between perception, capability and policy rather than encoding policy as sensory incapacity.
