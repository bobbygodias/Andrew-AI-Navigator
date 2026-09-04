# Andrew AI Navigator — Universal Input

## Why this exists

A Web operator that can only read DOM structure is not a complete browser operator.

Many ordinary tasks depend on human-style interaction: moving a pointer, clicking a visible control, focusing a field, scrolling, dragging, pressing Tab or Enter, using keyboard shortcuts, or interacting with a control that is poorly represented in the DOM/accessibility tree.

Navigator therefore treats mouse/pointer and keyboard input as first-class capabilities.

## Design principle

> Prefer semantics when semantics are reliable. Fall back to human-operable input when they are not.

Navigator must not confuse "no convenient selector" with "cannot operate this page".

## Interaction ladder

### 1. Semantic actions

Use structured element references when possible.

Examples:

```text
click(e17)
fill(e18, "query")
focus(e18)
select(e23, "option")
```

Benefits:

- easiest to audit;
- robust against viewport movement;
- meaningful to policy;
- friendly to accessibility metadata.

### 2. Browser-surface pointer

Required primitives:

```text
move(x, y)
move_relative(dx, dy)
hover(x, y)
click(x, y, button=left)
double_click(x, y, button=left)
button_down(button)
button_up(button)
wheel(dx, dy)
drag(x1, y1, x2, y2)
```

Coordinates belong to a specific tab viewport and observation generation.

Every screenshot observation records enough geometry to interpret coordinates safely:

- viewport width;
- viewport height;
- device scale factor where relevant;
- scroll position where relevant;
- observation generation ID.

If the page navigates, resizes, changes scale, or invalidates the observation, clients should obtain a fresh screenshot/observation before relying on old coordinates.

### 3. Browser-surface keyboard

Required primitives:

```text
key_down(key)
key_up(key)
press(key)
chord([Ctrl, L])
type_text("hello")
```

Key support includes ordinary characters and, where the engine supports them:

- Enter;
- Tab;
- Escape;
- Backspace;
- Delete;
- Home / End;
- PageUp / PageDown;
- arrow keys;
- Ctrl / Alt / Shift / Meta;
- function keys.

`type_text()` is distinct from physical key events. Text insertion communicates intended characters; key events model navigation, shortcuts, modifiers and special behavior.

## Login capability

A simple login flow must be possible without inventing a site-specific adapter.

A generic sequence may be:

1. open login page;
2. observe page and/or screenshot;
3. focus username field semantically or by pointer;
4. type username;
5. focus password field;
6. type password from runtime secret input;
7. press Enter or click the visible submit control;
8. observe resulting state.

Passwords and other secrets are runtime inputs. They are never committed to Git and must not appear in logs or returned observations merely because Navigator typed them.

Navigator does not claim that pointer/keyboard input bypasses CAPTCHA, MFA, passkeys, anti-bot systems, or user-consent requirements. Those are separate workflow constraints.

## 4. Optional host desktop I/O

Browser engines do not own every visible interaction. Native file pickers, permission dialogs, certain credential surfaces, external authentication windows and browser chrome may require host-level input.

A future host-I/O package may therefore expose bounded primitives such as:

- locate/list permitted windows;
- focus a permitted window;
- host pointer movement/click;
- host keyboard input;
- bounded screenshot capture.

This package must be optional, local and policy-gated. It must not become an arbitrary shell/command-execution backdoor.

## Security invariants

1. Capability is not authorization.
2. Web content cannot increase its own input authority.
3. Sensitive typed values are redacted from audit logs.
4. Coordinate actions are scoped to a tab and observation generation.
5. Host desktop I/O is disabled unless explicitly enabled locally.
6. Arbitrary JavaScript and arbitrary shell execution are not substitutes for proper input primitives.

## Engine contract implication

Every browser engine claiming full interactive support should report which capabilities it implements, for example:

```text
semantic_click: true
semantic_fill: true
pointer_move: true
pointer_click: true
pointer_drag: true
wheel: true
keyboard_keys: true
keyboard_text: true
host_io: false
```

This lets the Core reason about what an engine can actually do instead of assuming all browser drivers expose equivalent behavior.
