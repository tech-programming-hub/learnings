# 16 — Angular (Frontend Framework)

> Anchor: Your resume shows deep Angular experience — you built **Angular PQM frontend modules at BMW** (real-time quality-defect visualization), **Angular booking/rebooking/ancillary modules at Air Canada**, and **Angular observability modules at MGM** alongside React. Angular is a first-class skill on your resume, so expect dedicated Angular questions. Speak from real module-building experience.

> 📘 **How to read this file:** Every answer has layers — **(1) Simple idea** (plain-English so you "get it"), **(2) Deeper explanation** (interview-ready detail), and **(3) Example / talking point**. Read the Simple idea first.

---

## A. Angular Fundamentals

### Q1. What is Angular? Key features?

**🟢 Simple idea:** Angular is a **complete, opinionated frontend framework** (not just a library like React) built by Google, using **TypeScript**. It gives you *everything* out of the box — routing, forms, HTTP, dependency injection — so you don't assemble your own stack.

**🔵 Deeper explanation:**
Angular is a **full framework** — batteries included. Where React is "just the view layer and you pick the rest," Angular ships with official solutions for almost everything:
- **Component-based architecture** — UI built from components (each has a TypeScript class, an HTML template, and CSS styles).
- **TypeScript-first** — Angular is written in and designed for TypeScript (strong typing, decorators).
- **Dependency Injection (DI)** — a powerful built-in DI system (like Spring in the Java world) that provides services to components.
- **Two-way data binding** — `[(ngModel)]` syncs the view and the model automatically.
- **RxJS / Observables** — reactive programming built into HTTP, forms, and router.
- **Angular CLI** — a powerful command-line tool to scaffold, build, test, and serve.
- **Modules (`NgModule`)** — organize the app into cohesive blocks (in older Angular; newer versions favor **standalone components**).
- **Built-in Router, Forms, HttpClient, Animations.**

**💬 Interview one-liner:** "Angular is Google's complete, opinionated, TypeScript-based framework — component architecture, dependency injection, RxJS, and a full toolchain out of the box. React is a library; Angular is a framework."

---

### Q2. Angular vs React — the key differences?

**🟢 Simple idea:** Angular is a **full framework** (everything decided for you); React is a **library** (you choose your own tools). Both build component-based UIs.

**🔵 Deeper explanation (comparison table):**

| Aspect | Angular | React |
|---|---|---|
| **Type** | Full framework (opinionated) | Library (view layer only) |
| **Language** | TypeScript (mandatory) | JavaScript/TypeScript (optional) |
| **DOM** | Real DOM + change detection (Zone.js) | Virtual DOM + diffing |
| **Data binding** | Two-way (`[(ngModel)]`) + one-way | One-way only |
| **DI** | Built-in, powerful | Not built-in (use Context/libs) |
| **Routing** | Official Angular Router | React Router (3rd party) |
| **State** | Services + RxJS (or NgRx) | Redux/Zustand/Context (3rd party) |
| **Forms** | Built-in (Template & Reactive Forms) | 3rd party (react-hook-form) |
| **Learning curve** | Steeper (more concepts) | Gentler core, choices add complexity |
| **HTTP** | Built-in HttpClient + RxJS | fetch/axios (3rd party) |

- **When to use Angular:** large enterprise apps, teams wanting consistency and a prescribed structure, strong typing culture. (Your BMW/Air Canada enterprise apps fit this.)
- **When to use React:** flexibility, lighter footprint, freedom to pick tools, huge ecosystem.

**💬 One-liner:** "Angular gives you a complete, consistent framework great for large enterprise teams; React gives you flexibility and a lighter core but you assemble the rest. I've shipped production apps in both."

---

### Q3. What is a component in Angular? What are its building blocks?

**🟢 Simple idea:** A component is a reusable UI piece made of **three parts**: a TypeScript **class** (logic/data), an HTML **template** (view), and **CSS** (styling), tied together by the `@Component` decorator.

