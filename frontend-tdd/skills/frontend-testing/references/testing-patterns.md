# Frontend Testing Patterns

Complete code examples for each testable frontend category. Examples use React with @testing-library/react, but the query API (`getByRole`, `findByText`, `queryByRole`, etc.) is identical across all Testing Library adapters.

## Setup

```typescript
import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { vi, describe, test, expect } from 'vitest';
```

For async/API tests with MSW:

```typescript
import { http, HttpResponse } from 'msw';
import { setupServer } from 'msw/node';

const server = setupServer();
beforeAll(() => server.listen());
afterEach(() => server.resetHandlers());
afterAll(() => server.close());
```

## 1. Component Rendering

Assert that components produce the correct DOM structure for given props.

**Semantic queries over test IDs.** Prefer `getByRole`, `getByText`, `getByLabelText`. Use `data-testid` only as a last resort.

```tsx
test('renders product card with name and price', () => {
  render(<ProductCard name="Wireless Mouse" price={29.99} />);

  expect(screen.getByRole('heading', { name: 'Wireless Mouse' })).toBeInTheDocument();
  expect(screen.getByText('$29.99')).toBeInTheDocument();
});

test('renders empty state when no items provided', () => {
  render(<ItemList items={[]} />);

  expect(screen.getByText(/no items/i)).toBeInTheDocument();
  expect(screen.queryByRole('listitem')).not.toBeInTheDocument();
});

test('renders list items from data', () => {
  const items = [{ id: '1', name: 'Alpha' }, { id: '2', name: 'Beta' }];
  render(<ItemList items={items} />);

  const listItems = screen.getAllByRole('listitem');
  expect(listItems).toHaveLength(2);
  expect(listItems[0]).toHaveTextContent('Alpha');
});
```

## 2. Event Handlers

Use `userEvent` for realistic browser-like interaction simulation. Always `await` userEvent calls.

```tsx
test('calls onAdd when add-to-cart button is clicked', async () => {
  const onAdd = vi.fn();
  render(<ProductCard product={mockProduct} onAdd={onAdd} />);

  await userEvent.click(screen.getByRole('button', { name: /add to cart/i }));

  expect(onAdd).toHaveBeenCalledOnce();
  expect(onAdd).toHaveBeenCalledWith(mockProduct.id);
});

test('increments counter on plus button click', async () => {
  render(<Counter initialValue={0} />);

  await userEvent.click(screen.getByRole('button', { name: '+' }));

  expect(screen.getByText('1')).toBeInTheDocument();
});

test('calls onSearch after typing and pressing Enter', async () => {
  const onSearch = vi.fn();
  render(<SearchBar onSearch={onSearch} />);

  await userEvent.type(screen.getByRole('searchbox'), 'test query{Enter}');

  expect(onSearch).toHaveBeenCalledWith('test query');
});
```

## 3. Conditional Rendering

Assert both presence and absence. Use `queryBy*` (returns null) for absence, `getBy*` (throws) for presence.

```tsx
test('shows admin controls for admin users', () => {
  render(<Dashboard user={{ role: 'admin' }} />);
  expect(screen.getByRole('region', { name: /admin/i })).toBeInTheDocument();
});

test('hides admin controls for regular users', () => {
  render(<Dashboard user={{ role: 'user' }} />);
  expect(screen.queryByRole('region', { name: /admin/i })).not.toBeInTheDocument();
});

test('shows discount badge when item is on sale', () => {
  render(<ProductCard product={{ ...mockProduct, onSale: true, discount: 20 }} />);
  expect(screen.getByText('20% OFF')).toBeInTheDocument();
});

test('hides discount badge when item is not on sale', () => {
  render(<ProductCard product={{ ...mockProduct, onSale: false }} />);
  expect(screen.queryByText(/% OFF/)).not.toBeInTheDocument();
});
```

## 4. Async and API States

Test all three states: loading, success, error. Use `findBy*` for async (waits with timeout). Mock at network level with MSW.

```tsx
test('shows loading indicator while fetching users', () => {
  render(<UserList />);
  expect(screen.getByRole('progressbar')).toBeInTheDocument();
});

test('renders user list after successful fetch', async () => {
  server.use(
    http.get('/api/users', () =>
      HttpResponse.json([
        { id: '1', name: 'Alice' },
        { id: '2', name: 'Bob' },
      ])
    )
  );

  render(<UserList />);

  expect(await screen.findByText('Alice')).toBeInTheDocument();
  expect(screen.getByText('Bob')).toBeInTheDocument();
  expect(screen.queryByRole('progressbar')).not.toBeInTheDocument();
});

test('shows error message when fetch fails', async () => {
  server.use(
    http.get('/api/users', () => HttpResponse.error())
  );

  render(<UserList />);

  expect(await screen.findByText(/failed to load/i)).toBeInTheDocument();
  expect(screen.queryByRole('progressbar')).not.toBeInTheDocument();
});

test('refetches data when retry button is clicked', async () => {
  let callCount = 0;
  server.use(
    http.get('/api/users', () => {
      callCount++;
      if (callCount === 1) return HttpResponse.error();
      return HttpResponse.json([{ id: '1', name: 'Alice' }]);
    })
  );

  render(<UserList />);
  await screen.findByText(/failed to load/i);

  await userEvent.click(screen.getByRole('button', { name: /retry/i }));

  expect(await screen.findByText('Alice')).toBeInTheDocument();
});
```

## 5. Form Validation

Test validation messages, submission behavior, and field interactions.

