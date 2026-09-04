# Andrew AI Navigator — Surface Perception

**Target:** v0.2.0-alpha

## 1. First principle

Andrew AI Navigator treats the **rendered Web surface** as the operational reality of browsing.

> If something exists in the browser experience, Navigator must not declare it nonexistent merely because one structural channel cannot describe it.

The DOM is valuable evidence. It is not the definition of reality.

The accessibility tree is valuable evidence. It is not the definition of reality.

Pixels are valuable evidence. They are not the only definition of reality either.

Navigator perception is therefore a **fusion of channels**.

## 2. Perception channels

A browser engine may expose any combination of the following channels for one observation generation:

- DOM / document structure;
- accessibility tree;
- rendered geometry and hit-test information;
- screenshot / pixel surface;
- frame and browsing-context topology;
- navigation and document metadata;
- language, direction and locale hints;
- network/document metadata where local policy permits it;
- browser state relevant to the current surface, such as focus, selection, viewport and scroll position.

No channel receives constitutional priority merely because it is easier to automate.

## 3. Evidence fusion

Navigator should combine channels rather than flatten them prematurely.

Example:

```text
semantic evidence: role=button, name="Continue"
accessibility evidence: focusable=true
geometry evidence: rect=(412, 633, 168, 48)
visual evidence: visible control with text "Continue"
```

These pieces may be fused into one perceived target.

But disagreement must remain representable:

```text
DOM: element exists
geometry: outside viewport
pixels: obscured by modal overlay
accessibility: not currently actionable
```

The correct conclusion is not simply "button exists". The observation should preserve that it is presently obscured or unavailable on the rendered surface.

## 4. Surface objects

A perceived object may originate from one or more channels.

Examples include:

- text;
- links;
- buttons;
- inputs;
- menus;
- images;
- canvas controls;
- SVG controls;
- WebGL-rendered interfaces;
- video overlays;
- modal dialogs;
- drag handles;
- custom widgets;
- controls inside frames;
- visual controls with weak or absent semantic markup.

A surface object may receive an ephemeral reference such as `e17`, but that reference belongs to a particular observation generation.

## 5. Geometry is first-class

Every actionable perceived object should carry geometry when the engine can determine it.

Geometry is tied to:

- session;
- tab;
- frame/browsing context;
- viewport size;
- device scale factor;
- scroll position;
- observation generation.

This allows semantic understanding and physical input to meet at the same object.

A client may reason semantically about `e17` and still use pointer coordinates derived from the same observation when direct semantic activation is unreliable.

## 6. Pixels are not a last resort

Screenshot perception is a normal channel, not an emergency hack.

It is essential for surfaces such as:

- canvas applications;
- graphical editors;
- image-based controls;
- custom-rendered widgets;
- WebGL applications;
- visual state not represented faithfully in DOM/accessibility data;
- occlusion and overlay detection;
- layout relationships whose meaning is spatial.

Navigator should be able to associate visual regions with semantic and geometry evidence where possible.

## 7. Text and language

Rendered text must preserve Unicode and writing direction.

Observation should retain, when available:

- original text;
- declared language;
- inferred/engine language hints;
- writing direction;
- locale-sensitive values;
- relationship between text and its visual region.

Understanding or translation may be supplied by the connected AI or an optional language component, but the Navigator must not corrupt or discard the source representation.

Text recognition from pixels may supplement structured text when structured text is absent. Pixel-derived text must remain labeled by provenance/channel so clients can distinguish it from DOM text.

## 8. Frames, windows and overlays

The perceived surface is not necessarily one DOM tree.

Navigator must represent:

- top-level page;
- same-origin and cross-origin frames to the extent the browser allows observation/input;
- popup windows;
- new tabs;
- modal overlays;
- browser-exposed permission surfaces;
- visual occlusion across layers.

Changing browsing context is a state transition, not automatically a failure.

## 9. Surface-first interaction

Interaction follows perception.

A target may be operated through:

1. semantic activation when reliable;
2. focused keyboard interaction;
3. pointer interaction against rendered geometry;
4. optional host-I/O capability for UI outside the page surface.

These are alternate actuators over the same perceived reality, not separate classes of websites.

## 10. Site policy is separate from sensory capability

A website may impose terms, authentication requirements, rate limits, anti-automation policy or other rules.

Those rules are external policy considerations. They must not be encoded as artificial sensory blindness in the Navigator architecture.

Navigator should still be able to perceive the surface presented by the browser and represent the available controls accurately. Whether a particular action is authorized is decided separately by applicable policy and context.

This preserves the architectural separation:

> **Perception answers what exists. Capability answers what can be done. Policy answers what may be done.**

Conflating these three produces a crippled browser operator.

## 11. Observation generation

A surface observation is immutable once issued.

Any material change that can invalidate targets should advance the observation generation, including where detectable:

- navigation;
- major DOM/layout mutation;
- frame replacement;
- viewport resize;
- device-scale change;
- significant scroll/coordinate-frame change;
- modal/overlay state change relevant to hit testing.

Old references may remain useful as history but must not silently retain action authority.

## 12. Success criteria

The perception subsystem is acceptable when it can demonstrate that:

1. a control can be represented from semantic evidence when available;
2. a visible control can still be represented when semantic markup is poor or absent;
3. geometry and screenshot coordinates refer to the same observation frame;
4. occlusion can be represented rather than ignored;
5. frames/popups are explicit browsing contexts;
6. Unicode and mixed-direction text survive observation intact;
7. canvas/SVG/custom-rendered surfaces are not treated as empty pages;
8. perception-channel provenance remains available to clients;
9. stale visual/semantic references lose action authority after generation changes;
10. the Core does not depend on a specific AI provider to interpret the observation.