**🔵 Deeper explanation:**
```typescript
@Component({
  selector: 'app-defect-card',          // how you use it: <app-defect-card>
  templateUrl: './defect-card.html',    // the view
  styleUrls: ['./defect-card.css'],     // the styles
})
export class DefectCardComponent {
  @Input() defect!: Defect;             // data coming IN from parent
  @Output() resolved = new EventEmitter<string>();  // events going OUT to parent

  markResolved() {
    this.resolved.emit(this.defect.id);
  }
}
```
- **`@Component` decorator** — metadata: the selector (tag name), template, and styles.
- **Class** — holds properties (data) and methods (behavior).
- **`@Input()`** — receives data from a parent (like React props).
- **`@Output()` + `EventEmitter`** — sends events up to the parent.
- **Template** — HTML with Angular binding syntax (`{{ }}`, `[ ]`, `( )`, `*ngIf`, `*ngFor`).

**💬 Talking point:** "At BMW, I built defect-visualization components with `@Input` for defect data and `@Output` to emit resolution events to parent containers."

---

### Q4. Explain Angular data binding types.

**🟢 Simple idea:** Data binding connects your component's data to the template. Angular has **four** kinds, distinguished by the direction of data flow and the bracket syntax.

**🔵 Deeper explanation:**
1. **Interpolation `{{ value }}`** — component → view. Renders a value as text.
   ```html
   <h1>{{ title }}</h1>
   ```
2. **Property binding `[property]="value"`** — component → view. Binds to an element/DOM property.
   ```html
   <img [src]="imageUrl">
   <button [disabled]="isSaving">Save</button>
   ```
3. **Event binding `(event)="handler()"`** — view → component. Responds to user events.
   ```html
   <button (click)="save()">Save</button>
   ```
4. **Two-way binding `[(ngModel)]="value"`** — both directions. Syncs input and model (the "banana in a box" syntax `[()]`).
   ```html
   <input [(ngModel)]="searchText">
   ```
   Two-way binding is really property binding + event binding combined: `[(ngModel)]` = `[ngModel]` + `(ngModelChange)`.

**💬 One-liner:** "Interpolation and property binding push data to the view; event binding pushes user actions back; `[(ngModel)]` does both — it's the 'banana in a box.'"

---

### Q5. What are directives in Angular? Types?

**🟢 Simple idea:** Directives are instructions that tell Angular to **change the DOM** — add/remove elements, change their appearance, or attach behavior. There are three types.

**🔵 Deeper explanation:**
1. **Component directives** — directives with a template (components *are* directives with a view). The most common type.
2. **Structural directives** — **change the DOM layout** by adding/removing elements. They have a `*` prefix:
   - `*ngIf` — conditionally include an element.
   - `*ngFor` — repeat an element for each item in a list.
   - `*ngSwitch` — switch between elements.
   ```html
   <div *ngIf="isLoading">Loading...</div>
   <li *ngFor="let d of defects; trackBy: trackById">{{ d.name }}</li>
   ```
3. **Attribute directives** — **change the appearance/behavior** of an existing element without altering the DOM structure:
   - `ngClass` — add/remove CSS classes conditionally.
   - `ngStyle` — set inline styles dynamically.
   - Custom directives (e.g., a `highlight` directive).
   ```html
   <div [ngClass]="{ 'critical': defect.severity === 'high' }">...</div>
   ```

- **Modern Angular (v17+)** introduced new **built-in control flow** (`@if`, `@for`, `@switch`) that replaces `*ngIf`/`*ngFor` with cleaner syntax and better performance.

**💬 Talking point:** "I used `*ngFor` with `trackBy` for large defect lists to avoid re-rendering unchanged rows — the Angular equivalent of React keys."

---

### Q6. What is `trackBy` in `*ngFor` and why is it important?

