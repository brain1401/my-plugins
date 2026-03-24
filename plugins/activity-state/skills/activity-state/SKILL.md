---
name: activity-state
description: This skill should be used when implementing, reviewing, or debugging client components in a Next.js project with cacheComponents enabled. Covers React Activity state preservation bugs where ephemeral UI state (Dialog, Dropdown, Popover, Sheet, Modal, Tooltip open/close) persists across route navigations instead of resetting. Triggers when the user reports UI state "sticking" after navigation, or when creating components with open/close state inside cached routes.
---

# Activity State Management in Next.js with cacheComponents

## Why This Skill Exists

When `cacheComponents: true` is set in `next.config.ts`, Next.js wraps every route in React's `<Activity>` component. On client-side navigation, the previous route is **not unmounted** — instead, Activity switches to `mode="hidden"`. This means:

1. **`useState` values persist** — a Dialog that was open stays open when you navigate back
2. **DOM is preserved** (`display: none`) — DOM-based side effects (video, audio, iframe) continue running
3. **Effects (`useEffect`/`useLayoutEffect`) ARE cleaned up** on hide and recreated on show — this is your primary reset mechanism
4. **Refs remain valid** — the DOM nodes still exist in the document tree

This is fundamentally different from the traditional unmount-on-navigate behavior where all state was automatically destroyed. Components that worked fine before `cacheComponents` can break in subtle ways — a Dropdown that nobody noticed was missing cleanup suddenly stays open after back-navigation.

## Step 0: Confirm cacheComponents Is Enabled

Before applying these patterns, check `next.config.ts`:

```ts
// If this is present, all patterns in this skill apply
const nextConfig: NextConfig = {
  cacheComponents: true,
}
```

If `cacheComponents` is not enabled, routes unmount normally and this skill does not apply.

## The Core Patterns

### Pattern 1: Reset Ephemeral UI State on Route Hide

Components with open/close state (Dialog, Dropdown, Popover, Sheet, AlertDialog, Tooltip, etc.) should reset when the user navigates away. Since Activity destroys Effects on hide, use `useEffect` cleanup:

```tsx
'use client'

import { useEffect, useState } from 'react'

function MyDialog() {
  const [open, setOpen] = useState(false)

  // Cleanup runs when Activity transitions to hidden -> resets open state
  useEffect(() => {
    return () => {
      setOpen(false)
    }
  }, [])

  return (
    <Dialog open={open} onOpenChange={setOpen}>
      {/* ... */}
    </Dialog>
  )
}
```

**When to apply:** Any component where the user would expect a "fresh" state on return — overlays, menus, tooltips, confirmation dialogs, action sheets.

**When NOT to apply:** Components where persistence is desired — form inputs the user is filling out, expanded accordion sections, scroll position in a list. The whole point of Activity is to preserve these. Use judgment: "Would the user be surprised to see this still showing?"

### Pattern 2: Stop DOM-Based Side Effects on Hide

The DOM is not destroyed when Activity hides a component — it gets `display: none`. This means `<video>`, `<audio>`, and `<iframe>` elements continue running. Use `useLayoutEffect` (not `useEffect`) for immediate cleanup:

```tsx
'use client'

import { useLayoutEffect, useRef } from 'react'

function VideoPlayer() {
  const videoRef = useRef<HTMLVideoElement>(null)

  // Clean up DOM side effect: pause immediately on hidden transition
  useLayoutEffect(() => {
    return () => {
      videoRef.current?.pause()
    }
  }, [])

  return <video ref={videoRef} controls src="/video.mp4" />
}
```

Use `useLayoutEffect` here because DOM cleanup should happen synchronously before the browser paints. This prevents a brief flash of the side effect continuing.

### Pattern 3: Pathname-Driven Reset for Shared Layouts

Components in shared layouts (sidebar, header) are never hidden by Activity since they exist outside route boundaries. If these components need to react to route changes, use `usePathname()`:

```tsx
'use client'

import { useEffect, useState } from 'react'
import { usePathname } from 'next/navigation'

function HeaderSearch() {
  const pathname = usePathname()
  const [query, setQuery] = useState('')
  const [isExpanded, setIsExpanded] = useState(false)

  // Reset search UI on route change
  useEffect(() => {
    setQuery('')
    setIsExpanded(false)
  }, [pathname])

  return (/* ... */)
}
```

