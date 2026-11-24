# 07 — React, TypeScript & Frontend

> Anchor: You built React + Angular observability dashboards (real-time microservice health). Speak from real dashboard-building experience.

> 📘 **How to read this file:** Every answer now has three layers —
> **(1) Simple idea** (a plain-English one-liner or analogy so you "get it"),
> **(2) Deeper explanation** (the interview-ready detail), and
> **(3) Example / talking point** where useful. Read the Simple idea first; if that clicks, the rest will make sense.

---

## A. React Fundamentals

### Q1. What is React? Key features?

**🟢 Simple idea:** React is a tool for building website screens out of small reusable blocks (called *components*). You tell it "here's my data," and it automatically draws and updates the screen for you — you never have to manually change the page yourself.

**🔵 Deeper explanation:**
Think of building a house with LEGO. Each LEGO piece is a **component** (a button, a card, a navbar). You snap small pieces together to make big pieces, and big pieces together to make the whole house (the app).

React is **declarative**, which is the single most important word here. Let me contrast two ways of building UI:
- **Imperative (the old way):** "Find the counter element. Read its number. Add 1. Now update the text. Now change the color." — You give step-by-step DOM instructions.
- **Declarative (React's way):** "The counter should show `count`. When `count` is over 10, make it red." — You describe the *end result* for any given data, and React figures out the steps to get there.

The magic: **you only manage the data (state), and React keeps the screen in sync automatically.** You almost never touch the actual webpage (the DOM) directly.

Key features to name in an interview:
- **Virtual DOM** — a fast in-memory copy of the screen that lets React update only what changed (explained in Q2).
- **Component-based** — reusable building blocks.
- **One-way data flow** — data flows *downward* from parent to child, so it's easy to trace where data comes from (like water flowing downhill — predictable).
- **JSX** — write HTML-looking code inside JavaScript.
- **Hooks** — special functions (like `useState`) that add features to components.
- **Huge ecosystem** — ready-made libraries for routing, state, etc.

---

### Q2. What is the Virtual DOM and reconciliation?

**🟢 Simple idea:** The real webpage (DOM) is slow to change. So React keeps a lightweight "draft copy" in memory. When your data changes, React makes a *new* draft, compares it to the old draft to spot the exact differences, and then updates only those few spots on the real page — instead of redrawing everything.

**🔵 Deeper explanation:**
Imagine you're editing a printed document. You could reprint all 100 pages every time you fix a typo (slow, wasteful) — that's like updating the whole real DOM. Or you could compare the new version to the old one, find the 3 words that changed, and only reprint those (fast) — that's React.

Step by step:
1. Your component's **state changes** (e.g., a counter goes from 0 → 1).
2. React builds a **brand-new Virtual DOM tree** describing how the screen *should* now look.
3. **Reconciliation** happens — React runs a **diffing algorithm** comparing the new tree to the previous one to find exactly what's different.
4. React applies the **minimal set of changes** to the real DOM (maybe just changing one number).

**Keys** matter here (see Q7): when React diffs a *list* of items, it uses keys as name tags to know "this is the same item as before, just moved" versus "this is a brand-new item."

**💬 One-liner for interview:** "The Virtual DOM lets React batch and minimize expensive real-DOM operations by diffing an in-memory copy — that's the core of why React is fast."

---

### Q3. Functional vs class components?

**🟢 Simple idea:** These are just two ways to write a component. **Functional components** (a simple function) are the modern, cleaner way everyone uses now. **Class components** are the older way you'll only see in old code.

**🔵 Deeper explanation:**

**Functional component** — literally a JavaScript function that receives `props` (inputs) and returns JSX (what to show):
```jsx
function Welcome({ name }) {
  return <h1>Hello {name}</h1>;
}
```
By adding **hooks** (`useState`, `useEffect`), these functions can do everything the old classes did, with less code.

**Class component** — the older style using an ES6 `class`:
```jsx
class Welcome extends React.Component {
  render() { return <h1>Hello {this.props.name}</h1>; }
}
```
Classes store data in `this.state` and use **lifecycle methods** (`componentDidMount` runs after first render, `componentWillUnmount` runs before removal).

**Why the industry switched to functions + hooks:**
- Classes made it **hard to reuse logic** — sharing stateful logic between components was awkward (needed patterns like HOCs).
- Classes **scattered related code** — e.g., setting up a subscription in `componentDidMount` and cleaning it up in `componentWillUnmount`, two far-apart methods. Hooks let you keep that setup + cleanup together in one `useEffect`.
- `this` keyword in classes caused many bugs.

**💬 Interview line:** "New code should use functional components with hooks; class components are legacy but still supported."

---

### Q4. What is JSX?

**🟢 Simple idea:** JSX lets you write HTML-looking code *inside* your JavaScript. It's not real HTML and browsers can't read it directly — a tool (Babel) translates it into normal JavaScript before it runs.

**🔵 Deeper explanation:**
This is JSX:
```jsx
const element = <div className="card">{title}</div>;
```
Behind the scenes, Babel converts that into a plain JavaScript function call:
```js
const element = React.createElement("div", { className: "card" }, title);
```
Both do the same thing, but the JSX version is *far* easier to read. JSX is called **"syntactic sugar"** — a nicer-looking shortcut for something that already exists.

The powerful part: because JSX is "just JavaScript," you can drop real JavaScript expressions inside curly braces `{}`:
```jsx
<div>
  {isLoggedIn ? "Welcome!" : "Please log in"}   {/* conditionals */}
  {users.map(u => <li key={u.id}>{u.name}</li>)}  {/* loops */}
</div>
```
Note: it's `className` instead of `class` (because `class` is a reserved word in JavaScript).

---

### Q5. Props vs state?

**🟢 Simple idea:**
- **Props** = data **given to** a component by its parent (read-only, like arguments you pass to a function). The component cannot change them.
- **State** = data a component **owns and can change** itself over time. Changing state redraws the screen.

**🔵 Deeper explanation:**
Analogy: Think of a component as a **coffee machine**.
- **Props** are the settings you (the parent) hand it: "make a large latte." The machine can't override your order — it just uses it.
- **State** is what the machine tracks internally: "currently heating," "water level." It manages and updates this itself.

```jsx
function Counter({ startAt }) {          // startAt is a PROP (from parent)
  const [count, setCount] = useState(startAt);  // count is STATE (owned here)
  return <button onClick={() => setCount(count + 1)}>{count}</button>;
}
```

Key rules:
- **Props flow down** — parent → child. Children never modify props.
- **State changes trigger a re-render** — when you call the setter (`setCount`), React redraws the component with the new value.
- **To let a child affect the parent**, the parent passes a *function* (callback) down as a prop. The child calls it; the parent updates its own state. This keeps state as the single "source of truth."

**💬 Mental model:** "Props are what a component is *given*; state is what it *remembers and controls*."

---

### Q6. Controlled vs uncontrolled components?

**🟢 Simple idea:** This is about **who is in charge of what a form input shows**.
- **Controlled** = React state controls the input's value (React is the boss).
- **Uncontrolled** = the browser/DOM holds the value, and you only grab it when you need it (like an old-school HTML form).

**🔵 Deeper explanation:**

**Controlled component** — the input's value is tied to state, and every keystroke updates that state:
```jsx
const [name, setName] = useState("");
<input value={name} onChange={e => setName(e.target.value)} />
```
Because React always knows the current value, doing **validation, formatting, or conditional logic** is easy. The downside: it **re-renders on every keystroke** (usually fine, but can matter for huge forms).

**Uncontrolled component** — the DOM keeps the value; you read it only when needed using a **ref**:
```jsx
const inputRef = useRef();
<input ref={inputRef} />
<button onClick={() => alert(inputRef.current.value)}>Submit</button>
```
Less code, fewer re-renders, but React isn't watching the value continuously.

**💬 Best practice:** Use **controlled** for most cases (predictable + easy validation). For large/performance-heavy forms, use libraries like **react-hook-form** which use refs (uncontrolled) under the hood for speed.

---

### Q7. What are keys and why important?

**🟢 Simple idea:** When you show a list, each item needs a unique **key** (like a name tag). It helps React tell items apart between updates so it knows which ones were added, removed, or just moved — and updates the screen correctly.

**🔵 Deeper explanation:**
```jsx
{users.map(user => <Row key={user.id} name={user.name} />)}
```
During reconciliation (Q2), React compares the old list to the new list. Keys are how it matches them up. Without stable keys, React can't tell "did item #2 get deleted, or did everything shift up by one?"

**⚠️ The famous gotcha — don't use the array index as a key** for lists that can change (reorder, insert, delete):
```jsx
{items.map((item, index) => <Row key={index} />)}  // ❌ risky
```
Why it's buggy: if you delete the first item, all the indexes shift. React thinks item at index 0 is "the same item" (it kept the key 0), so it **reuses the wrong DOM node**. A classic symptom: you type into a text box on one row, delete a different row, and suddenly your typed text appears on the wrong row.

**✅ Fix:** always use a **stable, unique ID from your data** (`user.id`, a database ID, etc.).

---

## B. Hooks

### Q8. Explain the core hooks.

**🟢 Simple idea:** Hooks are special functions starting with `use` that give your simple function-components superpowers — like remembering data, running code after rendering, or sharing data across the app.

**🔵 Deeper explanation of each:**

- **`useState`** — gives a component **memory** (local state). Returns `[value, setter]`. Calling the setter redraws the component.
  ```jsx
  const [count, setCount] = useState(0);
  ```

- **`useEffect`** — runs **side effects** *after* the screen is drawn. "Side effect" = anything beyond just rendering: fetching data, timers, subscriptions. It can return a **cleanup function** and takes a **dependency array** to control when it runs.
  ```jsx
  useEffect(() => {
    const timer = setInterval(tick, 1000);
    return () => clearInterval(timer);  // cleanup runs on unmount
  }, []);
  ```

- **`useContext`** — reads shared data (theme, logged-in user) from a Context, so deep components don't need it passed down through every layer ("prop drilling").

- **`useRef`** — a **box that holds a value that survives re-renders but does NOT cause a re-render** when changed. Two uses: (1) point to a DOM element, (2) store a "latest value" quietly.

- **`useMemo`** — **remembers the result of an expensive calculation** and only recomputes it when its inputs change (caching a *value*).

- **`useCallback`** — **remembers a function** so it's the same function object across renders (caching a *function* — important when passing to memoized children).

- **`useReducer`** — for **complex state** with many related updates. Uses a reducer function (Redux-style). Better than `useState` when state logic gets tangled.

---

### Q9. Rules of hooks?

**🟢 Simple idea:** Two rules: (1) always call hooks at the **top level** — never inside `if`, loops, or nested functions; (2) only call them **inside React components or other hooks**.

**🔵 Deeper explanation — *why* rule #1 exists (this is the key insight):**
React doesn't know hooks by name — it tracks them by **the order they're called** on each render. First `useState` → slot 1, second `useState` → slot 2, and so on.

Imagine calling out numbers in order every render: 1, 2, 3. React relies on that exact sequence to match each hook to its saved value. If you put a hook inside an `if`:
```jsx
if (loggedIn) {
  const [x] = useState();  // ❌ sometimes runs, sometimes doesn't
}
```
...then on some renders the count is 1,2,3 and on others it's 1,3 — the order shifts and React attaches the wrong saved value to the wrong hook. Chaos.

**Rule #2** just means hooks belong in React-land (components or custom hooks), not random plain functions.

**💬 Good news:** the ESLint `react-hooks` plugin catches violations automatically.

---

### Q10. useEffect dependency array — common pitfalls?

**🟢 Simple idea:** The second argument to `useEffect` (the `[...]`) tells React *when* to re-run the effect. Getting it wrong causes most React bugs.

**🔵 Deeper explanation — the three cases:**

- **`[]` (empty)** → runs **once** when the component appears (mount), and cleanup runs when it's removed (unmount). Great for one-time setup:
  ```jsx
  useEffect(() => { connectWebSocket(); }, []);
  ```

- **`[id]`** → re-runs whenever `id` changes. Great for re-fetching when a filter or route param changes:
  ```jsx
  useEffect(() => { fetchUser(id); }, [id]);
  ```

- **No array at all** → runs after *every* render (rarely what you want).

**⚠️ Pitfall 1 — Stale closures (missing dependencies):** If your effect uses a variable but you leave it out of the array, the effect "freezes" the old value from when it was created. Example: an interval that always sees `count = 0`. Fix: include everything the effect reads (the lint rule flags this).

**⚠️ Pitfall 2 — Forgetting cleanup:** If you open a WebSocket/timer/subscription but never return a cleanup function, you get **memory leaks and duplicate connections**. This is *very* real for your dashboards — a WebSocket must close when the component unmounts, or you'll pile up dead connections.
```jsx
useEffect(() => {
  const ws = new WebSocket(url);
  return () => ws.close();   // ✅ essential cleanup
}, [url]);
```

---

### Q11. useMemo vs useCallback?

**🟢 Simple idea:** Both "remember" something between renders. **`useMemo` remembers a value** (the result of a calculation). **`useCallback` remembers a function**.

**🔵 Deeper explanation:**

**`useMemo`** — skip re-doing an expensive calculation unless its inputs changed:
```jsx
const sortedList = useMemo(() => bigList.sort(compare), [bigList]);
```

**`useCallback`** — keep the *same function instance* across renders. Why does that matter? Because a `React.memo` child re-renders if you hand it a "new" function every time. Even if the function does the same thing, it's technically a new object each render:
```jsx
const handleClick = useCallback(() => doThing(id), [id]);
<MemoizedChild onClick={handleClick} />  // now child won't needlessly re-render
```

Fun fact: `useCallback(fn, deps)` is literally the same as `useMemo(() => fn, deps)`.

**⚠️ Senior caveat — don't over-use them.** Memoization isn't free: it uses memory and runs a comparison every render. For cheap calculations, plain code is actually faster. **Measure first, optimize the real hotspots.**

---

### Q12. What are custom hooks?

**🟢 Simple idea:** A custom hook is your *own* reusable function (name starts with `use`) that bundles up some logic using the built-in hooks — so you can reuse it across components without copy-pasting.

**🔵 Deeper explanation:**
Say every component that uses a WebSocket needs the same connect/subscribe/cleanup code. Instead of duplicating it, you extract it into `useWebSocket`:
```jsx
function useWebSocket(url) {
  const [data, setData] = useState(null);
  useEffect(() => {
    const ws = new WebSocket(url);
    ws.onmessage = e => setData(JSON.parse(e.data));
    return () => ws.close();
  }, [url]);
  return data;
}

// Now any component just does:
const liveData = useWebSocket("wss://health-stream");
```
This is the **modern replacement** for older reuse patterns (Higher-Order Components and render props), which worked but added confusing wrapper nesting. Custom hooks keep components clean and make logic easy to test on its own. Common examples: `useFetch`, `useDebounce`, `useLocalStorage`.

---

## C. State Management & Data

### Q13. How do you manage global state?

**🟢 Simple idea:** First figure out *what kind* of state you have. There are two very different kinds, and mixing them up is the #1 mistake:
- **Client state** = UI stuff your app owns (theme, is-modal-open, form values, logged-in flag).
- **Server state** = data that actually lives on a server and you're just caching a copy (user lists, product data).

Pick the tool based on which kind it is.

**🔵 Deeper explanation — the toolbox:**

- **Context API** (built into React) — good for **small, rarely-changing shared data** like theme, current user, or language. Simple. *Downside:* when the context value changes, *every* component reading it re-renders — so it's bad for fast-changing data.

- **Redux Toolkit (RTK)** — for **big apps** needing one predictable central store, great devtools (time-travel debugging), and middleware. RTK removed most of old Redux's painful boilerplate.

- **Zustand / Jotai / Recoil** — **lightweight** alternatives to Redux, way less ceremony. Zustand gives a simple hook-based store where **only components reading a specific slice re-render**.

- **React Query / TanStack Query** — *THE* modern way to handle **server state**: caching, background refetching, retries, keeping data fresh. Once you use it, you often need almost no global client state at all.

**💬 Senior answer:** "Don't reach for Redux by default. Use **React Query for server data**, and **Context or Zustand** for the small bit of genuine client state."

---

### Q14. Redux core concepts?

**🟢 Simple idea:** Redux is one big central box (store) holding all your app's data, with strict rules for changing it so everything stays predictable and traceable.

**🔵 Deeper explanation — the pieces, with a shopping-cart analogy:**

- **Store** — the single central object holding all state (one source of truth).
- **Action** — a plain object describing *what happened*, like a note: `{ type: 'cart/addItem', payload: item }`. It doesn't change anything by itself — it just announces the event.
- **Reducer** — a **pure function** `(currentState, action) => newState`. "Pure" means: same inputs always give the same output, and it never modifies the old state — it returns a *new* one. This purity is what makes time-travel debugging possible.
- **Dispatch** — the "send" button. `dispatch(action)` sends the action to the store, which runs the reducer.
- **Selector** — a function that reads just the slice of state a component needs (`useSelector`), so components only re-render when *their* data changes.

**The flow:** component `dispatch`es an action → reducer calculates new state → subscribed components re-render.

**💬 Modern note:** Always use **Redux Toolkit (RTK)** — `createSlice` auto-generates actions + reducers with far less code, and `createAsyncThunk` handles API calls with automatic pending/fulfilled/rejected states.

---

### Q15. How do you fetch data & handle loading/errors?

**🟢 Simple idea:** Basic way — call the API inside `useEffect` and store the result in state. Better way — use **React Query**, which handles caching, retries, and refetching for you. Either way, always show the user a loading spinner, error message, and empty state — not just the success case.

**🔵 Deeper explanation:**
A common junior mistake is only handling the "happy path" (data loaded successfully). A good UI handles **all four states**:
1. **Loading** → show a spinner or skeleton.
2. **Error** → show a message + a retry button.
3. **Empty** → data loaded but there's nothing (show "No results").
4. **Success** → render the data.

**For real-time data** (like your observability dashboards), you don't repeatedly ask the server "any updates?" over HTTP (polling is wasteful). Instead you use a **WebSocket** or **Server-Sent Events (SSE)** — a persistent connection where the server *pushes* updates the instant they happen.

React Query example with simple live polling:
```tsx
const { data, isLoading, error } = useQuery({
  queryKey: ['services'],
  queryFn: fetchServiceHealth,
  refetchInterval: 5000, // re-fetch every 5s for a live-ish dashboard
});
```

---

### Q16. How did you build a real-time dashboard? (your MGM/BMW experience)

**🟢 Simple idea:** The hard part of a live dashboard is that updates arrive *constantly* (many per second). If you naively update React on every message, the whole screen re-renders hundreds of times a second and freezes. The whole skill is **controlling what re-renders and how often.**

**🔵 Deeper explanation — the architecture (great story to tell):**

1. **WebSocket/SSE stream** pushes live data into the app.
2. **Batch/debounce incoming messages** before calling `setState` — instead of updating 200 times a second, collect messages and update, say, a few times a second. This alone saves you.
3. **Memoized chart components** (`React.memo` with stable props) — so only the specific charts whose data actually changed re-render, not all of them.
4. **List virtualization** (`react-window`) for big data tables — only render the rows currently visible on screen, not all 10,000.
5. **Debounced filters** — don't re-query on every keystroke; wait until the user pauses typing.
6. **`useRef` for non-visual bookkeeping** — data that doesn't need to show on screen goes in a ref (changing it doesn't cause a re-render).
7. **Selector-based store** — so changing one slice only re-renders the components reading that slice.