**🟢 Simple idea:** `trackBy` tells Angular how to **identify each list item uniquely** (like React's `key`), so when the list changes, Angular only updates the items that actually changed instead of re-rendering the whole list.

**🔵 Deeper explanation:**
Without `trackBy`, Angular tracks list items by **object identity**. If you replace the array (e.g., after an API refresh), Angular thinks *every* item is new and destroys/recreates all DOM nodes — slow and it loses element state.
```typescript
trackById(index: number, defect: Defect): string {
  return defect.id;   // stable unique identifier
}
```
```html
<li *ngFor="let d of defects; trackBy: trackById">{{ d.name }}</li>
```
With `trackBy`, Angular matches items by their ID and only touches the changed ones.

**💬 One-liner:** "`trackBy` is Angular's version of React keys — it prevents needless DOM re-creation on list updates. Essential for the large real-time lists I built at BMW/MGM."

---

## B. Services, Dependency Injection & Modules

### Q7. What is Dependency Injection (DI) in Angular?

**🟢 Simple idea:** Instead of a component creating its own dependencies (like a service), Angular **creates and hands them in** automatically. You just ask for what you need in the constructor, and Angular provides it — exactly like Spring's DI in Java.

**🔵 Deeper explanation:**
```typescript
@Injectable({ providedIn: 'root' })   // registers the service app-wide (singleton)
export class DefectService {
  constructor(private http: HttpClient) {}   // HttpClient injected by Angular
  getDefects() { return this.http.get<Defect[]>('/api/defects'); }
}

@Component({...})
export class DefectListComponent {
  constructor(private defectService: DefectService) {}  // service injected here
}
```
- **`@Injectable({ providedIn: 'root' })`** — registers the service in the root injector, making it an app-wide **singleton** (one shared instance).
- **How it works:** Angular maintains a hierarchical **injector tree**. When a component asks for a dependency, Angular walks up the tree to find a registered provider and injects the instance.
- **Benefits:** loose coupling, easy testing (inject mocks), reusability, single source of truth (shared state via singleton services).

**💬 Talking point:** "Angular's DI felt very natural coming from Spring Boot — `@Injectable` is like `@Service`, and constructor injection is identical. I shared state across components via `providedIn: 'root'` singleton services."

---

### Q8. What is the difference between an Angular Module (`NgModule`) and a standalone component?

**🟢 Simple idea:** Historically, Angular grouped components into **modules** (`NgModule`) to organize the app. Newer Angular (v14+) introduced **standalone components** that don't need modules at all — simpler and the modern default.

**🔵 Deeper explanation:**
- **`NgModule` (classic):** a container that declares components, imports other modules, and provides services:
  ```typescript
  @NgModule({
    declarations: [DefectListComponent, DefectCardComponent],
    imports: [CommonModule, HttpClientModule, FormsModule],
    providers: [DefectService],
    exports: [DefectListComponent],
  })
  export class DefectModule {}
  ```
- **Standalone components (modern, v14+):** a component declares its own dependencies directly, no module needed:
  ```typescript
  @Component({
    selector: 'app-defect-list',
    standalone: true,
    imports: [CommonModule, DefectCardComponent],  // imports directly
    templateUrl: './defect-list.html',
  })
  export class DefectListComponent {}
  ```
- **Why standalone is better:** less boilerplate, easier lazy loading, clearer dependencies, and the recommended approach going forward.

**💬 One-liner:** "Modules were the classic way to organize Angular; standalone components (v14+) remove that boilerplate and are now the recommended default."

---

### Q9. How do you share data/state between components in Angular?

**🟢 Simple idea:** Several ways depending on the relationship: `@Input`/`@Output` for parent-child, a **shared service** (with RxJS) for unrelated components, or **NgRx** for complex global state.

**🔵 Deeper explanation:**
1. **Parent → child:** `@Input()` (pass data down).
2. **Child → parent:** `@Output()` + `EventEmitter` (emit events up).
3. **Unrelated components — a shared service with a `BehaviorSubject`** (the most common pattern):
   ```typescript
   @Injectable({ providedIn: 'root' })
   export class FilterService {
     private filter$ = new BehaviorSubject<string>('');
     filter = this.filter$.asObservable();     // components subscribe
     setFilter(value: string) { this.filter$.next(value); }  // components update
   }
   ```
   Any component can inject `FilterService`, call `setFilter()` to update, and subscribe to `filter` to react — a reactive shared state.
4. **NgRx (Redux for Angular)** — for large apps with complex, shared state: a central store, actions, reducers, effects, and selectors.

**💬 Talking point:** "For cross-component state in my Angular modules I used singleton services with `BehaviorSubject` — components subscribe and stay in sync reactively. For very large state I'd reach for NgRx."

---

## C. RxJS & Observables

### Q10. What is RxJS and what are Observables in Angular?

**🟢 Simple idea:** RxJS is a library for handling **asynchronous data streams** — things that arrive over time (HTTP responses, user events, WebSocket messages). An **Observable** is a stream you can **subscribe** to, and it pushes values to you as they arrive.

**🔵 Deeper explanation:**
Angular uses RxJS heavily — `HttpClient`, the router, and reactive forms all return Observables.
- **Observable** — a "stream" of values over time. Nothing happens until you **subscribe**.
- **Observer/subscriber** — reacts to emitted values, errors, and completion.
- **Operators** — functions to transform streams (`map`, `filter`, `switchMap`, `debounceTime`, `mergeMap`, `catchError`).
```typescript
this.defectService.getDefects()
  .pipe(
    map(defects => defects.filter(d => d.severity === 'high')),
    catchError(err => { console.error(err); return of([]); })
  )
  .subscribe(defects => this.defects = defects);
```
- **`Subject` / `BehaviorSubject`** — special Observables that are both a stream *and* an emitter; used for cross-component state.
- **Key operators to know:**
  - **`switchMap`** — cancel previous inner Observable and switch to a new one (great for search-as-you-type — cancels stale requests).
  - **`debounceTime`** — wait for a pause before emitting (search input).
  - **`mergeMap`/`concatMap`** — flatten inner Observables (parallel vs sequential).
  - **`combineLatest`/`forkJoin`** — combine multiple streams.

**💬 Talking point:** "For the real-time defect dashboards I used RxJS with `switchMap` for search (canceling stale requests) and `debounceTime` on filters — the reactive model handled live streams cleanly."

---

### Q11. Observable vs Promise — what's the difference?

**🟢 Simple idea:** A **Promise** handles **one** future value. An **Observable** handles a **stream of many** values over time and can be **cancelled**.

**🔵 Deeper explanation (table):**

| Aspect | Promise | Observable |
|---|---|---|
| **Values** | Single value | Multiple values over time (a stream) |
| **Eager/Lazy** | Eager (runs immediately) | Lazy (runs only when subscribed) |
| **Cancellable** | No | Yes (`unsubscribe()`) |
| **Operators** | None (just `.then`) | Rich (map, filter, switchMap, etc.) |
| **Retry** | Manual | Built-in (`retry`, `retryWhen`) |

- **Practical impact:** Observables can be **cancelled** — crucial for search-as-you-type (cancel stale HTTP calls with `switchMap`) and for avoiding memory leaks when a component is destroyed.

**💬 One-liner:** "Promise = one value, eager, not cancellable. Observable = a stream, lazy, cancellable, with powerful operators — that's why Angular is built on RxJS."

---

### Q12. How do you avoid memory leaks with Observables (unsubscribing)?

**🟢 Simple idea:** If you subscribe to an Observable and never unsubscribe, it keeps running even after the component is destroyed — a **memory leak**. You must clean up subscriptions.

**🔵 Deeper explanation — the common approaches:**
1. **`async` pipe (best)** — let Angular subscribe/unsubscribe automatically in the template:
   ```html
   <li *ngFor="let d of defects$ | async">{{ d.name }}</li>
   ```
   The `async` pipe subscribes when the component renders and **auto-unsubscribes** on destroy. This is the cleanest, preferred way.
2. **`takeUntil` pattern** — unsubscribe on a "destroy" signal:
   ```typescript
   private destroy$ = new Subject<void>();
   ngOnInit() {
     this.service.getDefects()
       .pipe(takeUntil(this.destroy$))
       .subscribe(d => this.defects = d);
   }
   ngOnDestroy() { this.destroy$.next(); this.destroy$.complete(); }
   ```
3. **Manual unsubscribe** — store the `Subscription` and call `.unsubscribe()` in `ngOnDestroy()` (verbose, error-prone).
4. **`takeUntilDestroyed()`** (Angular 16+) — a new helper that ties unsubscription to the component lifecycle automatically.

**💬 One-liner:** "Prefer the `async` pipe (auto-unsubscribes); for imperative subscriptions use `takeUntil(destroy$)` or `takeUntilDestroyed()`. Never leave HTTP/stream subscriptions dangling."

---

## D. Lifecycle, Change Detection & Performance

### Q13. Explain the Angular component lifecycle hooks.

**🟢 Simple idea:** Angular calls specific methods at key moments in a component's life — creation, updates, and destruction — so you can run code at the right time.

**🔵 Deeper explanation (in order):**
- **`ngOnChanges(changes)`** — called when an `@Input` value changes (before `ngOnInit` and on every input change).
- **`ngOnInit()`** — called **once** after the first `ngOnChanges`; ideal for **initialization and data fetching** (like `componentDidMount` in React).
- **`ngDoCheck()`** — custom change detection; runs on every change-detection cycle (use sparingly).
- **`ngAfterContentInit()` / `ngAfterContentChecked()`** — after projected content (`<ng-content>`) is initialized/checked.
- **`ngAfterViewInit()` / `ngAfterViewChecked()`** — after the component's view (and child views) are initialized/checked; use for DOM access via `@ViewChild`.
- **`ngOnDestroy()`** — called **once** just before the component is destroyed; ideal for **cleanup** (unsubscribe, clear timers) — like `componentWillUnmount`.

```typescript
export class DefectListComponent implements OnInit, OnDestroy {
  ngOnInit() { this.loadDefects(); }         // fetch on init
  ngOnDestroy() { this.destroy$.next(); }    // cleanup subscriptions
}
```

**💬 One-liner:** "`ngOnInit` for setup/data fetching, `ngOnChanges` for input changes, `ngOnDestroy` for cleanup — the three you use most. They map closely to React's mount/update/unmount."

---

### Q14. What is change detection in Angular? How does it work?

**🟢 Simple idea:** Change detection is how Angular figures out **what data changed** and updates the DOM to match. By default, whenever *anything* async happens (a click, HTTP response, timer), Angular checks the whole component tree.

**🔵 Deeper explanation:**
- **Zone.js** — Angular uses Zone.js to **monkey-patch** async APIs (events, `setTimeout`, HTTP, promises). When any of these fire, Zone.js notifies Angular to run change detection.
- **Default strategy (`ChangeDetectionStrategy.Default`)** — Angular checks **every component** in the tree top-down on each cycle, comparing template-bound values. Simple but can be wasteful in big apps.
- **OnPush strategy (`ChangeDetectionStrategy.OnPush`)** — a component is checked **only when**:
  1. An `@Input` **reference** changes (not mutation — new reference).
  2. An event fires from the component or its children.
  3. An Observable bound with `async` pipe emits.
  4. You manually trigger it (`markForCheck()`).
  ```typescript
  @Component({
    selector: 'app-defect-card',
    changeDetection: ChangeDetectionStrategy.OnPush,  // big perf win
    ...
  })
  ```
- **Why OnPush matters:** it drastically reduces the number of checks, which is critical for large/real-time UIs. It requires **immutable data** (pass new references, don't mutate objects) — same discipline as React.
- **Modern Angular (v17+):** introduced **Signals** — a fine-grained reactivity system that will eventually make Zone.js optional ("zoneless") and change detection far more surgical.

**💬 Talking point:** "For the high-frequency defect/health dashboards, I used `OnPush` change detection with immutable data updates and the `async` pipe — this kept the UI fast under constant updates, the Angular equivalent of `React.memo` + stable references."

---

### Q15. What are Angular Signals (modern Angular)?

**🟢 Simple idea:** Signals (Angular v16+) are a new way to hold reactive state — a value that **notifies Angular precisely when it changes**, so Angular can update only the exact parts of the DOM that depend on it (fine-grained, no whole-tree checks).

**🔵 Deeper explanation:**
```typescript
count = signal(0);                         // a writable signal
double = computed(() => this.count() * 2); // derived signal, auto-updates

increment() { this.count.update(c => c + 1); }  // or this.count.set(5)
```
```html
<p>{{ count() }} — doubled: {{ double() }}</p>
```
- **`signal(value)`** — a reactive container; read with `count()`, write with `.set()`/`.update()`.
- **`computed()`** — a derived value that recalculates automatically when its dependencies change (like `useMemo`).
- **`effect()`** — runs side effects when signals it reads change.
- **Why it's a big deal:** signals enable **fine-grained reactivity** — Angular knows exactly which DOM nodes depend on which signal, so it can eventually drop Zone.js ("zoneless") and do far less work. It's Angular's answer to modern reactive frameworks (Solid, Vue).

**💬 One-liner:** "Signals are Angular's new fine-grained reactivity primitive — `signal`, `computed`, `effect` — enabling surgical DOM updates and a future zoneless Angular. Conceptually similar to React's `useState`/`useMemo` but with precise dependency tracking."

---

### Q16. How do you optimize Angular performance?

**🟢 Simple idea:** Reduce how often Angular checks/re-renders, and ship less code to the browser.

**🔵 Deeper explanation — the main levers:**
- **`OnPush` change detection** — check components only when inputs change by reference (huge win for big trees).
- **`trackBy` in `*ngFor`** — avoid re-creating DOM for unchanged list items.
- **`async` pipe** — auto-manages subscriptions and works well with OnPush.
- **Lazy loading routes** — load feature modules/components only when the route is visited (smaller initial bundle):
  ```typescript
  { path: 'defects', loadComponent: () => import('./defects/defect-list.component').then(m => m.DefectListComponent) }
  ```
- **Signals (v16+)** — fine-grained updates instead of whole-tree checks.
- **`ChangeDetectorRef.detach()` / `markForCheck()`** — manual control for extreme cases.
- **Pure pipes** — cached transformations (only recompute when input changes).
- **Virtual scrolling** (`cdk-virtual-scroll-viewport` from Angular CDK) — render only visible rows in huge lists.
- **AOT compilation** — Ahead-of-Time compiles templates at build time (default in production; faster, smaller, safer).
- **`ng build --prod`** — tree-shaking, minification, bundle optimization.
- **Debounce user input** with RxJS `debounceTime`.

**💬 Talking point:** "For real-time dashboards I combined OnPush + `trackBy` + `async` pipe + virtual scrolling (CDK) + lazy-loaded routes — controlling change detection is the core of Angular performance, just like controlling re-renders in React."

---

## E. Forms, Routing & HTTP

### Q17. Template-driven vs Reactive Forms in Angular?

**🟢 Simple idea:** Two ways to build forms. **Template-driven** = simple, logic in the HTML template (good for small forms). **Reactive** = logic in the TypeScript class (better for complex forms, validation, and testing).

**🔵 Deeper explanation:**
- **Template-driven forms** — use `ngModel` and directives in the template; Angular builds the form model implicitly. Simple but less scalable.
  ```html
  <form #f="ngForm">
    <input name="email" [(ngModel)]="email" required email>
  </form>
  ```
- **Reactive forms** — you define the form model explicitly in the class with `FormGroup`/`FormControl`; more powerful, testable, and dynamic:
  ```typescript
  form = new FormGroup({
    email: new FormControl('', [Validators.required, Validators.email]),
    severity: new FormControl('low'),
  });
  ```
  ```html
  <form [formGroup]="form" (ngSubmit)="submit()">
    <input formControlName="email">
    <span *ngIf="form.get('email')?.invalid">Invalid email</span>
  </form>
  ```
- **When to use which:** Template-driven for simple forms; **Reactive for complex, dynamic forms** with custom/async validation, dynamic controls, and unit testing (the enterprise choice).

**💬 One-liner:** "Template-driven forms live in the HTML (simple); Reactive forms live in the TypeScript class (powerful, testable) — for enterprise forms with complex validation I use Reactive Forms."

---

### Q18. How does routing work in Angular?

**🟢 Simple idea:** The Angular Router maps **URLs to components**, swapping views without a full page reload (a Single Page Application). You define a route table and use `<router-outlet>` as the placeholder where matched components render.

**🔵 Deeper explanation:**
```typescript
const routes: Routes = [
  { path: '', component: HomeComponent },
  { path: 'defects', component: DefectListComponent },
  { path: 'defects/:id', component: DefectDetailComponent },   // route param
  {
    path: 'admin',
    loadChildren: () => import('./admin/admin.routes'),         // lazy loading
    canActivate: [authGuard],                                    // route guard
  },
  { path: '**', component: NotFoundComponent },                  // wildcard 404
];
```
```html
<a routerLink="/defects">Defects</a>
<router-outlet></router-outlet>   <!-- matched component renders here -->
```
- **Route params** — `:id`, read via `ActivatedRoute`.
- **`routerLink`** — navigation directive (no page reload).
- **Lazy loading** — `loadChildren`/`loadComponent` to load routes on demand (smaller initial bundle).
- **Route guards** — `canActivate`, `canDeactivate`, `canLoad` to protect routes (e.g., auth checks).
- **Resolvers** — pre-fetch data before a route activates.

**💬 Talking point:** "I used lazy-loaded feature routes with `canActivate` auth guards — the standard pattern for large Angular apps like the BMW PQM modules."

---

### Q19. What are Route Guards in Angular?

**🟢 Simple idea:** Guards are functions that decide **whether navigation is allowed** — e.g., block a page if the user isn't logged in, or warn before leaving a form with unsaved changes.

**🔵 Deeper explanation:**
- **`CanActivate`** — can the user enter this route? (auth/permission check). Most common.
- **`CanDeactivate`** — can the user leave? (e.g., "You have unsaved changes — leave?").
- **`CanActivateChild`** — guards child routes.
- **`CanLoad` / `CanMatch`** — prevent lazy-loaded modules from even downloading if not allowed.
- **`Resolve`** — pre-fetch data before activating (not strictly a guard, but related).
```typescript
export const authGuard: CanActivateFn = (route, state) => {
  const auth = inject(AuthService);
  const router = inject(Router);
  return auth.isLoggedIn() ? true : router.createUrlTree(['/login']);
};
```

**💬 One-liner:** "Guards control navigation — `CanActivate` for auth, `CanDeactivate` for unsaved-changes warnings, `CanLoad` to stop unauthorized lazy modules from downloading."

---

### Q20. How do you make HTTP calls in Angular (HttpClient + interceptors)?

**🟢 Simple idea:** Use Angular's built-in **`HttpClient`**, which returns **Observables**. For cross-cutting concerns (auth tokens, error handling, logging), use **HTTP interceptors** that run on every request/response.

**🔵 Deeper explanation:**
```typescript
@Injectable({ providedIn: 'root' })
export class DefectService {
  constructor(private http: HttpClient) {}
  getDefects(): Observable<Defect[]> {
    return this.http.get<Defect[]>('/api/defects');
  }
  createDefect(d: Defect): Observable<Defect> {
    return this.http.post<Defect>('/api/defects', d);
  }
}
```
- **Interceptors** — middleware for every HTTP call. Common uses: attach JWT tokens, handle 401s (refresh/redirect), global error handling, logging, retry logic.
  ```typescript
  export const authInterceptor: HttpInterceptorFn = (req, next) => {
    const token = inject(AuthService).getToken();
    const authReq = req.clone({ setHeaders: { Authorization: `Bearer ${token}` } });
    return next(authReq);
  };
  ```
- **Error handling** — use RxJS `catchError` in the service or a global interceptor.
- **Best practice:** keep HTTP logic in **services**, not components; use the **`async` pipe** in templates to consume the Observables.

**💬 Talking point:** "I centralized auth-token attachment and global error handling in HTTP interceptors, kept all API calls in typed services returning Observables, and consumed them with the `async` pipe — clean separation and automatic subscription cleanup."

---

## F. Rapid-Fire Angular (quick explanations)

- **AOT vs JIT** — Ahead-of-Time compiles templates at **build time** (faster, smaller, default in prod); Just-in-Time compiles in the **browser** (dev only).
- **Pipes** — transform displayed values in templates (`{{ date | date:'short' }}`, `{{ price | currency }}`); **pure pipes** are cached, **impure** run every cycle.
- **`ng-content`** — content projection (like React's `children` / slots) — pass template content into a component.
- **`@ViewChild` / `@ContentChild`** — get references to child components/DOM elements or projected content.
- **Angular CLI** — `ng new`, `ng generate component`, `ng serve`, `ng build`, `ng test` — scaffolding and tooling.
- **NgRx** — Redux-style state management for Angular (Store, Actions, Reducers, Effects, Selectors) for large apps.
- **Zone.js** — patches async APIs to trigger change detection (being phased out via Signals/zoneless).
- **Standalone components** — modern Angular (v14+) — components without NgModules; the new default.
- **`async` pipe** — subscribes/unsubscribes to Observables automatically in templates (prevents leaks).
- **Angular Universal** — server-side rendering (SSR) for Angular (SEO, faster first paint).
- **Angular CDK** — Component Dev Kit: virtual scrolling, drag-drop, overlays, a11y primitives.
- **Testing** — Jasmine + Karma (unit), `TestBed` for component testing, Cypress/Playwright (e2e).
- **`HttpClient` returns Observables** — remember to consume with `async` pipe or unsubscribe.
- **Two-way binding syntax** — `[(ngModel)]` = "banana in a box" = property binding + event binding.
- **Signals (v16+)** — fine-grained reactivity (`signal`, `computed`, `effect`) enabling zoneless change detection.

---

## G. Angular — Tough / Senior Questions

### TQ1. How would you architect a large enterprise Angular app?
- **Feature-based structure** — organize by feature (e.g., `defects/`, `auth/`, `dashboard/`), each with its own components, services, and (lazy-loaded) routes.
- **Core / Shared separation** — a **CoreModule** (singletons: auth, interceptors, guards) loaded once, and a **SharedModule** (reusable dumb components, pipes, directives) imported where needed. (Or standalone components in modern Angular.)
- **Smart/dumb components** — container components handle data/services; presentational components take `@Input`/`@Output` only (testable, reusable).
- **Lazy loading** per feature route for smaller initial bundles.
- **State management** — services + RxJS for moderate state; **NgRx** for complex shared state.
- **Typed API layer** — services returning typed Observables; interceptors for cross-cutting concerns.
- **OnPush + Signals** for performance.
- **Talking point:** "This mirrors how I structured the BMW PQM Angular modules — feature-based, lazy-loaded, smart/dumb split, with a core module for auth/interceptors."

### TQ2. How do you handle real-time updates in Angular (your dashboards)?
- **WebSocket / SSE** stream → wrap it in an **RxJS Observable** (or a `Subject`).
- **Batch/throttle** incoming messages (`bufferTime`, `throttleTime`) before updating state — avoid updating on every message.
- **OnPush + immutable updates + `async` pipe** so only affected components re-check.
- **`trackBy`** on lists; **virtual scrolling** (CDK) for large tables.
- **Talking point:** "For MGM/BMW real-time defect and health dashboards, I streamed updates via RxJS, batched them with `bufferTime`, and rendered with OnPush + virtual scrolling — same 'control what updates and how often' philosophy as my React dashboards."

### TQ3. Angular change detection is slow — how do you debug and fix it?
- **Profile** with Angular DevTools (the profiler shows change-detection cycles and component render times).
- **Switch to `OnPush`** on heavy components and ensure **immutable data** (new references).
- **Move heavy work out of templates** (no function calls in bindings — they run every cycle; use pure pipes or precomputed values instead).
- **Use `trackBy`** on all large `*ngFor`s.
- **Detach change detection** for extremely high-frequency components and `markForCheck()` selectively.
- **Consider Signals** for fine-grained reactivity.
- **Talking point:** "The #1 culprit is method calls in templates and mutating data with default change detection — I fix it with OnPush + immutability + pure pipes + `trackBy`."

### TQ4. Coming from React, what maps to what in Angular?
| React | Angular |
|---|---|
| Component (function) | Component (class + `@Component`) |
| Props | `@Input()` |
| Callbacks up / lifting state | `@Output()` + `EventEmitter` |
| `useState` | class property / **Signal** |
| `useMemo` | `computed()` signal / pure pipe |
| `useEffect` | `ngOnInit` / `ngOnChanges` / `effect()` |
| `useContext` | Dependency Injection (services) |
| `React.memo` | `ChangeDetectionStrategy.OnPush` |
| `key` in lists | `trackBy` in `*ngFor` |
| Redux | NgRx |
| React Router | Angular Router |
| `children` | `<ng-content>` |
| Virtual DOM diffing | Zone.js change detection / Signals |
- **Talking point:** "The concepts map cleanly — I've shipped production apps in both, so I switch based on the project's needs, not personal preference."