```tsx
test('shows required error when submitting empty form', async () => {
  render(<SignupForm />);

  await userEvent.click(screen.getByRole('button', { name: /sign up/i }));

  expect(screen.getByText(/email is required/i)).toBeInTheDocument();
  expect(screen.getByText(/password is required/i)).toBeInTheDocument();
});

test('shows format error for invalid email', async () => {
  render(<SignupForm />);

  await userEvent.type(screen.getByLabelText(/email/i), 'not-an-email');
  await userEvent.click(screen.getByRole('button', { name: /sign up/i }));

  expect(screen.getByText(/valid email/i)).toBeInTheDocument();
});

test('clears error when user corrects input', async () => {
  render(<SignupForm />);

  await userEvent.type(screen.getByLabelText(/email/i), 'bad');
  await userEvent.click(screen.getByRole('button', { name: /sign up/i }));
  expect(screen.getByText(/valid email/i)).toBeInTheDocument();

  await userEvent.clear(screen.getByLabelText(/email/i));
  await userEvent.type(screen.getByLabelText(/email/i), 'valid@example.com');
  await userEvent.click(screen.getByRole('button', { name: /sign up/i }));
  expect(screen.queryByText(/valid email/i)).not.toBeInTheDocument();
});

test('calls onSubmit with form data for valid submission', async () => {
  const onSubmit = vi.fn();
  render(<SignupForm onSubmit={onSubmit} />);

  await userEvent.type(screen.getByLabelText(/email/i), 'user@example.com');
  await userEvent.type(screen.getByLabelText(/password/i), 'secure123');
  await userEvent.click(screen.getByRole('button', { name: /sign up/i }));

  expect(onSubmit).toHaveBeenCalledWith({
    email: 'user@example.com',
    password: 'secure123',
  });
});

test('disables submit button while submitting', async () => {
  render(<SignupForm onSubmit={() => new Promise(() => {})} />);

  await userEvent.type(screen.getByLabelText(/email/i), 'user@example.com');
  await userEvent.type(screen.getByLabelText(/password/i), 'secure123');
  await userEvent.click(screen.getByRole('button', { name: /sign up/i }));

  expect(screen.getByRole('button', { name: /sign up/i })).toBeDisabled();
});
```

## 6. Accessibility

Test ARIA attributes, roles, keyboard navigation, and focus management.

```tsx
test('modal has correct ARIA attributes', () => {
  render(<Modal title="Confirm Action" open={true} />);

  const dialog = screen.getByRole('dialog');
  expect(dialog).toHaveAttribute('aria-labelledby');
  expect(dialog).toHaveAttribute('aria-modal', 'true');

  const title = screen.getByRole('heading', { name: 'Confirm Action' });
  expect(dialog.getAttribute('aria-labelledby')).toBe(title.id);
});

test('modal traps focus within dialog', async () => {
  render(<Modal open={true} title="Test"><button>First</button><button>Last</button></Modal>);

  const buttons = screen.getAllByRole('button');
  buttons[buttons.length - 1].focus();

  await userEvent.tab();

  expect(buttons[0]).toHaveFocus();
});

test('dropdown opens with Enter and closes with Escape', async () => {
  render(<Dropdown options={['A', 'B', 'C']} />);

  const trigger = screen.getByRole('combobox');
  trigger.focus();

  await userEvent.keyboard('{Enter}');
  expect(screen.getByRole('listbox')).toBeInTheDocument();

  await userEvent.keyboard('{Escape}');
  expect(screen.queryByRole('listbox')).not.toBeInTheDocument();
  expect(trigger).toHaveFocus();
});

test('form fields have associated labels', () => {
  render(<ContactForm />);

  expect(screen.getByLabelText(/name/i)).toBeInTheDocument();
  expect(screen.getByLabelText(/email/i)).toBeInTheDocument();
  expect(screen.getByLabelText(/message/i)).toBeInTheDocument();
});
```

## 7. Routing and Navigation

Test route-driven rendering and navigation events. Wrap components in a test router.

```tsx
import { MemoryRouter, Route, Routes } from 'react-router-dom';

function renderWithRouter(ui: React.ReactElement, { route = '/' } = {}) {
  return render(
    <MemoryRouter initialEntries={[route]}>
      {ui}
    </MemoryRouter>
  );
}

test('renders user profile for given route param', () => {
  renderWithRouter(
    <Routes>
      <Route path="/user/:id" element={<UserProfile />} />
    </Routes>,
    { route: '/user/42' }
  );

  expect(screen.getByText(/user #42/i)).toBeInTheDocument();
});

test('navigates to detail page on item click', async () => {
  renderWithRouter(
    <Routes>
      <Route path="/" element={<ItemList items={[{ id: '1', name: 'Alpha' }]} />} />
      <Route path="/item/:id" element={<ItemDetail />} />
    </Routes>
  );

  await userEvent.click(screen.getByText('Alpha'));

  expect(screen.getByText(/item detail/i)).toBeInTheDocument();
});

test('shows 404 page for unknown routes', () => {
  renderWithRouter(
    <Routes>
      <Route path="/" element={<Home />} />
      <Route path="*" element={<NotFound />} />
    </Routes>,
    { route: '/nonexistent' }
  );

  expect(screen.getByText(/page not found/i)).toBeInTheDocument();
});
```

## Key Principles

1. **One behavior per test.** "and" in the test name means split it.
2. **Semantic queries first.** `getByRole` > `getByLabelText` > `getByText` > `getByTestId`.
3. **userEvent over fireEvent.** `userEvent` simulates real browser behavior (focus, blur, keydown sequences).
4. **findBy for async.** Never use `waitFor` + `getBy` when `findBy` works.
5. **Mock at the boundary.** Use MSW for network, not `vi.mock('axios')`.
6. **Test behavior, not implementation.** Assert what the user sees, not internal state or DOM structure details.
