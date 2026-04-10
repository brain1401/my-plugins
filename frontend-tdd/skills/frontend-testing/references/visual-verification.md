# Visual Verification Guide

Visual presentation (CSS layout, colors, animations, responsive behavior) cannot be verified by unit test assertions. This guide covers how to verify visual aspects after implementation.

## When to Use Visual Verification

Use after implementing changes to:
- CSS layout and positioning
- Spacing, margins, padding
- Colors, gradients, shadows
- Typography (font size, weight, line height)
- Animations and transitions
- Responsive breakpoints
- Hover/focus visual states
- Scroll behavior

**Important:** Visual verification supplements TDD, never replaces it. Conditional logic that drives visual changes (e.g., applying a class based on state) is testable and must follow TDD.

## With Playwright MCP

When Playwright MCP tools are available (`browser_navigate`, `browser_snapshot`, `browser_take_screenshot`, etc.), use them for systematic visual verification.

### Verification Workflow

```
1. Ensure the dev server is running (or start it)
2. Navigate to the relevant page
3. Take a snapshot to verify DOM structure
4. Take a screenshot to verify visual appearance
5. If responsive changes: resize and re-verify at breakpoints
6. If issues found: fix and repeat from step 2
```

### Tool Usage

**Navigate to the page:**
```
browser_navigate → url: "http://localhost:3000/page"
```

**Inspect DOM structure** (lightweight, text-based):
```
browser_snapshot
```
Use this to verify elements exist and are in the correct hierarchy. Faster than screenshots for structural checks.

**Capture visual state:**
```
browser_take_screenshot
```
Use this to verify visual appearance: layout, colors, spacing, typography.

**Verify responsive behavior:**
```
browser_resize → width: 375, height: 812    (mobile)
browser_take_screenshot
browser_resize → width: 768, height: 1024   (tablet)
browser_take_screenshot
browser_resize → width: 1440, height: 900   (desktop)
browser_take_screenshot
```

**Verify hover/focus states:**
```
browser_hover → selector: ".card"
browser_take_screenshot

browser_click → selector: "input[name='email']"
browser_take_screenshot
```

**Verify animations** (check start and end states):
```
browser_take_screenshot                     (before trigger)
browser_click → selector: ".trigger"
browser_wait_for → time: 500               (animation duration)
browser_take_screenshot                     (after trigger)
```

### Common Verification Patterns

**Component in isolation:**
If the project has a component playground (Storybook, Ladle, Histoire), navigate there for isolated verification:
```
browser_navigate → url: "http://localhost:6006/?path=/story/button--primary"
browser_take_screenshot
```

**Full page layout:**
```
browser_navigate → url: "http://localhost:3000/dashboard"
browser_take_screenshot
```

**Dark mode / theme switching:**
```
browser_navigate → url: "http://localhost:3000"
browser_take_screenshot                     (light mode)
browser_click → selector: "[data-theme-toggle]"
browser_take_screenshot                     (dark mode)
```

## Without Playwright MCP

When Playwright MCP tools are not available, defer visual verification to the user.

### Workflow

```
1. Complete implementation and commit
2. Report to the user:
   - What visual changes were made
   - Which pages/components are affected
   - What to look for (specific visual aspects)
   - Suggested viewport sizes for responsive checks
3. Ask the user to verify visually
```

### Reporting Template

```
Visual verification needed for [component/page]:

Changes made:
- [Description of visual change 1]
- [Description of visual change 2]

Verify at:
- http://localhost:3000/[page]

Check:
- [ ] [Specific visual aspect 1]
- [ ] [Specific visual aspect 2]
- [ ] Responsive: mobile (375px), tablet (768px), desktop (1440px)
```

## What Visual Verification Catches

| Aspect | What to Look For |
|--------|------------------|
| Layout | Elements positioned correctly, no overlaps, correct stacking |
| Spacing | Consistent margins/padding, aligned with design system |
| Typography | Correct font, size, weight, line height, truncation |
| Color | Correct palette, sufficient contrast, theme consistency |
| Responsive | No overflow, readable text, touch targets adequate at mobile |
| Animation | Smooth transitions, correct timing, no janky reflow |
| States | Hover, focus, active, disabled states visually distinct |

## Mixed Changes: TDD + Visual

For changes that involve both testable logic and visual presentation:

```
1. TDD the logic first:
   - Conditional class application → assert class presence
   - Theme state management → assert state transitions
   - Responsive breakpoint hooks → assert returned values

2. Visual verify the presentation:
   - How the applied classes look
   - How the theme renders visually
   - How layouts respond to viewport changes
```

Example: A dark mode toggle has both testable and visual aspects.

**Testable (TDD):**
```tsx
test('applies dark class to document when dark mode is enabled', async () => {
  render(<ThemeToggle />);
  await userEvent.click(screen.getByRole('switch', { name: /dark mode/i }));
  expect(document.documentElement).toHaveClass('dark');
});
```

**Visual (Playwright):**
```
Navigate to page → toggle dark mode → screenshot → verify colors changed
```
