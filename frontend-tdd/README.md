# frontend-tdd

Frontend-specific TDD guidance plugin for Claude Code. Complements [Superpowers](https://github.com/obra/superpowers)' `test-driven-development` skill by filling the frontend testing gap.

## Problem

Superpowers enforces strict TDD but provides no guidance for frontend work. This causes agents to systematically skip tests for component logic, event handlers, form validation, and other testable frontend behavior.

## What This Plugin Provides

**`frontend-testing` skill** — Activates when implementing or modifying frontend code. Provides:

- Classification of what must be tested (TDD) vs. what requires visual verification
- Testing tool selection (Vitest, Testing Library, MSW)
- Anti-rationalizations preventing agents from skipping frontend tests
- Plan generation guidance ensuring frontend tasks include test steps

**Reference files:**

- `testing-patterns.md` — Complete code examples for 7 testable categories (rendering, events, conditional, async, forms, accessibility, routing)
- `visual-verification.md` — Playwright MCP visual verification workflow with fallback for environments without Playwright

## Installation

```bash
claude --plugin-dir /path/to/frontend-tdd
```

## Requirements

- Works standalone, but designed to complement Superpowers' TDD skill
- Playwright MCP plugin (optional, for visual verification)
