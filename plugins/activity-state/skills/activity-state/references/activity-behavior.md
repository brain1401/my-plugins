# Activity Behavior Deep Dive

## What Activity Preserves vs Destroys

| Aspect | On hidden transition | On visible restoration |
|--------|---------------------|----------------------|
| `useState` / `useReducer` | **Preserved** | Previous value intact |
| `useRef` | **Preserved** | Previous value intact |
| `useEffect` | **Cleanup runs** (destroy) | **Recreated** (setup re-runs) |
| `useLayoutEffect` | **Cleanup runs** (destroy) | **Recreated** (setup re-runs) |
| DOM nodes | **Preserved** (`display: none`) | `display: none` removed |
| Context values | **Preserved** | Previous value intact |
| Event listeners (via Effect) | Removed by Effect cleanup | Re-registered by Effect setup |
| Event listeners (inline JSX) | Remain on DOM but not clickable due to `display: none` | Work normally |

## Edge Cases

### Portals

Content rendered via Portals (e.g., Dialog overlays) is mounted in DOM outside the Activity boundary. When Activity becomes hidden, the portal's DOM may NOT get `display: none` applied.

> **You must reset the open state via Effect cleanup.** Otherwise, the Dialog overlay will remain visible on top of other routes.

shadcn's Dialog, AlertDialog, Dropdown, Sheet, etc. all use Radix Portal internally, so this applies to all of them.

```tsx
// shadcn Dialog usage — cleanup is mandatory
function DeleteConfirmDialog() {
  const [open, setOpen] = useState(false)

  useEffect(() => {
    return () => setOpen(false)
  }, [])

  return (
    <AlertDialog open={open} onOpenChange={setOpen}>
      <AlertDialogTrigger asChild>
        <Button variant="destructive">Delete</Button>
      </AlertDialogTrigger>
      <AlertDialogContent>
        {/* ... */}
      </AlertDialogContent>
    </AlertDialog>
  )
}
```

### Focus Management

When transitioning to hidden, the focused element gets `display: none` and the browser moves focus to `<body>`. React does not automatically restore focus on visible restoration.

> For cases where focus restoration is needed (e.g., complex forms), handle it manually in `useEffect`:

```tsx
function SearchInput() {
  const inputRef = useRef<HTMLInputElement>(null)
  const [shouldFocus, setShouldFocus] = useState(false)

  useEffect(() => {
    // On visible restoration: restore focus if it was previously active
    if (shouldFocus) {
      inputRef.current?.focus()
    }

    return () => {
      // On hidden transition: save current focus state
      setShouldFocus(document.activeElement === inputRef.current)
    }
  }, [shouldFocus])

  return <input ref={inputRef} type="text" />
}
```

### Scroll Position

When Activity is hidden, `display: none` is applied, so the browser automatically preserves scroll position. No additional handling is needed.

However, when using virtualized lists (react-window, tanstack-virtual, etc.), the container size becomes 0 while hidden, which can break virtualization calculations. A recalculation may be needed on visible restoration.

### Timers (setTimeout, setInterval)

Timers created inside Effects should be cleaned up in Effect cleanup (this is good practice regardless of Activity):

```tsx
useEffect(() => {
  const timer = setInterval(() => {
    // polling logic
  }, 5000)

  return () => clearInterval(timer)  // Automatically cleaned up on hidden transition
}, [])
```

Timers created outside Effects (e.g., inside event handlers) are NOT cleaned up by Activity. In this case, manual cleanup via `useEffect` cleanup is required.

### Third-Party Libraries

Some libraries may not be aware of Activity behavior:

- **Map libraries** (Google Maps, Mapbox): Container size becomes 0 when hidden. On visible restoration, you may need to fire a `resize` event or call `invalidateSize()`.
- **Chart libraries** (Chart.js, Recharts): Similarly need container size recalculation.
- **Animation libraries** (Framer Motion): AnimatePresence exit animations may conflict with Activity hidden transitions.

When integrating these libraries, verify whether reinitialization is needed on visible restoration.

## Testing Activity-Aware Components

To test Activity behavior, wrap the component in `<Activity>` and toggle its mode:

```tsx
import { useState } from 'react'
import { Activity } from 'react'
import { render, act, screen, fireEvent } from '@testing-library/react'

test('Dialog should close on Activity hidden transition', () => {
  let setMode: (mode: 'visible' | 'hidden') => void

  function Wrapper() {
    const [mode, _setMode] = useState<'visible' | 'hidden'>('visible')
    setMode = _setMode
    return (
      <Activity mode={mode}>
        <MyDialog />
      </Activity>
    )
  }

  const { queryByRole } = render(<Wrapper />)

  // Open the dialog
  fireEvent.click(screen.getByText('Open'))
  expect(queryByRole('dialog')).toBeInTheDocument()

  // Transition Activity to hidden
  act(() => setMode('hidden'))

  // Restore Activity to visible
  act(() => setMode('visible'))

  // Dialog should be closed
  expect(queryByRole('dialog')).not.toBeInTheDocument()
})
```

Enabling `<StrictMode>` causes Effect cleanup/setup to run twice, helping discover Effects with improper cleanup early. This has always been good practice, but it's especially important in Activity-enabled environments.
