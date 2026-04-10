---
name: frontend-testing
description: This skill should be used when implementing or modifying frontend code (components, pages, styles, templates), when the user asks to "test a component", "add frontend tests", "write component tests", "build a form", "create a page", "implement a component", or when a plan includes frontend implementation tasks. Complements superpowers:test-driven-development with frontend-specific TDD patterns, testability classification, and visual verification guidance.
---

# Frontend Testing

Frontend code is subject to TDD. Claiming frontend work is "visual, so it can't be tested" is rationalization. Most frontend behavior is assertable. Only pure visual presentation (spacing, color, animation) falls outside unit testing.

This skill complements `superpowers:test-driven-development`. Follow that skill's RED-GREEN-REFACTOR cycle. This skill specifies **what** to test and **how** for frontend work.

## The Classification Rule

Before implementing any frontend task, classify each change:

| Category | Action | Examples |
|----------|--------|----------|
| **Testable behavior** | TDD required (RED-GREEN-REFACTOR) | Component output, events, state, forms, a11y, routing |
| **Visual presentation** | Verify after implementation | CSS layout, color, animation, responsive breakpoints |
| **Mixed** | TDD for logic, visual verify for appearance | Conditional class application, theme switching |

When in doubt, it is testable. The "visual only" category is narrow: pure CSS properties with no conditional logic.

## Testable Behavior (TDD Required)

Apply strict RED-GREEN-REFACTOR for all of the following. No exceptions. For complete code examples of each category, see `references/testing-patterns.md`.

### 1. Component Rendering

Assert that components produce the correct DOM given specific props and state. Use semantic queries (`getByRole`, `getByText`, `getByLabelText`) over test IDs.

### 2. Event Handlers

Assert that user interactions trigger the correct callbacks or state changes. Use `userEvent` (not `fireEvent`) for realistic interaction simulation.

### 3. Conditional Rendering

Assert both branches: element present when condition is true, absent when false. Use `queryBy*` (returns null) for absence checks, not `getBy*` (throws).

### 4. Async and API States

Assert all three states: loading, success, error. Use `findBy*` queries for async assertions. Mock at the network level (MSW) rather than mocking fetch/axios directly.

### 5. Form Validation

Assert validation messages appear for invalid input and disappear for valid input. Test submission with valid and invalid data.

### 6. Accessibility

Assert ARIA attributes, roles, keyboard navigation, and focus management. Use `getByRole` as the primary query method.

### 7. Routing and Navigation

Assert that navigation events produce the correct route changes and that route parameters drive correct rendering.

## Visual Presentation (Post-Implementation Verification)

These aspects cannot be verified by unit test assertions. Verify after implementation using browser tools.

- CSS spacing, alignment, and positioning
- Color and typography rendering
- Animation and transition effects
- Responsive layout at different breakpoints
- Hover and focus visual styles
- Scroll behavior
- Cross-browser rendering differences

For detailed Playwright MCP verification workflow, consult `references/visual-verification.md`.

## Testing Tool Selection

### Recommended Stack

- **Test runner**: Vitest (fast, native ESM, compatible with Jest API)
- **DOM environment**: jsdom or happy-dom
- **Component queries**: @testing-library for the relevant framework
- **User interaction**: @testing-library/user-event
- **API mocking**: MSW (Mock Service Worker)
- **Visual verification**: Playwright MCP tools (if available)

### Framework Adapters

All frameworks share the same Testing Library query API (`getByRole`, `findByText`, etc.). The only difference is the render function:

| Framework | Package | Render |
|-----------|---------|--------|
| React | @testing-library/react | `render(<Component />)` |
| Vue | @testing-library/vue | `render(Component, { props })` |
| Svelte | @testing-library/svelte | `render(Component, { props })` |
| Angular | @testing-library/angular | `render(Component, { componentProperties })` |

Detect the project's framework from `package.json` and use the corresponding adapter. When no testing library is set up, setting it up is the first task before any implementation.

## Frontend TDD Workflow

For each frontend task in a plan:

```
1. Classify changes (testable / visual / mixed)
2. For testable behavior:
   a. Write failing test (RED)
   b. Run test, confirm it fails for the right reason
   c. Write minimal component code (GREEN)
   d. Run test, confirm it passes
   e. Refactor if needed, keep tests green
   f. Commit
3. For visual presentation:
   a. Implement CSS/styling
   b. Verify with Playwright MCP (see references/visual-verification.md)
   c. Commit
4. For mixed changes:
   a. TDD the logic (steps 2a-2f)
   b. Then implement visual styling (step 3)
```

## Anti-Rationalizations

| Excuse | Reality |
|--------|---------|
| "It's just a simple component" | Simple components break. Test takes 30 seconds. |
| "It's only CSS changes" | Test the conditional logic that drives class application. Pure CSS is visual-only; conditional classes are testable. |
| "No testing library is set up" | Set it up as the first task. Not optional. |
| "I'll verify it visually" | Visual verification supplements tests, never replaces them. |
| "The component is too coupled to test" | Design signal. Refactor to accept props/callbacks. |
| "Frontend testing is flaky" | Flaky tests mean bad test design, not untestable code. Use `findBy*` for async, avoid timing hacks. |
| "This page is mostly layout" | Layout may be visual-only, but conditional rendering within it is testable. Classify each piece. |
| "I tested it in the browser manually" | Manual testing is not recorded, not repeatable, not regression-proof. |

## Plan Generation Guidance

When writing implementation plans that include frontend tasks, each task MUST include:

1. **Test file path** in the Files section
2. **Explicit failing test code** in Step 1
3. **Classification** of what is testable vs visual-only

A plan that puts "write tests" at the end or omits test steps for frontend tasks is not following TDD. Restructure it.

## Reference Files

For detailed content, consult:

- **`references/testing-patterns.md`** — Complete code examples for each testable category (rendering, events, conditional, async, forms, accessibility). React-centered with framework-agnostic principles.
- **`references/visual-verification.md`** — Playwright MCP tool usage for visual verification. Includes dual-mode guidance (with and without Playwright MCP).