**When to use pathname vs Effect cleanup:**
- **Effect cleanup** — component is inside a route (Activity hides it)
- **`usePathname()`** — component is in a shared layout that persists across routes

### Pattern 4: Cleanup Subscriptions and Intervals

Global event listeners, WebSocket subscriptions, and intervals that are set up in Effects are automatically cleaned up by Activity (since Effects are destroyed on hide). But ensure your cleanup is correct:

```tsx
'use client'

import { useEffect } from 'react'

function NotificationListener() {
  useEffect(() => {
    const ws = new WebSocket('/ws/notifications')

    ws.onmessage = (event) => {
      // handle notification
    }

    // Automatically cleaned up on Activity hidden transition
    return () => {
      ws.close()
    }
  }, [])

  return (/* ... */)
}
```

If your Effect already has proper cleanup, Activity handles it automatically. The risk is Effects that _don't_ clean up — these are bugs regardless of Activity, but Activity makes them visible because the component lives longer than expected.

### Pattern 5: Custom Hook for Activity-Aware Reset

For components that need multiple states reset on route hide, extract a hook:

```tsx
'use client'

import { useEffect, useState, useRef, type Dispatch, type SetStateAction } from 'react'

/**
 * Resets state to its initial value when Activity transitions to hidden.
 * Use in cacheComponents environments to clean up ephemeral state on route exit.
 */
function useResetOnHide<T>(initialValue: T): [T, Dispatch<SetStateAction<T>>] {
  const [state, setState] = useState<T>(initialValue)

  useEffect(() => {
    return () => {
      setState(initialValue)
    }
  }, [initialValue])

  return [state, setState]
}

// Usage example
function ActionMenu() {
  const [open, setOpen] = useResetOnHide(false)
  const [selectedAction, setSelectedAction] = useResetOnHide<string | null>(null)

  return (/* ... */)
}
```

Only create this hook when you have 3+ states that need reset in multiple components. For one-off cases, inline the `useEffect` cleanup directly.

### Pattern 6: External State Management (Zustand, Jotai, Redux, etc.)

Patterns 1-5 cover `useState`-based state. But if the component's ephemeral state lives in an external store, local `setOpen(false)` won't work — you need to call the store's own reset/close action.

**Before applying cleanup to a component that uses external state, discover how the project manages state:**

1. Check the component's imports for store hooks (e.g., `useUploadStore`, `useModalStore`, `useAppStore`)
2. If found, read the store definition to find available reset/close actions
3. Use those store actions in your cleanup instead of local state setters

```tsx
'use client'

import { useEffect } from 'react'
import { usePathname } from 'next/navigation'
import { useSomeStore } from '@/store/some-store'

function SomeModal() {
  const pathname = usePathname()
  const isOpen = useSomeStore((s) => s.isOpen)
  const reset = useSomeStore((s) => s.reset)

  // Call the store's reset, not a local setOpen(false)
  useEffect(() => {
    reset()
  }, [pathname, reset])

  return (/* ... */)
}
```

Whether to use `useEffect` cleanup (Pattern 1) or `usePathname` (Pattern 3) depends on whether the component is inside a route or in a shared layout — the same rule applies regardless of local vs external state.

## Decision Flow

When implementing a client component inside a route:

```
Does this component have ephemeral UI state?
(open/close, hover, selection, expanded, etc.)
├─ Yes -> Is the state in an external store (Zustand, Jotai, Redux)?
│  ├─ Yes -> Read the store to find reset/close actions
│  │  └─ Use store actions in cleanup (Pattern 6)
│  └─ No (local useState)
│     -> Would the user be surprised if this state persists on return?
│        ├─ Yes (Dialog, Dropdown, Tooltip, etc.)
│        │  -> Pattern 1: Reset via useEffect cleanup
│        └─ No (Form input, accordion, scroll, etc.)
│           -> Do not reset (leverage Activity's default behavior)
├─ No, but DOM side effects exist (video, audio, iframe)
│  -> Pattern 2: useLayoutEffect cleanup
└─ No ephemeral state
   -> No additional work needed
```

For layout-level components (not inside a route): use Pattern 3 (`usePathname`) if needed.

## Reference Files

Read these for deeper details:

- **`references/activity-behavior.md`** — Detailed breakdown of what Activity preserves vs destroys, edge cases with portals and focus management, and testing strategies for Activity-aware components.