**💬 The talking point:** "It's all about controlling *what* re-renders and *how often* under a firehose of updates — batching messages, memoizing charts, and virtualizing tables."

---

## D. Performance & Architecture

### Q17. How do you optimize React performance?

**🟢 Simple idea:** Two goals: (1) stop components from re-rendering when they don't need to, and (2) make the browser download/process less stuff.

**🔵 Deeper explanation — the main levers:**

- **Memoization** — wrap pure components in **`React.memo`** (skips re-render if props didn't change), and use **`useMemo`/`useCallback`** to keep the values/functions you pass them stable (otherwise `React.memo` does nothing — see T3).

- **Code splitting** — with **`React.lazy` + `Suspense`** (usually per route), the browser only downloads the code for the page you're actually on. Faster initial load.

- **List virtualization** — render only the **visible rows** of huge lists (react-window), not thousands of hidden DOM nodes.

- **Avoid new references in props** — this trips everyone up. Writing `style={{color:'red'}}` or `onClick={() => ...}` inline creates a *brand-new* object/function on every render, which defeats `React.memo`. Hoist them out or memoize them.

- **Structural tactics** — good keys, pagination, debouncing frequent events, and **colocating state** (keep state as low/close to where it's used as possible; only lift it up when it's truly shared) so an update re-renders the smallest possible piece of the tree.

**💬 Senior framing:** "Measure first with the **React DevTools Profiler**, then fix the actual slow spots — don't sprinkle memoization everywhere blindly."

---

### Q18. What is code splitting / lazy loading?

**🟢 Simple idea:** Instead of forcing users to download your *entire* app before they can use it, you break it into chunks and load each chunk only when it's needed (usually per page).

**🔵 Deeper explanation:**
By default a bundler (Webpack/Vite) packs everything into one big JavaScript file. If your app has 50 pages, the user downloads all 50 before seeing anything — slow.

**Code splitting** breaks that big file into smaller pieces loaded **on demand**. Most common approach is **per route**: visiting `/dashboard` downloads only the dashboard's code, not the admin or settings pages.

```jsx
const Dashboard = React.lazy(() => import('./Dashboard'));

<Suspense fallback={<Spinner />}>
  <Dashboard />
</Suspense>
```
- `React.lazy(() => import(...))` tells React "load this component's code only when it's first needed."
- `<Suspense fallback={...}>` shows a loading UI (spinner) while that chunk downloads.

**Payoff:** faster initial load (smaller first download).
**Trade-off:** a brief pause the first time a new chunk is needed — so you split along natural boundaries (routes, big rarely-used components).

---

### Q19. Component composition patterns?

**🟢 Simple idea:** In React you build complex UIs by **combining small components** (composition), not by extending classes (inheritance). "Composition over inheritance."

**🔵 Deeper explanation — the common patterns:**

- **Container/Presentational split** — one component **fetches/manages data** (container), another just **displays UI from props** (presentational). Makes the display component reusable and easy to test.

- **Compound components** — a group of components that work together and share hidden state, giving a clean API:
  ```jsx
  <Tabs>
    <Tab>Home</Tab>
    <TabPanel>Home content</TabPanel>
  </Tabs>
  ```

- **Render props** — a component takes a *function* as its child that decides what to render. Powerful but older and more verbose.

- **Custom hooks** — the **modern** way to share *logic* (not UI). Largely replaced HOCs and render props.

- **`children` and slots** — pass JSX into a component via the special `children` prop, making it a flexible container:
  ```jsx
  <Card>{/* anything you put here becomes props.children */}</Card>
  ```

**💬 The goal:** small, focused, reusable components snapped together to build the app.

---

### Q20. How do you structure a large React app?

**🟢 Simple idea:** Organize files by **feature** (everything about "checkout" together), not by **type** (all components in one giant folder, all hooks in another).

**🔵 Deeper explanation:**

- **Feature-based folders** — put a feature's components, hooks, API calls, and tests together:
  ```
  /features/checkout/
     CheckoutPage.tsx
     useCart.ts
     checkoutApi.ts
     checkout.test.tsx
  ```
  This keeps related code together, so you're not jumping across the whole project to change one feature.

- **Shared UI library / design system** — reusable primitives (buttons, inputs, modals) with consistent styling.

- **Typed API layer** — one dedicated, typed module for backend calls, so fetch logic isn't scattered and types stay in sync.

- **Clear state boundaries** — server state via React Query, client state via Context/Zustand. Avoid one giant global store for everything.

- **Lazy-loaded routes** — code-split per route.

- **Colocated tests** — tests live next to the code they test.

**💬 Scaling further:** For huge enterprise apps with many teams, **micro-frontends** (e.g., Webpack Module Federation) let each team build and deploy their slice independently. But that adds real complexity — only worth it at genuine org scale. Otherwise a well-structured monorepo is simpler.

---

## E. TypeScript

### Q21. Why TypeScript over JavaScript?

**🟢 Simple idea:** TypeScript is JavaScript + a safety net. It checks your types *while you code*, so it catches mistakes (wrong type, typo in a name, forgetting `undefined`) *before* you ever run the app — instead of the app breaking in the user's browser.

**🔵 Deeper explanation:**
In plain JavaScript this silently breaks at runtime:
```js
function greet(user) { return "Hi " + user.name.toUpperCase(); }
greet({ nam: "Anup" }); // typo "nam" → crashes: cannot read toUpperCase of undefined
```
TypeScript catches it *as you type*:
```ts
function greet(user: { name: string }) { return "Hi " + user.name.toUpperCase(); }
greet({ nam: "Anup" }); // ❌ red squiggle immediately: "nam does not exist"
```

Benefits beyond bug-catching:
- **Better tooling** — accurate autocomplete, safe renaming/refactoring, jump-to-definition.
- **Self-documenting** — the types *are* the contract. You know exactly what a function needs and returns without reading its body.
- **Safe to change big codebases** — change a type, and the compiler points at *every* place that now breaks.

**Trade-off:** a bit more upfront typing and a build step — but well worth it for anything beyond a tiny script, especially team projects. (TypeScript compiles down to plain JavaScript to run.)

---

### Q22. `interface` vs `type`?

**🟢 Simple idea:** Both describe the "shape" of data. Rough rule: use **`interface`** for object shapes (like component props), and **`type`** when you need fancier things like unions.

**🔵 Deeper explanation:**

**`interface`** — best for describing objects; it's **extendable and mergeable**:
```ts
interface User { id: number; name: string; }
interface Admin extends User { role: string; }  // extends
```
"Declaration merging" means if you declare the same interface twice, they combine — useful for augmenting library types.

**`type`** (type alias) — more flexible. It can do things interfaces can't:
```ts
type ID = string | number;              // union: "one of these"
type Staff = User & { dept: string };   // intersection: "combine both"
type Point = [number, number];          // tuple
type Status = "idle" | "loading" | "done"; // string literal union
```

**💬 Practical guidance:** `interface` for object/props definitions (nice extendability), `type` when you need unions, intersections, tuples, or other advanced expressions. For a plain object shape, they're basically interchangeable.

---

### Q23. Key TS features to know?

**🟢 Simple idea:** A handful of TypeScript features give you most of the power. Here they are with quick examples.

**🔵 Deeper explanation:**

- **Generics** — reusable type-safe code parameterized by a type (a "placeholder type" filled in later):
  ```ts
  function first<T>(arr: T[]): T { return arr[0]; }
  first<number>([1, 2, 3]); // T becomes number
  ```

- **Union (`A | B`)** = "one of these," **Intersection (`A & B`)** = "both combined."

- **`unknown` vs `any`** — `any` turns off checking (avoid); `unknown` is the safe "not sure yet" that forces you to check before using (see Q25).

- **`enum`** — named constant sets (though string literal unions are often preferred).

- **Optional (`?`) and `readonly`**:
  ```ts
  interface User { id: number; email?: string; readonly createdAt: Date; }
  ```

- **Utility types** — derive new types from existing ones, keeping them DRY:
  - `Partial<T>` — all fields optional (great for update/patch objects)
  - `Pick<T, K>` / `Omit<T, K>` — take or exclude certain fields
  - `Record<K, V>` — a typed map/dictionary
  - `Required<T>` — all fields required

- **Type narrowing / type guards** — using `typeof`, `in`, or custom checks so TS refines a broad type inside a branch:
  ```ts
  if (typeof x === "string") { x.toUpperCase(); } // TS knows x is a string here
  ```

- **Discriminated unions** — a shared "tag" field lets TS know exactly which variant you have (see T11 for a full example).

---

### Q24. Typing a React component?

**🟢 Simple idea:** Define an `interface` for the props, then apply it to the component so TypeScript checks every place you use it.

```tsx
interface Props {
  title: string;                     // required string
  count?: number;                    // optional (the ?)
  onClick: (id: string) => void;     // a function taking a string, returning nothing
}

const Card = ({ title, count = 0, onClick }: Props) => (
  <div onClick={() => onClick(title)}>{title}: {count}</div>
);
```
Now if someone forgets `title` or passes a number for it, TypeScript errors immediately.

*(Note: `React.FC<Props>` also works and was popular, but many teams now prefer typing props directly as shown above.)*

---

### Q25. `any` vs `unknown`?

**🟢 Simple idea:** Both mean "a value we're not sure about." But **`any` turns off safety** (dangerous), while **`unknown` keeps safety on** by forcing you to check the type before using it (safe).

**🔵 Deeper explanation:**

**`any`** — TypeScript stops checking. You can do anything, and it won't warn you — which defeats the whole point of TypeScript:
```ts
let x: any = "hello";
x.foo.bar.baz();  // no error, but CRASHES at runtime
```

**`unknown`** — you can *store* anything, but TypeScript won't let you *use* it until you prove what it is:
```ts
let x: unknown = getData();
x.toUpperCase();               // ❌ error: don't know it's a string
if (typeof x === "string") {
  x.toUpperCase();             // ✅ now allowed — you proved it
}
```

**💬 Rule:** Use `unknown` when the type is genuinely unknown (parsing untrusted JSON, `catch (err)` blocks). Treat `any` as a code smell — a last resort.

---

## F. Web Fundamentals

### Q26. How do you make apps responsive & accessible?

**🟢 Simple idea:** Two separate quality goals:
- **Responsive** = looks good on any screen size (phone, tablet, desktop).
- **Accessible (a11y)** = usable by everyone, including people with screen readers or keyboard-only navigation.

**🔵 Deeper explanation:**

**Responsive techniques:**
- **CSS Flexbox and Grid** for layouts that flex/flow.
- **Media queries** to change the layout at certain widths (breakpoints).
- **Mobile-first** — design for small screens first, then add rules for bigger ones (simpler and more robust).
- **Relative units** (`rem`, `%`, `vw`) instead of fixed pixels, so things scale.
- **Responsive images** (`srcset`) to serve smaller images to phones.

**Accessibility techniques:**
- **Semantic HTML** — use `<button>`, `<nav>`, `<header>` instead of styled `<div>`s. They carry built-in meaning that screen readers understand.
- **ARIA attributes** — extra labels where semantics aren't enough.
- **Keyboard navigation & focus management** — everything usable without a mouse.
- **Color contrast**, **alt text** on images, proper **labels** on form fields.

**💬 Bonus point:** Good accessibility is often a **legal requirement** and also helps **SEO**.

---

### Q27. CSS approaches?

**🟢 Simple idea:** The core problem with CSS is that styles are global — one component's CSS can accidentally break another's. Every approach below solves this by **scoping** styles to a component.

**🔵 Deeper explanation:**

- **CSS Modules** — normal CSS files, but class names get automatically hashed/scoped to one component, so no collisions.

- **CSS-in-JS (Styled-components / Emotion)** — write styles inside your JavaScript, scoped to the component, with easy access to props/theme for dynamic styling. Small runtime cost.

- **Tailwind (utility-first)** — build styles from tiny utility classes right in the markup:
  ```jsx
  <div className="flex p-4 text-sm rounded shadow">...</div>
  ```
  Very fast to build with and consistent, though the markup gets verbose.

- **Sass/SCSS** — adds variables, nesting, and mixins to CSS (often combined with the others).

**💬 Common thread:** scope your styles so components don't clash.

---

### Q28. CORS — what is it?

**🟢 Simple idea:** CORS is a **browser security rule** that stops a website from freely calling APIs on a *different* domain — unless that server explicitly says "yes, this website is allowed." It's configured on the **backend**, not the frontend.

**🔵 Deeper explanation:**
An **origin** = protocol + domain + port (e.g., `https://app.mgm.com:443`). By default, browsers enforce the **same-origin policy**: a page can only call APIs on its *own* origin, to protect users from malicious cross-site requests.

**CORS (Cross-Origin Resource Sharing)** is how a server *opts in* to allowing other origins. The server returns headers like:
```
Access-Control-Allow-Origin: https://app.mgm.com
```
For "non-simple" requests (custom headers, or methods like PUT/DELETE), the browser first sends a **preflight `OPTIONS` request** asking the server "am I allowed to do this?" before sending the real request.

**⚠️ Two things to stress in interviews:**
1. CORS is **enforced by the browser, not the server** — so it doesn't affect server-to-server calls or Postman (which is why "it works in Postman but not the browser" happens).
2. It's **fixed on the backend/gateway**, not the frontend. This is the #1 source of "why is my API call blocked?" confusion.

---

### Q29. How do you handle auth on the frontend?

**🟢 Simple idea:** Log the user in, attach their token to API requests, and store that token as safely as possible so it can't be stolen. And remember — the frontend is never the *real* security; the backend must always re-check.

**🔵 Deeper explanation — key practices:**

- **Store tokens securely** — prefer **httpOnly, Secure cookies** over `localStorage`. An httpOnly cookie **can't be read by JavaScript**, so if an attacker injects a malicious script (**XSS**), they still can't steal the token. The browser attaches the cookie automatically. Storing a JWT in `localStorage` is convenient but any XSS script can read it.

- **Attach the token** — automatic with cookies, or manually via an `Authorization: Bearer <token>` header (often using an axios interceptor that adds it to every request).

- **Refresh tokens** — use **short-lived access tokens** + a **refresh token** flow, so even a stolen token expires fast. Handle the refresh transparently (queue in-flight requests while refreshing — see T9).

- **Route guards** — redirect not-logged-in users away from protected pages; on a `401` response, send them to login.

**💬 Golden rule:** "The frontend is never the security boundary — the **backend must re-validate** every token and permission on every request."

---

### Q30. Browser rendering & optimization basics?

**🟢 Simple idea:** This is about how the browser turns your code into pixels, and how to make that fast — mainly by (1) downloading less and (2) making the browser recalculate the layout less often.

**🔵 Deeper explanation:**
The **critical rendering path** is the browser's step-by-step process:
1. Parse HTML → build the **DOM**.
2. Parse CSS → build the **CSSOM**.
3. Combine them → **render tree**.
4. **Layout** — figure out where everything goes.
5. **Paint** — actually draw pixels.

The goal is to get meaningful content on screen quickly.

**Optimization techniques:**
- **Minimize bundle size** — **tree-shaking** (drop unused code), minification, code splitting.
- **Lazy-load images** and offscreen content.
- **Caching + CDN** — serve assets fast and geographically close to users.
- **Debounce/throttle** high-frequency events (scroll, resize, input) so you don't do work on every single event.
- **Avoid layout thrashing** — don't repeatedly read a layout property (like `element.offsetHeight`) and then change the layout in a loop; that forces the browser to recalculate layout over and over. Batch reads, then batch writes.

**💬 Theme:** download less, recompute layout/paint less often.

---

## ⚡ Rapid-Fire (with quick explanations)

- **SPA vs SSR vs SSG** — SPA renders in the browser (blank until JS loads); SSR renders on the server per request (good SEO, e.g., Next.js); SSG pre-builds static HTML at build time (fastest).
- **Next.js** — a React framework that adds SSR/SSG, file-based routing, and API routes.
- **Error boundaries** — special components that catch errors during rendering and show a fallback instead of a white screen.
- **StrictMode** — a dev-only helper that double-invokes effects/renders to surface bugs (like missing cleanup). Off in production.
- **Testing** — Jest + React Testing Library (test *behavior*, not internals); Cypress/Playwright for full end-to-end tests.
- **Debounce vs throttle** — both limit how often something runs; **debounce waits for a pause** (search box), **throttle caps the rate** (scroll handler).
- **Prop drilling** — passing props through many layers; solved with Context or a state library.
- **Your 3 performance levers** — reconciliation keys, memoization, virtualization.

---
---

# PART 2 — Advanced & Tough Questions (with detailed explanations + examples)

## T1. Explain the closure/stale-state trap in `useEffect` and `setInterval`.

**🟢 Simple idea:** When you set up an interval inside `useEffect` with an empty `[]`, the interval "remembers" the value of `count` from the very first render *forever* — so it keeps adding 1 to 0, giving you 1 every time instead of counting up.

**🔵 Why it happens:** The function inside `setInterval` is a **closure** — it captures whatever `count` was when the effect ran (which was `0`, on mount). Since `[]` means "only set up once," it never gets the new `count`.
```tsx
function Counter() {
  const [count, setCount] = useState(0);
  useEffect(() => {
    const id = setInterval(() => setCount(count + 1), 1000); // BUG: count is stuck at 0
    return () => clearInterval(id);
  }, []); // empty deps → closure captured count=0
}
```

**✅ The fix — functional update:** `setCount(c => c + 1)` uses whatever the *latest* count is, without depending on the captured value:
```tsx
setCount(c => c + 1);   // always uses the current value
```
Other fixes: add `count` to the deps (recreates the interval each change — less ideal), or use `useRef` to hold the latest value.

---

## T2. Why does React batch state updates, and what breaks intuition?

**🟢 Simple idea:** If you call `setCount` twice in a row using the current value, both calls use the *same old* value — so you get +1, not +2. React also groups multiple updates into one re-render for performance.

**🔵 Deeper explanation:**
```tsx
setCount(count + 1);  // count is 0 → sets to 1
setCount(count + 1);  // count is STILL 0 here → sets to 1 again → net +1
```
Both lines read the same `count` (0) because state updates are **asynchronous** — `count` doesn't change mid-function. React **batches** these updates and re-renders once.

**✅ Correct way** — functional updaters, each getting the latest value:
```tsx
setCount(c => c + 1);  // 0 → 1
setCount(c => c + 1);  // 1 → 2  ✅
```
**Note:** React 18 batches updates *everywhere* now (even inside promises/timeouts) — "automatic batching." Also, reading state right after setting it gives you the *old* value (it updates on the next render).

---

## T3. When does `React.memo` actually help — and when does it silently do nothing?

**🟢 Simple idea:** `React.memo` skips re-rendering a child if its props didn't change. But if you pass a *new* function or object every render (even one that looks identical), the props *did* "change" (new reference) — so memo does nothing.

**🔵 Deeper explanation:** `React.memo` does a **shallow comparison** of props. In JavaScript, `{} !== {}` and `(() => {}) !== (() => {})` — two identical-looking objects/functions are different references. So:
```tsx
// ❌ Parent creates NEW onClick + style every render → memo is useless
<Child onClick={() => doThing()} style={{color:'red'}} />
```

**✅ Fix — stabilize the references** with `useCallback`/`useMemo`:
```tsx
const onClick = useCallback(() => doThing(), []);
const style = useMemo(() => ({ color: 'red' }), []);
<Child onClick={onClick} style={style} />  // now memo works
```

**💬 Key lesson:** `React.memo` + `useCallback`/`useMemo` go together. But don't over-apply — premature memoization adds complexity and cost.

---

## T4. `useMemo`/`useCallback` — are they free? When NOT to use them?

**🟢 Simple idea:** No, they're not free. They use memory and run a comparison every render. For cheap calculations, plain code is actually faster.

**🔵 Deeper explanation:** Use them only when there's a real benefit:
- A genuinely **expensive computation** (sorting/filtering a big list).
- Keeping a **stable reference** to pass to a memoized child (T3).

For a simple value like `const total = a + b`, wrapping it in `useMemo` is wasteful — the memoization overhead costs more than just recomputing. They can also **hide bugs** via stale dependency arrays.

**💬 Senior answer:** "Measure first. Only memoize the actual hotspots."

---

## T5. How do you prevent unnecessary re-renders in a large dashboard? (your MGM/BMW case)

**🟢 Simple idea:** Make sure only the small piece that changed re-renders — not the whole screen.

**🔵 The toolkit:**
- **Split/colocate state** so high-frequency updates don't re-render the whole tree — keep state close to where it's used; lift only when truly shared.
- **`React.memo` leaf chart components** with stable props.
- **Virtualize** long lists/tables with `react-window` (render only visible rows).
- **Debounce/throttle** stream updates before calling `setState` (batch incoming WebSocket messages).
- **Selector-based store** (Zustand/Redux `useSelector`) so only components reading a slice re-render.
- **`useRef`** for non-visual data (changing it doesn't re-render).

**💬 Talking point:** tune WebSocket update frequency + batch incoming messages.

---

## T6. Controlled vs uncontrolled — and why controlled forms can be a perf problem.

**🟢 Simple idea:** Controlled inputs re-render on *every keystroke*. In a huge form, that's a lot of re-renders and can feel laggy.

**🔵 Deeper explanation:** Controlled = React state is the source of truth, easy validation, but re-renders each keypress. For big forms, use **react-hook-form** (uses uncontrolled inputs + refs under the hood) to minimize re-renders, or debounce the state updates.

**Trade-off:** controlled = predictable + easy validation; uncontrolled = better performance.

---

## T7. `useEffect` vs `useLayoutEffect` — when does it matter?

**🟢 Simple idea:** `useEffect` runs *after* the screen is painted (doesn't block). `useLayoutEffect` runs *before* paint (blocks briefly) — use it when you need to measure or adjust the DOM before the user sees it, to avoid a visible flicker.

**🔵 Deeper explanation:**
- **`useEffect`** — runs asynchronously after paint. Good for 99% of cases (data fetching, subscriptions).
- **`useLayoutEffect`** — runs synchronously after DOM changes but *before* the browser paints. Use it when you must **read an element's size/position and adjust** before it's visible — e.g., positioning a tooltip based on measured dimensions. If you did this in `useEffect`, the user might briefly see it in the wrong spot (flicker).

**⚠️ Caveat:** `useLayoutEffect` blocks painting, so overusing it hurts performance.

---

## T8. What problem does React Query (TanStack Query) solve that Redux doesn't?

**🟢 Simple idea:** Redux is for *your app's own* data (client state). React Query is specifically for *server* data — it automatically handles caching, refetching, retries, and keeping data fresh, which you'd otherwise have to build by hand.

**🔵 Deeper explanation:** React Query manages **server state**: caching, background refetch, request deduping, stale-while-revalidate (show cached data instantly while fetching fresh data), retries, pagination, and cache invalidation. It removes tons of boilerplate (the manual loading/error/caching code you'd write with `useEffect` + Redux).

**💬 Rule:** Redux/Zustand for **UI/client state**; React Query for **API data**. Often you don't need Redux at all anymore.

---

## T9. How do you handle authentication + token refresh cleanly on the frontend?

**🟢 Simple idea:** Store tokens safely (httpOnly cookies), and when a request fails with 401 (expired token), automatically refresh the token and retry — without the user noticing.

**🔵 Deeper explanation:**
- Prefer **httpOnly Secure cookies** (mitigates XSS; browser sends them automatically; backend handles refresh).
- If using bearer tokens: use an **axios interceptor** that catches a `401` → calls the refresh endpoint → retries the original request. **Queue concurrent requests** during refresh so you don't fire 10 refresh calls at once (a "refresh storm").
- Route guards redirect not-logged-in users; keep minimal user info in memory/context — never sensitive tokens in `localStorage`.

---

## T10. Error boundaries — what they catch and what they don't.

**🟢 Simple idea:** An error boundary is a component that catches crashes *during rendering* in its child tree and shows a fallback UI instead of a blank white screen. But it does NOT catch errors in event handlers or async code.

**🔵 Deeper explanation:**
Built with a class component (or the `react-error-boundary` library) using `getDerivedStateFromError` / `componentDidCatch`. It catches **render-time errors** in the subtree below it.

**It does NOT catch:**
- Errors in **event handlers** (use try/catch there).
- **Async** errors (setTimeout, promises).
- Errors during **server-side rendering**.
- Errors in the **boundary itself**.

**💬 Best practice:** wrap risky sections + report caught errors to Sentry.

---

## T11. TypeScript: generics + discriminated unions for safer components.

**🟢 Simple idea:** A "discriminated union" uses a shared tag field (like `status`) so TypeScript knows exactly which shape you have in each branch — and stops you from accessing fields that don't exist there.

```tsx
type Result<T> =
  | { status: 'loading' }
  | { status: 'error'; error: string }
  | { status: 'success'; data: T };

function render<T>(r: Result<T>) {
  switch (r.status) {
    case 'loading': return <Spinner/>;
    case 'error':   return <Err msg={r.error}/>;   // ✅ TS knows .error exists ONLY here
    case 'success': return <View data={r.data}/>;  // ✅ TS knows .data exists ONLY here
  }
}
```

**🔵 Why it's powerful:** In the `'error'` branch, TypeScript knows `r` has `.error` but *not* `.data`, and vice versa. If you try `r.data` in the error branch, it errors. Add a `never` default case to force **exhaustiveness** (TS errors if you add a new status and forget to handle it). **Generics** (`<T>`) make the component reusable for any data type.

---

## T12. `any` vs `unknown` vs `never` — and utility types in practice.

**🟢 Simple idea:**
- `any` = "stop checking" (dangerous).
- `unknown` = "I don't know yet, force me to check first" (safe).
- `never` = "this can never happen" (used for exhaustiveness checks).

**🔵 Utility types in practice:**
- `Partial<T>` — makes all fields optional (perfect for update/patch objects where you only send changed fields).
- `Pick<T, K>` / `Omit<T, K>` — build a smaller view model from a big type.
- `Record<K, V>` — a typed dictionary/map.
- `ReturnType<F>` / `Parameters<F>` — extract a function's return type or argument types.

These keep types **DRY** — derive them from one source-of-truth type instead of redefining.

---

## T13. Micro-frontends — when and how (enterprise relevance)?

**🟢 Simple idea:** Split one big frontend into independent pieces that separate teams can build and deploy on their own, then stitch them together at runtime.

**🔵 Deeper explanation:** Use **Module Federation** (Webpack 5) or a shell app + "remotes."
- **Benefits:** team autonomy, independent releases.
- **Costs:** shared-dependency version conflicts, bundle duplication, keeping state/styling consistent across apps, runtime integration complexity.

**💬 Verdict:** Only adopt at real org scale. For most apps, a modular monorepo is simpler.

---

## T14. SSR/SSG/ISR (Next.js) — why and the trade-offs?

**🟢 Simple idea:** Different ways to decide *where* and *when* your pages get built into HTML.

**🔵 The options:**
- **CSR (client-side)** — renders in the browser. Fast to build, but poor SEO and a blank screen until JS loads.
- **SSR (server-side)** — renders on the server *per request*. Fresh data + good SEO, but slower TTFB and more server cost.
- **SSG (static)** — pre-renders at *build time*. Fastest + cache-friendly, but static (needs a rebuild to update).
- **ISR (incremental)** — SSG + periodic regeneration. Best of both for semi-dynamic content (e.g., a blog that updates hourly).

**💬 Choose per page** based on freshness + SEO needs.

---

## T15. Tough rapid-fire

- **Why not use array index as a key?** When you reorder/insert/delete, indexes shift and React reuses the wrong component → state/DOM bugs. Use stable IDs.
- **What does StrictMode double-invoke and why?** Effects/renders (in dev only) to surface impure logic or missing cleanup. Not in production.
- **Reconciliation:** React diffs by element **type + key**. Different type → it unmounts and remounts (losing that subtree's state).
- **Debounce vs throttle:** debounce waits for a pause (search box); throttle caps the rate (scroll/resize).
- **Hydration mismatch (SSR):** server HTML and client's first render differ → warnings/bugs. Keep rendering deterministic (no `Math.random()`/`Date.now()` differences).
- **Context re-render pitfall:** every consumer re-renders when the context value changes → split contexts or memoize the value object.
- **Also know:** keys in fragments/lists, `lazy` + `Suspense` for code splitting, and **`useTransition`** (React 18) to keep the UI responsive during heavy updates.

---
---

# PART 3 — More Real Interview Questions (Easy Language, No Repeats)

## Q1. What is React, in one simple line?
A JavaScript library for building user interfaces out of small, reusable pieces called **components**, where the UI automatically updates when the underlying data (state) changes.

## Q2. What is a component?
A reusable, self-contained piece of UI — like a Lego block. It's a function that takes inputs (**props**) and returns what should appear on screen (JSX). You compose small components into bigger ones to build the whole app.

## Q3. What does "declarative" mean in React?
You describe **what** the UI should look like for a given state, and React figures out **how** to update the DOM. You don't manually add/remove elements — you just change the state and React re-renders. (Imperative = you manually manipulate the DOM step by step; declarative = you describe the end result.)

## Q4. What is "state lifting"?
When two sibling components need to share data, you move (lift) that state **up** to their common parent, then pass it down to both as props. The parent becomes the single source of truth. It's the standard way to share data between components without a global store.

**Example:** Two components — a search box and a results list. Put the `searchText` state in their shared parent; pass it down to both.

## Q5. What is "prop drilling" and how do you avoid it?
Passing props down through many layers of components just to reach a deeply nested one — tedious and messy (each middle component has to forward a prop it doesn't even use). Avoid it with the **Context API** (for shared data like theme/auth) or a state library (Redux/Zustand) so deep components can read the data directly.

## Q6. What happens when state changes in React?
React re-runs the component function to produce a new virtual UI, **compares** it to the previous version (diffing), and updates only the parts of the real DOM that actually changed. This is why React feels fast — minimal DOM updates.

## Q7. Why do we need `key` when rendering a list?
Keys give each list item a stable identity (a name tag) so React knows which items changed, moved, or were removed. Without good keys (or using array index), React can reuse the wrong DOM elements, causing bugs like a typed value showing on the wrong row. Use a unique ID as the key.

## Q8. What is conditional rendering? Show simple ways.
Showing different UI based on a condition:
```jsx
{isLoggedIn ? <Dashboard/> : <Login/>}     // ternary: A or B
{error && <ErrorBanner msg={error}/>}      // show only if error exists
{items.length === 0 && <Empty/>}           // show only if list is empty
```

## Q9. What is the difference between state and props (simple)?
- **Props** — data passed **into** a component from its parent (read-only, like function arguments).
- **State** — data a component **owns and can change** over time (like variables it manages). Changing state triggers a re-render.

## Q10. What is `useEffect` used for, in plain words?
For "side effects" — things beyond just drawing UI: fetching data from an API, setting up a timer, subscribing to a WebSocket, or updating the document title. It runs *after* the component renders, and can clean up after itself (e.g., close the WebSocket) when the component is removed.

## Q11. How do you fetch data from an API in React?
Basic way: call the API inside `useEffect` and store the result in state.
```jsx
useEffect(() => {
  fetch("/api/users")
    .then(r => r.json())
    .then(setUsers)
    .catch(setError);
}, []);   // [] = run once on mount
```
Modern way: use **React Query**, which handles loading, caching, retries, and refetching for you.

## Q12. What is JSX, and can browsers understand it?
JSX is the HTML-like syntax you write inside JavaScript (`<div>Hello {name}</div>`). Browsers **can't** read it directly — a tool like **Babel** compiles it into regular JavaScript (`React.createElement(...)`) before it runs.

## Q13. What is a Single Page Application (SPA)?
An app that loads one HTML page and then updates the content dynamically with JavaScript as you navigate, instead of reloading the whole page from the server each time. Feels fast and app-like. React apps are typically SPAs (with React Router handling "pages").

## Q14. What is client-side routing (React Router)?
It lets your SPA show different "pages" (URLs) without full page reloads. React Router matches the URL to a component and swaps the view instantly. `/home` shows `<Home/>`, `/profile` shows `<Profile/>` — all in the browser, no server round-trip.

## Q15. Why is TypeScript popular for React projects?
It adds **types** to JavaScript, so mistakes (like passing a number where a string is expected, or a typo in a prop name) are caught **while you code**, not after the app breaks in the browser. It also gives great auto-complete and makes large codebases much safer to change.

## Q16. What is a `type` or `interface` in TypeScript, simply?
It's a description of the "shape" of your data — what fields it has and their types:
```ts
interface User { id: number; name: string; email?: string; } // ? = optional
```
Now anywhere you use a `User`, TypeScript checks you're using the right fields.

## Q17. What is the difference between `let`, `const`, and `var` (JS basics they may ask)?
- `const` — can't be reassigned (use by default).
- `let` — can be reassigned; block-scoped.
- `var` — old, function-scoped, has confusing hoisting behavior — avoid it.

## Q18. What are arrow functions and why are they common in React?
A shorter way to write functions: `const add = (a, b) => a + b;`. In React they're used for event handlers and callbacks. They also don't rebind `this`, which avoided a lot of bugs in older class components.

## Q19. What is the difference between `==` and `===` in JavaScript?
- `==` compares values but does **type coercion** (`"5" == 5` is true — confusing).
- `===` compares value **and** type, no coercion (`"5" === 5` is false).
Always use `===` to avoid surprises.

## Q20. How do you handle forms in React (simple version)?
Use **controlled inputs** — the input's value comes from state, and you update state on every change:
```jsx
const [name, setName] = useState("");
<input value={name} onChange={e => setName(e.target.value)} />
```
For big/complex forms, use a library like **react-hook-form** to reduce re-renders and simplify validation.

## Q21. What is a build tool (Vite/Webpack) and what does it do?
It bundles your many JS/TS/CSS files into optimized files the browser can load quickly, compiles JSX/TypeScript into plain JS, and provides a fast dev server with hot reload. **Vite** is the modern fast default; **Webpack** is the older, powerful one (still used for micro-frontends via Module Federation).

## Q22. How do you make a website work well on mobile (responsive design)?
Use flexible layouts (CSS **Flexbox/Grid**), relative units (`%`, `rem`), and **media queries** to change layout at different screen widths. Design **mobile-first** (style for small screens, then add rules for bigger ones). Test on multiple screen sizes. This ties to the JD's "responsive across desktop, tablet, mobile" requirement.

---
---

# PART 4 — Actual Interview Questions (exactly as asked, with detailed answers)

> These are the exact questions asked in a recent interview. Answers are written to be spoken out loud confidently. Some overlap earlier sections — that's intentional so each question has a complete, standalone answer.

## IQ1. What are ReactJS key features?
React's headline features, each with the *why*:
- **Component-based architecture** — the UI is built from small, reusable, self-contained pieces. You compose small components into bigger ones. This makes code reusable, testable, and easy to reason about.
- **Virtual DOM + reconciliation** — React keeps a lightweight in-memory copy of the UI. On a state change it builds a new virtual tree, **diffs** it against the old one, and updates only the changed nodes on the real DOM. Fewer expensive DOM operations = fast UI.
- **Declarative** — you describe *what* the UI should look like for a given state; React figures out *how* to update the DOM. You never manually manipulate DOM nodes.
- **One-way (unidirectional) data flow** — data flows top-down from parent to child via props, which makes data easy to trace and debug.
- **JSX** — HTML-like syntax inside JavaScript, compiled by Babel to `React.createElement` calls.
- **Hooks** — functions like `useState`, `useEffect`, `useMemo` that let function components hold state and side effects without classes.
- **Rich ecosystem** — React Router (routing), Redux/Zustand (state), React Query (server state), Next.js (SSR/SSG).
- **One-liner:** "Components + Virtual DOM + declarative rendering + one-way data flow + hooks — that combination is what makes React productive and fast."

## IQ2. What makes ReactJS more effective than other frameworks?
Speak comparatively and honestly:
- **Virtual DOM diffing** — instead of re-rendering the whole page, React computes the *minimal* set of real-DOM changes. Many older approaches re-touched the DOM directly, which is slow.
- **Declarative model reduces bugs** — you manage state, not DOM steps. Fewer manual DOM manipulations means fewer inconsistency bugs.
- **Just a library, not a full framework** — React is unopinionated about routing, state, and data-fetching, so you pick best-in-class tools. Angular, by contrast, is a full opinionated framework (heavier but more batteries-included).
- **Huge ecosystem & community** — the most mature ecosystem, tons of libraries, hiring pool, and long-term support (backed by Meta).
- **Reusable component model + hooks** — logic reuse via custom hooks is cleaner than mixins/HOCs of the past.
- **Learn once, write anywhere** — same mental model powers React Native (mobile), Next.js (SSR), etc.
- **Balanced comparison:** "Vue is approachable and Angular is a complete framework, but React's flexibility, Virtual DOM performance, and ecosystem maturity make it the safest choice for large, long-lived apps. The trade-off is you assemble your own stack."

## IQ3. Have you worked with Nest.js?
Be honest but demonstrate understanding:
- **What Nest.js is:** a **Node.js backend framework** (not frontend) built with TypeScript, heavily inspired by Angular's architecture — it uses **modules, controllers, providers/services, and dependency injection**. It runs on top of Express (or Fastify) under the hood.
- **Why teams use it:** it brings **structure and enterprise patterns** (DI, decorators, modules) to Node backends, making large codebases maintainable — similar discipline to Spring Boot in the Java world.
- **Key concepts:** `@Controller` (routes), `@Injectable` services, `@Module` to group features, built-in support for **guards** (auth), **interceptors**, **pipes** (validation), and easy integration with TypeORM/Prisma, GraphQL, WebSockets, and microservices.
- **How to answer if limited experience:** "I've primarily worked with Java/Spring Boot on the backend and React on the frontend, but I understand Nest.js well — it maps almost one-to-one to Spring concepts (controllers, services, DI, modules), so I'd ramp up quickly. It's essentially 'Angular-style architecture for Node backends.'"

## IQ4. What challenges have you faced while working with ReactJS?
Give real, senior-level challenges and how you solved them:
- **Unnecessary re-renders / performance** — large dashboards re-rendering too often. Solved with `React.memo`, `useMemo`/`useCallback`, selector-based stores, and list virtualization (`react-window`).
- **Stale closures in `useEffect`** — effects capturing old state values. Solved with functional state updates (`setCount(c => c + 1)`) and correct dependency arrays.
- **`useEffect` dependency array pitfalls** — missing deps causing stale data, or too many deps causing infinite loops. Solved with the `react-hooks` ESLint rule and careful memoization of referenced objects/functions.
- **Prop drilling** in deep trees — solved with Context API or a state library (Redux/Zustand).
- **Managing server vs client state** — mixing them causes messy code. Solved by using **React Query for server state** and Context/Zustand for client state.
- **Memory leaks** — WebSockets/timers not cleaned up on unmount. Solved with cleanup functions in `useEffect`.
- **State management complexity at scale** — solved by adopting Redux Toolkit with clear slices and selectors.
- **One-liner:** "The recurring theme was **controlling re-renders and managing state boundaries** — most React problems come down to those two."

## IQ5. What is React re-rendering?
- **Definition:** a **re-render** is React **calling your component function again** to produce a new description of the UI (new virtual DOM). It does *not* necessarily mean the real DOM changes — after re-rendering, React diffs and updates the DOM only where needed.
- **What triggers a re-render:**
  1. **State change** — calling a `useState`/`useReducer` setter.
  2. **Props change** — a parent passes new props.
  3. **Parent re-renders** — by default, when a parent re-renders, all its children re-render (unless memoized).
  4. **Context value change** — every consumer of that context re-renders.
- **Key nuance:** re-render (running the function) ≠ repaint (DOM update). React re-renders in memory, diffs, then commits minimal DOM changes.
- **One-liner:** "Re-rendering is React re-running the component to compute the new UI; whether the actual DOM changes depends on the diff."

## IQ6. How do you detect issues in ReactJS re-rendering?
Practical tooling and techniques:
- **React DevTools Profiler** — records renders and shows **which components re-rendered, how often, and why** ("Why did this render?"). This is the primary tool.
- **"Highlight updates" option** in React DevTools — flashes components on screen as they re-render, so you *see* excessive re-renders visually.
- **`why-did-you-render` library** — logs to the console whenever a component re-renders unnecessarily (props/state looked equal but reference changed).
- **`console.log` / `console.count`** in the render body as a quick check of render frequency.
- **StrictMode** — double-invokes renders/effects in dev to surface impure logic and missing cleanup.
- **Look for common culprits:** inline objects/functions in props (`style={{...}}`, `onClick={() => ...}`), context value objects recreated each render, unstable keys, and lifting state too high.
- **One-liner:** "Profile with React DevTools first to find *what* re-renders and *why*, then fix the root cause — don't guess."

## IQ7. How do you fix issues in ReactJS (re-rendering / performance)?
The fix toolkit, matched to the cause:
- **`React.memo`** — wrap a component so it skips re-rendering when its props are shallow-equal.
- **`useMemo`** — cache an expensive computed value so it recomputes only when inputs change.
- **`useCallback`** — keep a function's identity stable across renders (essential when passing callbacks to memoized children).
- **Stabilize props** — don't create new objects/functions inline; hoist or memoize them (otherwise `React.memo` is useless — new reference every render).
- **Colocate / lift state correctly** — keep state as close to where it's used as possible so an update re-renders the smallest subtree.
- **Selector-based stores** — with Redux `useSelector` or Zustand, only components reading a changed slice re-render.
- **Split contexts** — a single big context re-renders all consumers; split into smaller contexts or memoize the value.
- **List virtualization** (`react-window`) — render only visible rows in big lists/tables.
- **Code splitting** (`React.lazy` + `Suspense`) — reduce initial bundle.
- **Debounce/throttle** high-frequency events (search input, scroll, WebSocket streams).
- **One-liner:** "Memoize the right things, stabilize references, colocate state, and virtualize big lists — but always measure first."

## IQ8. What are class components in ReactJS?
- **Definition:** the older way to write components using an ES6 `class` that extends `React.Component`, with a required `render()` method returning JSX.
- **State & lifecycle:** state lives in `this.state`, updated via `this.setState()`. Behavior is wired through **lifecycle methods**: `componentDidMount` (after first render — good for data fetching/subscriptions), `componentDidUpdate` (after updates), and `componentWillUnmount` (cleanup before removal).
```jsx
class Welcome extends React.Component {
  constructor(props) {
    super(props);
    this.state = { count: 0 };
  }
  componentDidMount() { /* fetch data / subscribe */ }
  componentWillUnmount() { /* cleanup */ }
  render() {
    return <button onClick={() => this.setState({ count: this.state.count + 1 })}>
      {this.state.count}
    </button>;
  }
}
```
- **Why the industry moved away:** hard logic reuse (needed HOCs/render props), related code scattered across lifecycle methods, and `this`-binding bugs.
- **Still relevant because:** **Error Boundaries can currently only be written as class components** (`getDerivedStateFromError` / `componentDidCatch`), and you'll encounter class components in legacy code.

## IQ9. What are Pure Components in ReactJS?
- **Definition:** a **`PureComponent`** is a class component that implements `shouldComponentUpdate` with a **shallow comparison** of props and state automatically. It **skips re-rendering** if the new props/state are shallow-equal to the previous ones — a built-in performance optimization.
```jsx
class MyList extends React.PureComponent {
  render() { return <div>{this.props.items.length}</div>; }
}
```
- **Functional equivalent:** **`React.memo`** does the same thing for function components (shallow-compares props and skips re-render if unchanged).
- **The shallow-comparison catch:** it only compares references one level deep. If you mutate an object/array in place (same reference) or pass a *new* inline object/function each render, the optimization either misses the change or is defeated. Always pass **new references for changed data** and **stable references for unchanged data**.
- **One-liner:** "A PureComponent auto-skips re-renders via shallow prop/state comparison — `React.memo` is its hook-era equivalent — but you must respect immutability and reference stability for it to work."

## IQ10. What are hooks in functional components?
- **Definition:** hooks are special functions (names start with `use`) that let **function components** use state, lifecycle-like side effects, context, and more — features that used to require class components.
- **Core hooks:**
  - **`useState`** — local state: `const [count, setCount] = useState(0)`.
  - **`useEffect`** — side effects after render (fetch, subscriptions, timers), with a dependency array and optional cleanup.
  - **`useContext`** — read shared data from a Context without prop drilling.
  - **`useRef`** — a mutable box that survives re-renders without causing one (DOM refs or "latest value" storage).
  - **`useMemo`** — cache an expensive computed value.
  - **`useCallback`** — cache a function's identity across renders.
  - **`useReducer`** — Redux-style state for complex, related updates.
  - **`useLayoutEffect`** — like `useEffect` but runs synchronously before paint (for DOM measurement).
- **Rules of hooks:** (1) call them only at the **top level** (never inside conditions/loops), and (2) only from **React components or custom hooks**. React tracks hooks by call order, so the order must be stable.
- **Custom hooks:** you can bundle logic into your own `useXxx` hook (e.g., `useFetch`, `useWebSocket`) to reuse stateful logic across components.

## IQ11. Explain `useMemo` in ReactJS.
- **Purpose:** `useMemo` **caches (memoizes) the result of an expensive calculation** and only recomputes it when one of its dependencies changes. Between renders where the deps are unchanged, it returns the previously computed value.
```jsx
const sortedList = useMemo(() => {
  return bigList.slice().sort((a, b) => a.value - b.value); // expensive
}, [bigList]);   // recompute only when bigList changes
```
- **Two main use cases:**
  1. **Avoid re-running expensive computations** (sorting/filtering large lists, heavy math) on every render.
  2. **Stabilize a reference** (e.g., an object/array) passed to a memoized child, so `React.memo` isn't defeated by a new reference each render.
- **Not free:** it uses memory and runs a dependency comparison every render. For cheap calculations (`a + b`), plain code is faster — don't over-use it.
- **Related:** `useCallback(fn, deps)` is `useMemo(() => fn, deps)` — one caches a value, the other a function.
- **One-liner:** "`useMemo` remembers a computed value between renders so you don't redo expensive work or hand memoized children unstable references."

## IQ12. There are 3 components A, B, C. If an update happens in component A, what is the sequence of rendering in React?
This tests understanding of the render tree and top-down rendering.
- **The rule:** when a component's **state updates, that component re-renders, and then React re-renders its entire subtree (all descendants) by default** — regardless of whether their props changed. Rendering flows **top-down** (parent before children).
- **It depends on the tree structure. Two common cases:**

**Case 1 — A is the parent of B, which is the parent of C (A → B → C):**
If the state update happens in **A**, the sequence is: **A re-renders → then B re-renders → then C re-renders** (top-down through the subtree). React re-runs A's function first, then its children in order.

**Case 2 — A, B, C are siblings under a common parent:**
If **A** owns the state that changed and B/C are *not* descendants of A, then **only A re-renders**. B and C do **not** re-render, because a sibling's state change doesn't affect them (they're not in A's subtree, and their props didn't change).

- **Important nuance:** child re-renders happen because the parent re-rendered, **not** necessarily because props changed. To *stop* B or C from re-rendering when their props didn't actually change, wrap them in **`React.memo`** (then React shallow-compares props and skips them).
- **Order guarantee:** React renders **parent first, then children, depth-first**. Effects (`useEffect`) then run **bottom-up** (child effects before parent effects) after the DOM is committed.
- **One-liner:** "A state update in A re-renders A and everything below it, top-down (A → B → C if nested); siblings not under A won't re-render. `React.memo` can prune children whose props didn't change."

## IQ13. What are the ways to bypass (skip re-rendering of) components?
"Bypass" = prevent a component from re-rendering unnecessarily. Techniques:
- **`React.memo`** — wraps a function component; skips re-render when props are shallow-equal to the previous render.
- **`PureComponent`** — the class-component equivalent (auto shallow-compares props + state in `shouldComponentUpdate`).
- **`shouldComponentUpdate(nextProps, nextState)`** — in class components, return `false` to skip a re-render manually with custom logic.
- **`useMemo` / `useCallback`** — stabilize the values/functions you pass down so memoized children actually get to skip (otherwise new references defeat `React.memo`).
- **State colocation** — keep state as low in the tree as possible so fewer components sit in the re-rendering subtree.
- **`children` / composition trick** — pass expensive subtrees as `children` from a parent that doesn't re-render, so React reuses the same element and skips re-rendering them:
  ```jsx
  <Layout><ExpensiveTree /></Layout>  // ExpensiveTree won't re-render when Layout's own state changes
  ```
- **Selector-based state (Redux `useSelector` / Zustand)** — only components subscribed to the changed slice re-render.
- **Split contexts** — so a context update only re-renders the consumers that need that specific value.
- **One-liner:** "`React.memo`/`PureComponent` + stable references (`useMemo`/`useCallback`) + smart state placement and the `children` pattern let you bypass unnecessary re-renders."

## IQ14. Explain component composition in ReactJS.
- **Definition:** building complex UIs by **combining smaller components together**, rather than using inheritance. React's official guidance: **"composition over inheritance."**
- **Main techniques:**
  - **`children` prop / containment** — a component wraps whatever you put inside it, acting as a flexible container:
    ```jsx
    function Card({ children }) { return <div className="card">{children}</div>; }
    <Card><h2>Title</h2><p>Body</p></Card>
    ```
  - **Specialization via props / slots** — pass JSX into named props for flexible layouts:
    ```jsx
    <Dialog header={<Title/>} footer={<Actions/>} />
    ```
  - **Compound components** — a set of components that share implicit state to give a clean API (e.g., `<Tabs><Tab/><TabPanel/></Tabs>`).
  - **Container/Presentational split** — one component fetches/manages data, another purely renders from props.
  - **Custom hooks** — compose and share *logic* (not UI), the modern replacement for HOCs and render props.
- **Why it matters:** composition keeps components small, focused, reusable, and testable, and avoids the rigidity of deep inheritance hierarchies.
- **One-liner:** "In React you snap small components together (via `children`, slots, compound components) instead of extending classes — composition over inheritance."

## IQ15. What is Redux in ReactJS?
- **Definition:** Redux is a **predictable state-management library** that holds all your app's shared state in a single central **store**, with strict rules for how state can change so updates are traceable and debuggable.
- **Core concepts:**
  - **Store** — the single source of truth (one big state object).
  - **Action** — a plain object describing *what happened*: `{ type: 'cart/addItem', payload: item }`.
  - **Reducer** — a **pure function** `(state, action) => newState` that returns a *new* state without mutating the old one.
  - **Dispatch** — `dispatch(action)` sends an action to the store, which runs the reducer.
  - **Selector** — reads a slice of state (`useSelector`) so a component only re-renders when *its* data changes.
- **The one-way flow:** component `dispatch`es an action → reducer computes new state → subscribed components re-render.
- **Why:** predictable state, great **DevTools** (time-travel debugging), and a single place to reason about state in large apps.
- **When to use:** big apps with lots of shared client state and complex update logic. For server data, prefer **React Query**; for small shared state, Context/Zustand may be enough.

## IQ16. What is Redux Toolkit (RTK)?
- **Definition:** the **official, recommended way to write Redux today**. It's a wrapper around Redux that removes the historic boilerplate and bakes in best practices.
- **Key APIs:**
  - **`configureStore`** — sets up the store with good defaults (DevTools, `redux-thunk` middleware, and immutability/serializability checks) in one call.
  - **`createSlice`** — defines a slice's **state + reducers + auto-generated action creators** in one place. It uses **Immer** under the hood, so you can write "mutating" code (`state.value += 1`) that's actually applied immutably.
  - **`createAsyncThunk`** — handles async logic (API calls) with automatic **pending / fulfilled / rejected** action states.
  - **RTK Query** — a built-in data-fetching + caching layer (a React Query-style solution inside Redux).
```js
const counterSlice = createSlice({
  name: 'counter',
  initialState: { value: 0 },
  reducers: {
    increment: (state) => { state.value += 1; },     // Immer makes this safe
    addBy: (state, action) => { state.value += action.payload; },
  },
});
export const { increment, addBy } = counterSlice.actions;
```
- **One-liner:** "RTK is modern Redux — `createSlice` + `configureStore` eliminate boilerplate, Immer lets you write mutating-looking immutable updates, and `createAsyncThunk`/RTK Query handle async and caching."

## IQ17. Redux vs Redux Toolkit — what's the difference?
| Aspect | Classic Redux | Redux Toolkit (RTK) |
|---|---|---|
| **Boilerplate** | Lots — manual action types, action creators, switch-based reducers, store setup | Minimal — `createSlice` generates actions + reducers automatically |
| **Store setup** | Manual `createStore` + wiring middleware/DevTools | One `configureStore` call with sensible defaults |
| **Immutability** | You must manually return new state (`{...state}`) | **Immer** lets you write "mutating" code safely |
| **Async** | Add `redux-thunk`/`redux-saga` yourself | `createAsyncThunk` built in; RTK Query for data fetching |
| **Best practices** | Up to you | Baked in (serializability & immutability checks) |
| **Recommendation** | Legacy | **Official recommended approach** |
- **Bottom line:** Redux Toolkit *is* Redux — same core concepts (store, actions, reducers, dispatch) — just with far less code and best practices built in. Classic Redux is what you'll see in older codebases.
- **One-liner:** "Same Redux under the hood; RTK just removes the pain — less boilerplate, Immer-powered updates, and built-in async/caching. Always use RTK for new projects."

## IQ18. How do you add Redux Toolkit to a project?
Step-by-step:
1. **Install the packages:**
   ```bash
   npm install @reduxjs/toolkit react-redux
   ```
2. **Create a slice** (state + reducers + auto actions):
   ```js
   // features/counter/counterSlice.js
   import { createSlice } from '@reduxjs/toolkit';
   const counterSlice = createSlice({
     name: 'counter',
     initialState: { value: 0 },
     reducers: {
       increment: (state) => { state.value += 1; },
       addBy: (state, action) => { state.value += action.payload; },
     },
   });
   export const { increment, addBy } = counterSlice.actions;
   export default counterSlice.reducer;
   ```
3. **Configure the store:**
   ```js
   // app/store.js
   import { configureStore } from '@reduxjs/toolkit';
   import counterReducer from '../features/counter/counterSlice';
   export const store = configureStore({
     reducer: { counter: counterReducer },
   });
   ```
4. **Provide the store to React** (wrap the app):
   ```jsx
   import { Provider } from 'react-redux';
   import { store } from './app/store';
   root.render(<Provider store={store}><App /></Provider>);
   ```
5. **Use it in components** with the `react-redux` hooks:
   ```jsx
   import { useSelector, useDispatch } from 'react-redux';
   import { increment } from '../features/counter/counterSlice';
   const value = useSelector((state) => state.counter.value);
   const dispatch = useDispatch();
   <button onClick={() => dispatch(increment())}>{value}</button>
   ```
- **One-liner:** "Install `@reduxjs/toolkit` + `react-redux`, create a slice, configure the store, wrap the app in `<Provider>`, then read with `useSelector` and update with `useDispatch`."

## IQ19. Why do we add react-redux?
- **The problem it solves:** Redux itself is **framework-agnostic** — it's just a state container. **`react-redux`** is the **official binding library that connects Redux to React**.
- **What it provides:**
  - **`<Provider store={store}>`** — makes the Redux store available to the entire component tree via React Context (so you don't pass the store manually everywhere).
  - **`useSelector(selectorFn)`** — subscribes a component to a *slice* of the store; the component re-renders **only when that selected value changes** (not on every store update).
  - **`useDispatch()`** — gives you the `dispatch` function to send actions.
- **Performance benefit:** `react-redux` optimizes subscriptions and does referential comparisons so components re-render efficiently — you get fine-grained updates instead of the whole tree re-rendering on any state change.
- **One-liner:** "Redux is the store; **react-redux is the glue** that plugs it into React via `<Provider>`, `useSelector`, and `useDispatch`, with optimized subscriptions so only affected components re-render."

## IQ20. What is SSR (Server-Side Rendering) in ReactJS?
- **Definition:** with **SSR**, React renders the components to **HTML on the server** for each request and sends that fully-formed HTML to the browser. The browser shows content immediately, then React **hydrates** it (attaches event handlers) to make it interactive.
- **Contrast with CSR (client-side rendering):** a normal React SPA sends a nearly empty HTML page plus a JS bundle; the browser must download and run the JS before *anything* appears (blank screen first, poor SEO).
- **Benefits of SSR:**
  - **Better SEO** — crawlers see fully-rendered HTML with content.
  - **Faster First Contentful Paint** — users see content before the JS bundle finishes loading.
  - **Better for social sharing** (Open Graph meta tags rendered server-side).
- **Costs / trade-offs:**
  - **Higher server load** — HTML is rendered per request.
  - **Slower TTFB** (time to first byte) compared to static.
  - **Hydration cost/mismatch** — server HTML and the client's first render must match, or you get hydration warnings/bugs (avoid non-deterministic values like `Date.now()`/`Math.random()` during render).
- **How you do it:** typically with **Next.js** (`getServerSideProps`, or the App Router's server components), which handles SSR, routing, and bundling for you. Raw React offers `renderToString`/`renderToPipeableStream` + `hydrateRoot`, but frameworks are the practical choice.
- **Related modes:** **SSG** (pre-render at build time — fastest, static), **ISR** (SSG + periodic regeneration). Choose per page based on freshness and SEO needs.
- **One-liner:** "SSR renders React to HTML on the server per request for fast first paint and good SEO, then hydrates on the client — usually via Next.js; the trade-off is server cost and hydration care."

## IQ21. Can the React lifecycle be achieved in a component? (class component lifecycle)
Yes — in **class components** the lifecycle is explicit via lifecycle methods, grouped into three phases:
- **Mounting (component created & inserted):**
  - `constructor()` — initialize state, bind methods.
  - `render()` — return JSX.
  - `componentDidMount()` — runs **after** first render; ideal for **data fetching, subscriptions, timers**.
- **Updating (props/state change):**
  - `shouldComponentUpdate(nextProps, nextState)` — return `false` to skip a re-render (performance).
  - `render()` — re-render.
  - `componentDidUpdate(prevProps, prevState)` — react to changes (e.g., re-fetch when a prop changed).
- **Unmounting (component removed):**
  - `componentWillUnmount()` — **cleanup**: clear timers, close WebSockets, unsubscribe.
- **Error handling:** `getDerivedStateFromError` / `componentDidCatch` (Error Boundaries).
- **One-liner:** "Class components expose the lifecycle directly: `componentDidMount` (setup), `componentDidUpdate` (react to changes), `componentWillUnmount` (cleanup)."

## IQ22. Can the React lifecycle be achieved in a functional component?
**Yes — entirely, using the `useEffect` hook** (plus a few others). Functional components don't have named lifecycle methods, but `useEffect` covers all lifecycle phases based on its **dependency array**:
- **`componentDidMount` (run once on mount):**
  ```jsx
  useEffect(() => { fetchData(); }, []);   // empty deps → runs once after first render
  ```
- **`componentDidUpdate` (run on specific changes):**
  ```jsx
  useEffect(() => { refetch(id); }, [id]); // runs whenever `id` changes
  ```
- **`componentWillUnmount` (cleanup):**
  ```jsx
  useEffect(() => {
    const ws = new WebSocket(url);
    return () => ws.close();              // cleanup runs on unmount (and before re-run)
  }, [url]);
  ```
- **Run after every render:** `useEffect(() => {...})` with **no** dependency array.
- **Other hooks that map to lifecycle-ish needs:**
  - **`useLayoutEffect`** — synchronous, before paint (DOM measurement) — closer to `componentDidMount`/`componentDidUpdate` timing before the browser paints.
  - **`useMemo`/`useCallback`** — optimization akin to `shouldComponentUpdate` (with `React.memo`).
- **Key mental model:** one `useEffect` keeps **related setup + cleanup together** (unlike classes, which split them across `componentDidMount` and `componentWillUnmount`). You can also use **multiple `useEffect`s** to separate unrelated concerns.
- **One-liner:** "Yes — `useEffect` covers mount (`[]`), update (`[deps]`), and unmount (cleanup return) in one place; `useLayoutEffect` handles pre-paint timing. It's the hooks equivalent of the class lifecycle."
