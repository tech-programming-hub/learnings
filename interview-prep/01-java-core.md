# 01 — Java Core (Java 8–21, Collections, Concurrency, JVM)

> Anchor: You've worked with Java up to v21, high-concurrency systems, multithreading. Speak with authority here.

---

## A. Java Fundamentals & OOP

### Q1. Difference between JDK, JRE, and JVM?
Think of it as three nested layers — the JVM is inside the JRE, which is inside the JDK.
- **JVM (Java Virtual Machine)** is the engine that actually **runs** your compiled `.class` bytecode. It's an *abstract specification* with many implementations (HotSpot is the common one). It's what makes Java "write once, run anywhere" — the *same* bytecode runs on any OS because each OS has its own JVM that translates bytecode into native machine instructions. Internally it does: **class loading** (loading `.class` files into memory), **bytecode verification** (security check that the code is well-formed), **JIT compilation** (Just-In-Time — hot code paths get compiled to native machine code for speed), and **garbage collection** (automatic memory cleanup).
- **JRE (Java Runtime Environment)** = JVM **+ the standard class libraries** (`java.lang`, `java.util`, collections, etc.) + supporting files. It's everything you need to *run* a Java application, but not to build one. If you only want to run a Java app, the JRE is enough.
- **JDK (Java Development Kit)** = JRE **+ development tools**: `javac` (the compiler that turns `.java` source into `.class` bytecode), `jar` (packaging), `javadoc` (documentation), `jdb` (debugger), etc. You need the JDK to *write and compile* Java.
- **One-liner to say:** "I write code, `javac` (JDK) compiles it to bytecode, the JVM (inside the JRE) runs that bytecode on any platform."

### Q2. Explain the four pillars of OOP with a real example.
OOP organizes code around "objects" (data + behavior together). The four pillars, each with the *why*:
- **Encapsulation** — bundling data and the methods that operate on it into one unit, and **hiding the internal state** behind `private` fields exposed only through controlled methods. *Why it matters:* it protects invariants (rules that must always hold) and lets you change the internals without breaking callers. Example: a `BankAccount` keeps `balance` private and only allows changes via `deposit()`/`withdraw()`, so no one can set a negative balance directly.
- **Abstraction** — exposing **what** something does while hiding **how** it does it, usually via interfaces or abstract classes. *Why:* callers depend on a simple contract, not messy details, so implementations can be swapped freely. Example: a `PaymentGateway` interface has `pay(amount)`; the caller doesn't care whether it's Stripe or PayPal underneath.
- **Inheritance** — a subclass reuses and extends a parent ("is-a" relationship). *Why:* code reuse and a shared type hierarchy. Example: `SavingsAccount extends Account` reuses common account logic. *Caution:* prefer **composition over inheritance** when the relationship isn't a true "is-a" — deep inheritance trees become rigid.
- **Polymorphism** — "many forms": the same interface/call behaves differently depending on the actual object. Two kinds: **compile-time (overloading)** — same method name, different parameters; and **runtime (overriding)** — a subclass provides its own version, and the JVM picks it at runtime via **dynamic dispatch**. *Why:* you can write general code (`Account a`) that works with any subtype. Example: `for (Shape s : shapes) s.area();` calls the right `area()` per shape.

### Q3. `==` vs `.equals()` vs `hashCode()` contract?

**The one-line summary:** `==` asks "are these the *same object*?", `.equals()` asks "are these *meaningfully equal*?", and `hashCode()` gives a number that lets hash collections *find* objects fast. Now let's build the intuition step by step.

**1) `==` compares references, not contents (for objects).**
Every object lives at some address in memory. A variable of an object type doesn't hold the object itself — it holds a *reference* (think of it as the object's address). `==` simply checks "do these two variables hold the same address?"

```java
String a = new String("hello");   // object #1 in memory
String b = new String("hello");   // object #2 in memory (new = force a new object)
System.out.println(a == b);       // false  -> different addresses
System.out.println(a.equals(b));  // true   -> same characters "hello"
```
For **primitives** (`int`, `double`, `char`, `boolean`, ...) there are no references at all, so `==` just compares the raw values: `5 == 5` is `true`.

> Analogy: two people can live in *identical* houses (same layout, same furniture) but at *different addresses*. `==` compares the addresses; `.equals()` compares whether the houses look the same inside.

**2) `.equals()` defines "logical / value equality" — and YOU decide what that means.**
By default, `Object.equals()` is literally just `==` (it compares addresses). That's useless for value objects, so classes that represent a *value* override it. `String`, the wrapper classes (`Integer`, `Long`, ...), and `record` types already override `equals()` sensibly for you. For your own classes you must write it:

```java
class Money {
    final String currency;
    final long cents;
    Money(String currency, long cents) { this.currency = currency; this.cents = cents; }

    @Override
    public boolean equals(Object o) {
        if (this == o) return true;                 // same object shortcut
        if (!(o instanceof Money m)) return false;  // type check (pattern match)
        return cents == m.cents && Objects.equals(currency, m.currency);
    }
    @Override
    public int hashCode() { return Objects.hash(currency, cents); }
}
```

**3) `hashCode()` is the "bucket number" for hash-based collections.**
`HashMap` and `HashSet` don't scan every element to find a key — that would be slow. Instead they call `hashCode()` to compute which *bucket* (slot) an object belongs to, jump straight to that bucket, and only then use `.equals()` to confirm the exact match within that bucket. This is what makes lookups roughly O(1) instead of O(n).

**4) The contract (this is the part interviewers push on):**
- If `a.equals(b)` is `true`, then `a.hashCode()` **must** equal `b.hashCode()`. (Equal objects *must* land in the same bucket.)
- The reverse is **not** required: two *unequal* objects are *allowed* to share a hashcode — that's called a **collision**, and it's fine (the collection falls back to `.equals()` inside the bucket).
- Also: `hashCode()` must be **consistent** — the same object must return the same value as long as its `equals`-relevant fields don't change. (This is why immutable keys are ideal.)

**5) Concrete demo of the bug you get if you break the contract** (override `equals` but forget `hashCode`):

```java
class BadKey {
    final int id;
    BadKey(int id) { this.id = id; }
    @Override public boolean equals(Object o) {
        return o instanceof BadKey b && b.id == this.id;
    }
    // BUG: no hashCode() override -> inherits Object's identity-based hashCode
}

Map<BadKey, String> map = new HashMap<>();
map.put(new BadKey(1), "Anup");
System.out.println(map.get(new BadKey(1))); // prints null !!
```
Why `null`? The two `BadKey(1)` objects are `.equals()`, but because `hashCode()` wasn't overridden they produce *different* bucket numbers. The map stores the value in bucket A, then looks for it in bucket B, and never finds it. Your data effectively "disappears."


### Q4. Why are Strings immutable in Java?
"Immutable" means once a `String` object is created, its characters can **never change** — any operation that looks like it modifies a string (`concat`, `replace`, `toUpperCase`) actually **creates a brand-new String object** and leaves the original untouched. There are several deliberate reasons Java's designers chose this:
- **Security:** Strings are used everywhere for sensitive things — file paths, network URLs/hostnames, database connection strings, class names in class loading, usernames. If a String could be changed after a security check, an attacker could pass a valid value to the check and then mutate it to something malicious before it's used (a "time-of-check to time-of-use" attack). Immutability makes that impossible.
- **Thread-safety for free:** because a String can't change, multiple threads can share the *same* String object with **zero synchronization** and never see a corrupted or half-updated value. Mutable objects need locks to be shared safely; immutable ones don't.
- **The String Pool (memory efficiency):** Java keeps a special area in memory called the **String Pool**. String **literals** (like `"hello"`) are stored there once and reused, so writing `"hello"` in 100 places reuses one object instead of creating 100. This is only safe *because* strings are immutable — if one reference could change the shared string, it would corrupt it for everyone else. (This is also why `"a" == "a"` is `true` — both point to the same pooled object.)
- **Hashcode caching (fast map keys):** because the content never changes, a String's `hashCode()` is computed **once and cached**. Since Strings are the most common `HashMap` keys, this makes map lookups very fast — no need to recompute the hash each time.
- **Trade-off to mention:** the downside is that building strings in a loop with `+` creates many throwaway objects (garbage) — that's exactly why `StringBuilder` exists (next question).

### Q5. `String` vs `StringBuilder` vs `StringBuffer`?
All three deal with text, but differ in **mutability** and **thread-safety** — pick based on those two axes:
- **`String`** — **immutable**. Great for fixed text and as map keys, but doing `s += x` repeatedly in a loop is O(n²): each `+=` creates a new object and copies all the characters, generating lots of garbage.
- **`StringBuilder`** — **mutable** (you can append/insert/delete in place using an internal resizable char array) and **not thread-safe**. It's the **default choice** for building strings efficiently in a single thread (e.g., building a big report or SQL string in a loop). Fast because there's no locking.
- **`StringBuffer`** — same as `StringBuilder` but **thread-safe** because its methods are `synchronized`. That locking makes it slower. You only need it in the rare case where **multiple threads** append to the *same* buffer — which is uncommon, so in modern code you almost always use `StringBuilder`.
- **Rule of thumb:** immutable text → `String`; building text in one thread → `StringBuilder`; building shared text across threads → `StringBuffer` (rare).

### Q6. `final`, `finally`, `finalize`?
Three unrelated things with confusingly similar names — a classic trick question:
- **`final`** is a **keyword/modifier** with three uses: (1) a **`final` variable** can't be reassigned after it's set (a constant, or a reference that always points to the same object — though the object's contents can still change); (2) a **`final` method** can't be overridden by subclasses; (3) a **`final` class** can't be extended (e.g., `String` is final). Used for safety, clarity of intent, and enabling some JVM optimizations.
- **`finally`** is a **block** in try/catch that **always executes** — whether the `try` succeeded, threw an exception, or even `return`ed early. It's for **cleanup** (closing files/connections, releasing locks) that must happen no matter what. (Modern code prefers **try-with-resources**, which auto-closes and is cleaner than a manual `finally`.)
- **`finalize()`** is a **method** (from `Object`) the garbage collector *might* call before reclaiming an object — meant for last-chance cleanup. It's **deprecated and unreliable** (there's no guarantee it ever runs, or when), can hurt performance, and can even resurrect objects. **Never rely on it** — use try-with-resources / `AutoCloseable` / `Cleaner` instead.

### Q7. Checked vs unchecked exceptions?
Java splits `Throwable` into two families, and the difference is about **whether the compiler forces you to handle it**:
- **Checked exceptions** (extend `Exception` but not `RuntimeException`) — the **compiler forces** you to either `catch` them or declare them with `throws`. They represent **recoverable, external conditions** the caller might reasonably handle — e.g., `IOException` (a file/network could fail), `SQLException` (the DB could reject a query). The idea: "this can fail for reasons outside your control, so acknowledge it."
- **Unchecked exceptions** (extend `RuntimeException`) — the compiler does **not** force handling. They usually indicate **programming bugs** you should *fix*, not catch — e.g., `NullPointerException` (you forgot a null check), `IllegalArgumentException` (bad argument), `ArrayIndexOutOfBoundsException` (bad index).
- **Errors** (extend `Error`) — serious problems from the JVM/environment that you generally **should not catch** or try to recover from, e.g., `OutOfMemoryError`, `StackOverflowError`.
- **Real-world note:** many modern frameworks (Spring) lean toward **unchecked** exceptions to avoid cluttering code with `throws` and to centralize handling (e.g., a global `@ControllerAdvice`). Be ready to argue both sides.

### Q8. Abstract class vs Interface (Java 8+)?
Both let you define a contract that subclasses/implementers fulfill, but they answer different design questions. Use an **abstract class** when classes share a common **base with state and some shared code** ("is-a" + common implementation); use an **interface** to define a **capability/contract** that unrelated classes can implement ("can-do"). Since Java 8, interfaces can also have `default` and `static` methods (and `private` methods since Java 9), which narrowed the gap — but the key differences remain:

| | Abstract Class | Interface |
|--|--|--|
| Multiple inheritance | No (one superclass only) | Yes (a class can implement many) |
| State (fields) | Yes — can hold instance fields | Only `public static final` constants |
| Constructor | Yes | No |
| Methods | abstract + concrete | abstract + `default` + `static` + `private` (Java 9) |
| Use when | shared base + shared state/behavior | a capability many unrelated types can have |

- **Simple guidance:** "Is it a core identity with shared state?" → abstract class (`Animal`). "Is it a role/ability?" → interface (`Comparable`, `Serializable`, `Runnable`). Modern designs favor **interfaces + composition** for flexibility, using abstract classes mainly to share common implementation.


---

## B. Java 8+ Functional Features

### Q9. What are functional interfaces? Name key built-ins.
A **functional interface** is an interface with **exactly one abstract method** (it can have other default/static methods). Because it has a single "slot," it can be implemented concisely with a **lambda expression** or **method reference** instead of a bulky anonymous class. The `@FunctionalInterface` annotation is optional but good practice — it makes the compiler *enforce* the single-abstract-method rule so you don't accidentally break it. This is the foundation that makes Java 8's functional style (streams, etc.) possible. Key built-ins in `java.util.function`:
- **`Function<T,R>`** — takes a T, returns an R. Method: `apply`. e.g., `Function<String,Integer> len = String::length;`
- **`Supplier<T>`** — takes nothing, supplies a T. Method: `get`. e.g., lazy value provider `() -> new Config()`.
- **`Consumer<T>`** — takes a T, returns nothing (side effect). Method: `accept`. e.g., `System.out::println`.
- **`Predicate<T>`** — takes a T, returns boolean (a test/condition). Method: `test`. e.g., `x -> x > 0`.
- **`BiFunction<T,U,R>`** (two inputs), **`UnaryOperator<T>`** (T→T), **`BinaryOperator<T>`** (two T's → T, e.g., `Integer::sum`).
- **Why it matters:** these let you pass *behavior* as arguments (e.g., `list.forEach(consumer)`, `stream.filter(predicate)`), enabling clean, reusable, declarative code.

### Q10. Explain the Stream API. Intermediate vs terminal operations.
A **Stream** is a pipeline for processing a sequence of elements in a **declarative** style — you say *what* you want (filter, map, collect), not *how* to loop. Key properties: streams are **lazy** (nothing runs until a terminal operation), **don't modify the source**, and are **single-use** (consumed once). A pipeline has three parts: a **source** (collection/array), zero or more **intermediate operations**, and one **terminal operation**.
- **Intermediate operations** are **lazy** and return another stream, so they chain. They only *describe* work; nothing executes yet. Examples: `map` (transform each element), `filter` (keep matching), `sorted`, `distinct` (remove duplicates), `limit`/`skip`, `flatMap` (flatten), `peek` (debug).
- **Terminal operations** **trigger** the whole pipeline to actually run and produce a result or side effect. Examples: `collect` (gather into a List/Map), `forEach`, `reduce` (combine into one value), `count`, `anyMatch`/`allMatch`, `findFirst`.
- **Why laziness is powerful:** the stream can **short-circuit** (e.g., `findFirst` stops as soon as it finds one) and **fuse** operations in a single pass for efficiency — instead of creating intermediate collections at each step.

```java
// Group employees by dept, average salary
Map<String, Double> avg = employees.stream()
    .collect(Collectors.groupingBy(
        Employee::getDept,
        Collectors.averagingDouble(Employee::getSalary)));

// Top 3 highest paid names
List<String> top3 = employees.stream()
    .sorted(Comparator.comparingDouble(Employee::getSalary).reversed())
    .limit(3)                          // short-circuits after 3 (with sorted)
    .map(Employee::getName)
    .collect(Collectors.toList());
```

### Q11. `map` vs `flatMap`?
Both transform stream elements, but they differ in the *shape* of the result:
- **`map`** is a **one-to-one** transform: each input element becomes exactly one output element. If each element itself produces a *collection/stream*, you'd end up with a nested `Stream<List<T>>` or `Stream<Stream<T>>` — still nested.
- **`flatMap`** is a **one-to-many + flatten**: each input element maps to a *stream* of values, and `flatMap` **merges (flattens) all those little streams into one flat stream**. Use it whenever you have nested structures you want to unwrap.

```java
// map keeps nesting: Stream<List<String>>
// flatMap flattens: Stream<String>
List<String> allTags = posts.stream()
    .flatMap(post -> post.getTags().stream())   // each post -> its tags, all merged
    .distinct()
    .collect(Collectors.toList());
```
**Mental model:** `map` = "change each item"; `flatMap` = "change each item into several items and combine them all."

### Q12. What is `Optional` and why use it?
`Optional<T>` is a **container that either holds a value or is empty** — a deliberate, explicit way to represent "a value might be absent." Before Java 8, absence was represented by `null`, which led to the infamous `NullPointerException` and unclear APIs (does this method return null sometimes? you had to read the docs/code). `Optional` makes "might be missing" **part of the type signature**, forcing the caller to consciously handle the empty case, and gives fluent methods to do so cleanly:
```java
Optional<User> u = repo.findById(id);           // clearly signals "might not exist"
String name = u.map(User::getName)              // transform only if present
               .orElse("Unknown");              // default if empty
u.ifPresent(this::process);                     // run only if present
u.orElseThrow(() -> new UserNotFoundException(id)); // throw if empty
```
**Best practices / anti-patterns:** Use `Optional` primarily as a **return type** to signal "may be absent." **Don't** use it for fields, method parameters, or in collections (adds overhead and complexity). **Don't** call `.get()` blindly (it throws if empty — use `orElse`/`orElseThrow`). It's about **communicating intent** and avoiding NPEs, not a null-wrapper for everything.

### Q13. `findFirst` vs `findAny`? Lazy evaluation?
Both are **short-circuiting terminal operations** that return an `Optional` of one element (or empty), and both stop as soon as they can — but they differ on **ordering guarantees**:
- **`findFirst`** returns the **first** element in the stream's **encounter order** (deterministic). Use when order matters.
- **`findAny`** may return **any** element — it gives the JVM freedom to return whatever's fastest. This is meaningless for a normal sequential stream (it usually returns the first anyway) but becomes a real **performance win in parallel streams**, because it doesn't have to coordinate threads to find *the first* — any thread that finds a match can return immediately.
- **Lazy evaluation angle:** because these are short-circuiting, the stream pipeline only processes as many elements as needed to find one match, then stops — it won't run `map`/`filter` on the rest.

### Q14. What are default and static methods in interfaces (Java 8)?
Before Java 8, interfaces could only declare abstract methods, so **adding a method to an interface broke every existing implementer** (they'd all fail to compile). Java 8 solved this with two new kinds of concrete methods you can put directly in an interface: **default** and **static**.

**1) Default methods (`default` keyword)** provide a **body/implementation right in the interface**. Implementers inherit it automatically, so you can **add new methods without breaking existing code**. This is the *backward-compatibility* feature — it's exactly how Java added `stream()`, `forEach()`, and `removeIf()` to `Collection`/`Iterable` without breaking the thousands of classes that already implemented those interfaces. Implementers can still **override** the default if they want different behavior.

```java
interface Vehicle {
    String name();                       // abstract — each implementer must provide it

    default void start() {               // default — inherited automatically, no break
        System.out.println(name() + " starting with a generic engine...");
    }
}

// Existing class written years ago — it keeps compiling and gets start() for FREE.
class Car implements Vehicle {
    public String name() { return "Car"; }
}

// A newer class chooses to override the default behavior.
class ElectricCar implements Vehicle {
    public String name() { return "Tesla"; }
    @Override
    public void start() {                // override the default
        System.out.println(name() + " powering up silently...");
    }
}

new Car().start();          // Car starting with a generic engine...
new ElectricCar().start();  // Tesla powering up silently...
```

Real-world example from the JDK itself:
```java
List<String> names = new ArrayList<>(List.of("ann", "bob", "cara", "bob"));
names.removeIf(n -> n.equals("bob"));   // removeIf is a DEFAULT method on Collection
names.forEach(System.out::println);      // forEach is a DEFAULT method on Iterable
```

**2) Static methods in interfaces** are **utility/factory methods** tied to the interface itself (called as `MyInterface.method()`, never on an instance). They keep related helpers *with* the interface instead of in a separate `SomethingUtils` class. Classics: `Comparator.comparing(...)`, `List.of(...)`, `Stream.of(...)`, `Path.of(...)`.

```java
interface Shape {
    double area();

    // Factory/utility method that lives on the interface itself.
    static Shape circle(double r) {
        return () -> Math.PI * r * r;    // lambda implementing the single abstract method
    }
    static Shape square(double side) {
        return () -> side * side;
    }
}

Shape c = Shape.circle(2);   // called on the interface, not an instance
System.out.println(c.area()); // 12.566...

// JDK example: Comparator.comparing is a static interface method
List<String> words = new ArrayList<>(List.of("banana", "fig", "apple"));
words.sort(Comparator.comparing(String::length));  // [fig, apple, banana]
```

> Note: static interface methods are **not inherited** by implementing classes — you must call them via the interface name (`Shape.circle(...)`), not via an instance or subclass.

**3) The diamond problem** — if a class implements two interfaces that both provide the *same* default method, the compiler can't decide which one to use, so it **forces you to override it** to resolve the ambiguity. Inside your override you can delegate to a specific parent with `InterfaceName.super.method()`.

```java
interface A {
    default String greet() { return "Hello from A"; }
}
interface B {
    default String greet() { return "Hello from B"; }
}

class C implements A, B {
    @Override
    public String greet() {
        // Won't compile without this override — ambiguous between A and B.
        return A.super.greet() + " & " + B.super.greet();  // pick / combine explicitly
    }
}

System.out.println(new C().greet());  // Hello from A & Hello from B
```

**Rules to remember (interview one-liners):**
- A default method can be overridden; a `static` interface method cannot (it's not inherited).
- **Class methods win over interface defaults** — if a superclass provides a concrete method, it takes priority over any interface's default ("class always beats interface").
- Default methods can't override `Object` methods like `equals`, `hashCode`, `toString`.
- Java 9 also added **`private` methods in interfaces** to share code between default methods without exposing it publicly.

### Q15. New features across Java versions (know highlights).
Interviewers like to see you've kept current. Know the *headline* features per LTS:
- **Java 8** (huge release) — **lambdas**, **Stream API**, **`Optional`**, **default/static interface methods**, a new **Date/Time API** (`java.time`, replacing the broken `Date`/`Calendar`), and **`CompletableFuture`** for async.
- **Java 9** — the **module system (JPMS)** for strong encapsulation; **collection factory methods** (`List.of`, `Map.of`); private interface methods.
- **Java 11 (LTS)** — `var` usable in lambda params, a modern **HTTP Client**, handy `String` methods (`strip`, `isBlank`, `lines`), run a single `.java` file directly.
- **Java 17 (LTS)** — **records** (concise immutable data classes), **sealed classes** (restrict who can extend), **pattern matching for `instanceof`**, **switch expressions**, **text blocks** (multi-line strings).
- **Java 21 (LTS)** — **virtual threads** (Project Loom — massive lightweight concurrency), **pattern matching for `switch`**, **record patterns** (destructuring), **sequenced collections**.
- **Tip:** mention you work "up to Java 21" and can name virtual threads + records + sealed classes as the modern highlights.

### Q16. What are records (Java 16+)?
A **record** is a concise way to declare an **immutable, data-carrying class**. In one line you get a class whose fields are `final`, plus the compiler auto-generates: an all-args **constructor**, **accessor methods** (`x()`, `y()`), and correct **`equals()`, `hashCode()`, and `toString()`** — eliminating tons of boilerplate you'd otherwise write (or generate with Lombok).
```java
public record Point(int x, int y) {}
// auto-gets: constructor, x(), y(), equals, hashCode, toString — all correct & immutable
```
**Where to use:** DTOs, API request/response objects, value objects, and **immutable events** (perfect for Kafka messages/domain events). You can add validation via a "compact constructor." **Trade-off:** records are immutable and can't extend other classes, so they're for *data*, not rich behavior/inheritance hierarchies.

### Q17. What are virtual threads (Java 21)?
Traditional Java threads are **platform threads** — each maps 1:1 to an expensive OS thread, so you can only run a few thousand before running out of memory. That forced complex "reactive/async" programming for high-concurrency I/O apps. **Virtual threads** are **lightweight threads managed by the JVM**, not the OS — you can have **millions** of them. When a virtual thread **blocks on I/O** (a DB call, HTTP request), the JVM cheaply "unmounts" it from its underlying OS carrier thread and runs another virtual thread there, so blocking is no longer wasteful.
- **Why it's a big deal:** you can write **simple, blocking, sequential code** ("thread-per-request") and still get huge scalability — no callback/reactive complexity — which is ideal for **I/O-bound** workloads like handling thousands of concurrent HTTP calls (very relevant to microservices). Enable in Spring Boot 3.2+ with `spring.threads.virtual.enabled=true`.
- **Caveat:** they help **I/O-bound**, not CPU-bound work (CPU work still needs real cores). Avoid pinning them with long `synchronized` blocks on external resources.

### Q18. Sealed classes?
A **sealed** class or interface **restricts which other classes are allowed to extend/implement it** using a `permits` clause. Normally any class can be subclassed (unless `final`); sealed gives you a middle ground — a **controlled, known set of subtypes**.
```java
public sealed interface Shape permits Circle, Square, Triangle {}
```
- **Why it's useful:** (1) **Domain modeling** — you explicitly say "a Shape is *only ever* a Circle, Square, or Triangle," which documents intent and prevents unexpected subtypes. (2) **Exhaustive pattern matching** — because the compiler knows *all* possible subtypes, a `switch` over them can be checked for completeness (no `default` needed, and it warns if you miss a case). This pairs beautifully with records + pattern matching for clean, type-safe "algebraic data type" style code.


---

## C. Collections

### Q19. Explain the Collections hierarchy.
The Java Collections Framework is a set of interfaces + implementations for storing groups of objects. There are **two separate root trees**: `Collection` (single elements) and `Map` (key-value pairs — technically not a `Collection`).
- **`Collection`** splits into: **`List`** (ordered sequence, allows duplicates, index-based — `ArrayList`, `LinkedList`); **`Set`** (no duplicates — `HashSet`, `TreeSet`, `LinkedHashSet`); and **`Queue`/`Deque`** (ordering for processing — `ArrayDeque`, `PriorityQueue`, `LinkedList`).
- **`Map`** (separate) stores key→value with unique keys — `HashMap`, `TreeMap`, `LinkedHashMap`, `ConcurrentHashMap`.
- **How to choose:** need order + index → `List`; need uniqueness → `Set`; need key lookup → `Map`; need FIFO/LIFO/priority processing → `Queue`/`Deque`. Then pick the implementation by whether you need **sorting** (Tree*), **insertion-order** (Linked*), or just **fast unordered** (Hash*).

### Q20. `ArrayList` vs `LinkedList`?
Both are `List`s, but backed by completely different data structures, which drives their performance:
- **`ArrayList`** is backed by a **resizable array**. **Random access by index is O(1)** (just jump to `array[i]`), it's **memory-compact and cache-friendly** (elements sit contiguously, so CPU caching is efficient). Downside: inserting/removing in the **middle** is O(n) because all following elements must shift; and when it grows past capacity it allocates a bigger array and copies over (amortized O(1) appends).
- **`LinkedList`** is a **doubly-linked list** of nodes. Insert/remove at the **ends** is O(1) (great as a `Queue`/`Deque`), but **random access is O(n)** (must walk node-by-node), and it uses more memory (each node stores prev/next pointers) and is cache-unfriendly.
- **Practical verdict:** `ArrayList` is the **default** for almost everything — even for many insert/remove patterns it wins due to cache locality. Use `LinkedList` only when you specifically need a queue/deque with frequent add/remove at both ends (and even then `ArrayDeque` is usually better).

### Q21. How does HashMap work internally?
A `HashMap` stores key-value pairs and gives **O(1) average** lookup by using **hashing**. Instead of scanning every entry (which would be O(n)), it computes *where* an entry should live from the key itself, so it can jump straight there.

**The core data structure — an array of buckets.**
Internally a `HashMap` holds a `Node<K,V>[] table` (the "buckets"). Each `Node` stores the key's hash, the key, the value, and a `next` pointer (for chaining):

```java
// Simplified from the JDK
static class Node<K,V> {
    final int hash;
    final K key;
    V value;
    Node<K,V> next;   // links to the next node in the SAME bucket (collision chain)
}
```

**Step 1 — computing the bucket index (`put`/`get`).**
When you `put(key, value)`, the map:
1. Calls `key.hashCode()`.
2. **Spreads the bits** to mix high bits into low bits (reduces clustering): `hash = h ^ (h >>> 16)`.
3. Computes the bucket index as `hash & (n - 1)`, where `n` is the table size (always a **power of 2**, so `& (n-1)` is a fast substitute for `% n`).

```java
int hash = key.hashCode() ^ (key.hashCode() >>> 16);
int index = hash & (table.length - 1);   // e.g. if table.length = 16 -> hash & 15
```

**Visualization — buckets with collision chains:**
```
table (capacity = 16)
 index
  [0]  -> null
  [1]  -> ("apple", 3)                         (single entry)
  [2]  -> null
  ...
  [5]  -> ("banana", 7) -> ("grape", 2)        (COLLISION: 2 keys, same bucket = linked list)
  ...
  [9]  -> ("mango", 5)
  [15] -> null
```

**Step 2 — handling collisions (two keys in the same bucket).**
Different keys can produce the same bucket index (a **collision**). They're stored as a **chain**:
- **Java 7 and earlier:** always a **linked list** in the bucket. Worst case (all keys collide) is **O(n)** lookups.
- **Java 8+:** if a single bucket's chain grows beyond **8 entries** (`TREEIFY_THRESHOLD`) *and* the table has **≥ 64 buckets** (`MIN_TREEIFY_CAPACITY`), that bucket is converted from a **linked list into a balanced red-black tree**, improving that bucket's worst-case lookup from **O(n) to O(log n)**. (This defends against hash-collision denial-of-service attacks.) If the tree later shrinks below 6 entries, it untreeifies back to a list.

**Visualization — treeification of a hot bucket:**
```
Before (linked list, slow when long):
  [5] -> k1 -> k2 -> k3 -> ... -> k9        (O(n) walk)

After (>8 entries, capacity >= 64) -> red-black tree:
  [5] ->        (k5)
               /     \
            (k2)     (k8)                    (O(log n) lookup)
           /   \     /   \
        (k1)  (k3) (k6)  (k9)
```

**Step 3 — load factor & resizing.**
The **load factor** (default **0.75**) controls how full the table gets before it grows. The threshold = `capacity × loadFactor` (e.g., `16 × 0.75 = 12`). When `size` exceeds the threshold, the map **doubles the capacity** and **rehashes** (redistributes) all entries into the bigger table. This keeps chains short so operations stay ~O(1).

```
capacity 16, threshold 12
 put 13th entry  ==>  RESIZE: capacity becomes 32, threshold 24, all entries rehashed
```
- Resizing is **expensive** (allocate + rehash everything), so if you know the size ahead of time, **pre-size** it: `new HashMap<>(expectedSize / 0.75 + 1)` to avoid repeated resizes.

**Step 4 — why keys need correct `hashCode()` and `equals()`.**
Lookup is a **two-phase** process:
1. `hashCode()` (spread) → finds the **bucket**.
2. `equals()` → finds the **exact key** within that bucket's chain/tree.

If either is wrong, the map misbehaves. A **mutable key whose fields change after insertion** produces a different hashcode, so the map looks in the wrong bucket and the entry is effectively "lost":

```java
class MutableKey {
    int id;
    MutableKey(int id) { this.id = id; }
    @Override public int hashCode() { return Integer.hashCode(id); }
    @Override public boolean equals(Object o) {
        return o instanceof MutableKey m && m.id == id;
    }
}

Map<MutableKey, String> map = new HashMap<>();
MutableKey k = new MutableKey(1);
map.put(k, "value");        // stored in bucket for hash(1)
k.id = 999;                 // MUTATED -> hashCode now points to a different bucket!
System.out.println(map.get(k)); // null -- looks in bucket for hash(999), entry is "lost"
```
This is why **immutable keys** (like `String`, `Integer`, or records) are strongly preferred.

**One-liner to say:** "A HashMap is an array of buckets indexed by a spread hashcode; collisions chain as a linked list that treeifies to a red-black tree after 8 entries; it doubles capacity and rehashes at 0.75 load factor; and keys need consistent `hashCode()`/`equals()` (ideally immutable) so entries aren't lost."

### Q22. `HashMap` vs `Hashtable` vs `ConcurrentHashMap`?
All are maps; the difference is **thread-safety and performance**:
- **`HashMap`** — **not synchronized** (not thread-safe). Fastest for single-threaded use. Allows **one null key** and null values.
- **`Hashtable`** — **legacy** (pre-Java collections). It's fully synchronized: **every method is `synchronized`**, so only one thread can touch it at a time — thread-safe but a **major bottleneck** under concurrency. No nulls allowed. Essentially obsolete.
- **`ConcurrentHashMap`** — the **modern thread-safe choice**. Instead of locking the whole map, it locks only a **single bucket/bin** at a time (via CAS for empty bins + `synchronized` on the bin head), so many threads can read/write **different** buckets concurrently → high throughput. Reads are largely lock-free. No null keys/values (so `null` can't be ambiguous with "absent" across threads).
- **Verdict:** single-threaded → `HashMap`; concurrent → `ConcurrentHashMap`; never use `Hashtable` in new code.

### Q23. `HashSet` vs `TreeSet` vs `LinkedHashSet`?
All are `Set`s (no duplicates); they differ in **ordering** and are each backed by a corresponding map:
- **`HashSet`** — **no ordering** (elements appear in unpredictable order). Backed by a `HashMap`. **O(1)** add/contains/remove. Use when you just need uniqueness and don't care about order (the fastest choice).
- **`LinkedHashSet`** — maintains **insertion order** (iterates in the order you added items). Slightly more memory (linked list overhead) but still ~O(1). Use when you need uniqueness *and* predictable iteration order.
- **`TreeSet`** — keeps elements **sorted** (natural order or a `Comparator`). Backed by a red-black tree, so operations are **O(log n)**. It's "navigable" — supports `first()`, `last()`, `ceiling()`, `floor()`, `headSet`/`tailSet`. Use when you need sorted data or range queries.

### Q24. `Comparable` vs `Comparator`?
Both define how objects are ordered, but *who* defines the ordering and *how many* orderings differ:
- **`Comparable`** — the class defines its **own single "natural" ordering** by implementing `compareTo(other)`. Example: `String` and `Integer` are Comparable. Use it when there's one obvious default sort order for the type. `Collections.sort(list)` uses this.
- **`Comparator`** — an **external, separate object** that defines an ordering via `compare(a, b)`, without touching the class. This lets you define **multiple different orderings** (by name, by salary, by date) and sort the same objects different ways. Great when you don't own the class or need several sort strategies.
```java
// Sort by dept ascending, then by salary descending — a Comparator chain
list.sort(Comparator.comparing(Emp::getDept)
         .thenComparing(Emp::getSalary, Comparator.reverseOrder()));
```
**Mental model:** `Comparable` = "the object knows how to compare itself"; `Comparator` = "someone else decides the comparison."

### Q25. Fail-fast vs fail-safe iterators?
This is about what happens if a collection is **modified while you're iterating** over it:
- **Fail-fast** (default for `ArrayList`, `HashMap`, `HashSet`): if the collection is structurally modified during iteration (except via the iterator's own `remove()`), it **throws `ConcurrentModificationException` immediately**. It detects this using an internal `modCount` counter that the iterator checks. This is a *safety feature* — it fails loudly rather than silently producing wrong results. (Note: it's "best-effort" detection, not a guarantee.)
- **Fail-safe** (e.g., `CopyOnWriteArrayList`, `ConcurrentHashMap`): the iterator works on a **snapshot/copy** of the data, so concurrent modifications don't throw an exception — but the iteration **may not reflect the latest changes** (you might miss recent updates). Safer for concurrent scenarios at the cost of slightly stale views and extra memory.
- **Practical fix for the fail-fast trap:** to remove during iteration, use `iterator.remove()` or `collection.removeIf(...)` rather than `collection.remove()` inside a for-each loop.

---

## D. Concurrency & Multithreading

### Q26. Ways to create a thread?
There are several, from low-level to high-level (prefer the high-level ones):
- **Extend `Thread`** and override `run()` — simplest but couples your logic to the Thread class (you "use up" your single inheritance). Rarely recommended.
- **Implement `Runnable`** (or `Callable`) and pass it to a thread/executor — preferred because it separates the *task* from the *thread*, and you can still extend another class.
- **`ExecutorService`** (thread pools) — the **recommended modern approach**: you submit tasks and the pool manages reusable threads, sizing, queueing, and shutdown for you.
- **`CompletableFuture`** — for composing asynchronous tasks without manually managing threads.
- **Virtual threads (Java 21)** — `Executors.newVirtualThreadPerTaskExecutor()` for massive I/O concurrency.
- **Best practice:** avoid creating raw `Thread` objects by hand in production — use an `ExecutorService` (or virtual threads) so you control pool size and lifecycle.

### Q27. `Runnable` vs `Callable`?
Both represent a task to run on a thread, but:
- **`Runnable`** — its method `run()` returns **void** and **can't throw checked exceptions**. Use for "fire and forget" tasks where you don't need a result.
- **`Callable<V>`** — its method `call()` **returns a value** and **can throw checked exceptions**. When submitted to an executor, you get back a **`Future<V>`** you can use to retrieve the result (blocking until it's ready) or handle failure. Use when the task computes something you need back.

### Q28. Explain the thread lifecycle.
A Java thread moves through defined states (visible via `Thread.State`):
- **NEW** — created (`new Thread()`) but `start()` not yet called.
- **RUNNABLE** — eligible to run; the OS scheduler decides when it actually gets CPU (Java lumps "ready" and "running" into RUNNABLE).
- **BLOCKED** — waiting to acquire a monitor lock (e.g., to enter a `synchronized` block held by another thread).
- **WAITING** — waiting indefinitely for another thread to signal it (`wait()`, `join()`, `park()`).
- **TIMED_WAITING** — waiting for a set time (`sleep(ms)`, `wait(ms)`, `join(ms)`).
- **TERMINATED** — finished (`run()` completed or threw).
Understanding these helps diagnose hangs (many threads BLOCKED = lock contention; WAITING = coordination issue).

### Q29. `synchronized` vs `Lock` (ReentrantLock)?
Both provide mutual exclusion (only one thread in the critical section), but differ in flexibility:
- **`synchronized`** — the built-in, **implicit** lock (on `this`, a given object, or a class). The lock is **acquired and released automatically** (released even if an exception is thrown), which makes it simple and safe. Limitations: you can't try-and-give-up, can't time out, no fairness control, and it's block/method-scoped.
- **`ReentrantLock`** — an **explicit** lock (`lock()` / `unlock()`, always unlock in a `finally`). It adds powerful features: **`tryLock()`** (attempt without blocking forever), **timed lock** (`tryLock(timeout)`), **fairness** (FIFO ordering option), **interruptible** locking, and multiple **`Condition`** objects (finer-grained wait/notify). "Reentrant" means the same thread can acquire it again without deadlocking itself.
- **Verdict:** use `synchronized` for simple cases (it's cleaner and auto-released); use `ReentrantLock` when you need tryLock/timeout/fairness/multiple conditions.

### Q30. What is the `volatile` keyword?
`volatile` addresses a subtle multithreading problem: **visibility**. Normally each thread may cache a variable's value in a CPU register/cache, so one thread's update might **never be seen** by another. Marking a field `volatile` guarantees that:
1. **Visibility** — every read comes straight from **main memory** and every write goes straight to main memory, so all threads see the latest value.
2. **No reordering** — the compiler/CPU won't reorder instructions across the volatile access (establishes a happens-before edge).
**Crucially, it does NOT provide atomicity** for compound operations: `count++` is read-modify-write (three steps), so two threads can still lose an update even if `count` is volatile. **Use `volatile` for simple flags** (e.g., a `boolean running` to stop a loop); use **`Atomic*` classes or locks** for counters/compound updates.

### Q31. `Atomic` classes and CAS?
The `java.util.concurrent.atomic` classes (`AtomicInteger`, `AtomicLong`, `AtomicReference`, etc.) provide **thread-safe updates without locks**, which is faster under contention. They rely on **CAS (Compare-And-Swap)** — a single CPU instruction that says: "if this variable still equals the expected old value, atomically set it to the new value; otherwise fail and let me retry." So `incrementAndGet()` reads the value, computes +1, and CAS-swaps it; if another thread beat it, it just retries in a loop. This is **lock-free** (no blocking), scaling better than `synchronized` for hot counters/flags. Under *very high* contention, `LongAdder` spreads the count across multiple cells to reduce retries.

### Q32. What is the ExecutorService / thread pools?
Creating a new OS thread per task is expensive (memory + setup) and unbounded thread creation can crash your app. An **`ExecutorService`** manages a **pool of reusable worker threads**: you `submit()` tasks, they queue up, and idle workers pick them up — controlling concurrency and resource use. Common factory methods:
- **`newFixedThreadPool(n)`** — a fixed number of threads (bounded concurrency).
- **`newCachedThreadPool()`** — grows/shrinks on demand (good for many short tasks; risky if tasks are unbounded).
- **`newSingleThreadExecutor()`** — one thread, tasks run sequentially.
- **`newScheduledThreadPool()`** — for delayed/periodic tasks.
- **`newVirtualThreadPerTaskExecutor()`** (Java 21) — a virtual thread per task, for massive I/O concurrency.
**Best practices:** always **`shutdown()`** the pool; size it by workload — **CPU-bound** ≈ number of cores; **I/O-bound** can be much higher since threads spend time waiting. Prefer a bounded queue + rejection policy to avoid memory blowups.

### Q33. Explain CompletableFuture.
`CompletableFuture` is Java 8's tool for **composing asynchronous, non-blocking pipelines** — much more powerful than the old `Future` (which could only block on `get()`). You can chain steps, transform results, run things in parallel, and handle errors — all without blocking threads:
```java
CompletableFuture.supplyAsync(() -> fetchUser(id))     // run async, produce a value
    .thenApply(User::getName)                          // transform the result
    .thenCompose(name -> callServiceAsync(name))       // chain another async call (flatMap-like)
    .exceptionally(ex -> "fallback")                   // handle errors gracefully
    .thenAccept(System.out::println);                  // consume the final result
// run several in parallel and wait for all:
CompletableFuture.allOf(f1, f2, f3).join();
```
Key methods: `thenApply` (transform), `thenCompose` (chain another future), `thenCombine` (merge two), `allOf`/`anyOf` (parallel coordination), `exceptionally`/`handle` (error handling). Use it to call multiple services concurrently and combine results — a common microservices pattern.

### Q34. What is a deadlock? How to avoid?
A **deadlock** is when two (or more) threads are each **waiting for a lock the other holds**, so neither can ever proceed — the program hangs forever. Classic example: Thread 1 holds lock A and wants lock B; Thread 2 holds lock B and wants lock A. **How to avoid:**
- **Consistent lock ordering** — always acquire multiple locks in the *same global order* everywhere (the most effective fix).
- **`tryLock` with a timeout** — give up and retry instead of waiting forever.
- **Minimize lock scope** — hold locks for as short a time as possible; don't call external/unknown code while holding a lock.
- **Prefer higher-level utilities** (concurrent collections, `BlockingQueue`) over manual locking.
- To diagnose in production: a thread dump shows the deadlocked threads and which locks they're stuck on.

### Q35. `wait()`/`notify()` vs modern alternatives?
`wait()`, `notify()`, and `notifyAll()` are **low-level** thread coordination primitives on an object's monitor — you must hold the object's lock (be inside `synchronized`) to call them, and they're **error-prone** (missed signals, spurious wakeups, must loop-check the condition). They let one thread wait until another signals a condition. **Modern code prefers higher-level utilities** from `java.util.concurrent` that are safer and clearer:
- **`BlockingQueue`** — producer/consumer handoff without manual wait/notify.
- **`CountDownLatch`** — wait until N tasks complete.
- **`CyclicBarrier`** — wait for a group of threads to all reach a point.
- **`Semaphore`** — limit concurrent access to a resource.
- **`CompletableFuture`** — async result coordination.
Use these instead of raw `wait/notify` whenever possible.

### Q36. Race condition vs data race? Thread-safety strategies?
These sound alike but are distinct:
- **Data race** — a *low-level* problem: two threads access the **same variable** concurrently, at least one writes, and there's **no synchronization** ordering them. The result is undefined (you might read a torn/stale value).
- **Race condition** — a *higher-level* correctness problem: the program's outcome depends on the **timing/interleaving** of threads (e.g., check-then-act: two threads both check "seat available" then both book it). You can have a race condition even without a data race.
- **Thread-safety strategies (in order of preference):** (1) **Immutability** — immutable objects are inherently thread-safe; (2) **Confinement** — keep data in one thread (`ThreadLocal`); (3) **Synchronization** — locks/`synchronized` to serialize access; (4) **Atomics** — CAS-based for simple counters; (5) **Concurrent collections** — `ConcurrentHashMap`, `BlockingQueue` that handle locking internally.

### Q37. What is the Fork/Join framework?
Fork/Join (Java 7+) is a framework for **divide-and-conquer parallelism** — split a big task into smaller subtasks, run them in parallel, and combine (join) the results. It uses a **`ForkJoinPool`** with a clever **work-stealing** algorithm: each worker thread has its own task queue, and when a thread runs out of work it "steals" tasks from another thread's queue — keeping all cores busy and balanced. It backs Java 8 **parallel streams**. It's ideal for **CPU-bound, recursively splittable** problems (e.g., parallel sort, large array computations), not for I/O-bound tasks.

---

## E. JVM, Memory & GC

### Q38. Explain JVM memory areas.
When the JVM runs, it divides memory into several regions:
- **Heap** — the big shared area where **all objects** (and arrays) live; it's garbage-collected. It's split into generations: the **Young generation** (Eden + two Survivor spaces) where new objects are created and most die quickly, and the **Old/Tenured generation** for long-lived objects that survive several collections.
- **Stack** — **one per thread**; holds **stack frames** for each method call (local variables, parameters, partial results, and the return address). It's LIFO and freed automatically when methods return. Deep/infinite recursion overflows it → `StackOverflowError`.
- **Metaspace** (replaced "PermGen" in Java 8) — stores **class metadata** (the structure of loaded classes). It lives in **native memory** (outside the heap) and grows as needed.
- **PC (Program Counter) register** — per thread; points to the current instruction.
- **Native method stack** — for native (JNI/C) method calls.
- **Key distinction:** primitives and object *references* live on the **stack** (within frames); the actual *objects* live on the **heap**.

### Q39. How does Garbage Collection work?
Garbage Collection (GC) **automatically reclaims memory** from objects that are no longer **reachable** (nothing references them) — so you don't manually free memory (avoiding leaks/dangling pointers common in C). It's based on the **generational hypothesis**: *most objects die young*. So:
- **Minor GC** cleans the **Young generation** frequently and fast — surviving objects get promoted toward the Old generation.
- **Major/Full GC** cleans the **Old generation** — less frequent but more expensive, and can cause a longer "stop-the-world" pause.
- **Collectors (algorithms), evolving over versions:** Serial (single-threaded, small apps), Parallel (throughput-focused), CMS (deprecated), **G1** (the default since Java 9 — region-based, balances throughput and predictable pauses), and **ZGC/Shenandoah** (ultra-low pause times, for very large heaps).
- **Tuning knobs:** heap size (`-Xmx`/`-Xms`), target pause (`-XX:MaxGCPauseMillis`), and GC logs (`-Xlog:gc*`) to diagnose issues.

### Q40. Common memory leaks in Java despite GC?
GC only frees **unreachable** objects — so a "leak" happens when you unintentionally keep objects **reachable** forever. Common causes:
- **Unbounded caches / static collections** — a `static Map` you keep adding to but never evict from grows forever.
- **Unclosed resources** — streams, DB connections, sockets not closed (use try-with-resources).
- **Listeners/callbacks not removed** — registering a listener but never unregistering keeps the whole object graph alive.
- **`ThreadLocal` not cleared in thread pools** — pool threads live forever, so a value set once stays and accumulates (a classic web-app leak; always `remove()` in a finally).
- **ClassLoader leaks** — common in app servers when redeploying.
- **How to detect:** watch for old-gen memory that keeps rising after Full GCs, take a **heap dump**, and analyze it in **Eclipse MAT** or VisualVM (the "dominator tree" shows what's retaining memory).

### Q41. Stack vs Heap?
The two main runtime memory areas, with different rules:
- **Stack** — **thread-private** (each thread has its own), stores method call frames: local variables, primitive values, and object *references* (not the objects themselves). It's LIFO and **automatically freed** when a method returns — very fast, no GC needed. It's small; deep recursion causes **`StackOverflowError`**.
- **Heap** — **shared across all threads**, stores the actual **objects and arrays**, and is managed by the **garbage collector**. It's much larger but slower to allocate and needs GC. When it fills up and can't reclaim enough, you get **`OutOfMemoryError`**.
- **Example:** `Person p = new Person();` — the reference `p` sits on the stack; the `Person` object sits on the heap.

### Q42. What is class loading? Class loader hierarchy?
Class loading is how the JVM **finds, loads, and prepares `.class` files** into memory the first time they're needed (lazy loading). It happens in phases: **Loading** (read the bytecode) → **Linking** (Verify the bytecode is safe/valid → Prepare static fields with defaults → Resolve symbolic references) → **Initialization** (run static initializers/blocks).
Class loaders form a **hierarchy that uses the "parent-first delegation" model**: before a loader tries to load a class, it **asks its parent first**:
- **Bootstrap** class loader — loads core JDK classes (`java.lang.*`).
- **Platform/Extension** class loader — loads extension/platform classes.
- **Application (System)** class loader — loads your application's classes from the classpath.
**Why delegation matters:** it ensures core classes (like `java.lang.String`) are always loaded by the trusted bootstrap loader and can't be spoofed by application code — a security and consistency guarantee. Frameworks/app servers sometimes use custom class loaders for isolation (e.g., separate loaders per deployed app).


---

## F. Design Patterns (know 5–6 well)
- **Singleton** — one instance (use enum or double-checked locking with `volatile`).
- **Factory / Abstract Factory** — decouple object creation.
- **Builder** — construct complex objects step by step (immutable).
- **Strategy** — swap algorithms at runtime (great with lambdas).
- **Observer** — event notification (pub/sub).
- **Decorator** — add behavior dynamically (e.g., `BufferedReader`).
- **Dependency Injection** — Spring's core (inversion of control).

```java
// Thread-safe singleton
public enum Config { INSTANCE; private final Properties p = load(); }
```

---

## ⚡ Rapid-Fire
- **autoboxing** — auto conversion primitive ↔ wrapper; beware NPE on unboxing null & performance in loops.
- **transient** — field excluded from serialization.
- **static block** — runs once at class load.
- **`this` vs `super`** — current vs parent reference.
- **shallow vs deep copy** — copy references vs copy whole object graph.
- **method overloading (compile-time)** vs **overriding (runtime)**.
- **immutability recipe** — final class, final private fields, no setters, defensive copies, init in constructor.

---
---

# PART 2 — Advanced & Tough Questions (with detailed explanations + examples)

> These are the "senior engineer" questions that separate a 7+ year candidate from a junior. Read the reasoning, not just the answer.

## T1. Explain the Java Memory Model (JMM) — happens-before, visibility, reordering.
**Why it's asked:** to test if you *really* understand concurrency, not just `synchronized`.

The JMM defines **when a write by one thread becomes visible to a read by another**, and what reorderings the compiler/CPU may perform. Without synchronization, there is **no guarantee** another thread ever sees your write (it may sit in a CPU cache/register).

- **happens-before** is the key relationship: if action A *happens-before* B, then A's effects are visible to B. Established by:
  - Program order within a single thread.
  - `synchronized` — unlock happens-before a subsequent lock on the same monitor.
  - `volatile` — a write happens-before every subsequent read of that variable.
  - `Thread.start()` happens-before the started thread's actions; a thread's actions happen-before another thread's `join()` returning.
  - `final` fields — safely published after construction (if `this` doesn't escape).

**Concrete bug example (no visibility guarantee):**
```java
class Worker {
    private boolean running = true;          // NOT volatile
    void stop() { running = false; }
    void run() { while (running) { /* work */ } } // may loop FOREVER
}
```
The `run()` thread may cache `running=true` and never see `stop()`'s write. Fix: make `running` **volatile** (establishes happens-before), or use `AtomicBoolean`.

**Follow-up — double-checked locking (classic trap):**
```java
class Singleton {
    private static volatile Singleton instance;   // volatile is REQUIRED
    static Singleton get() {
        if (instance == null) {                    // 1st check (no lock)
            synchronized (Singleton.class) {
                if (instance == null)              // 2nd check (locked)
                    instance = new Singleton();
            }
        }
        return instance;
    }
}
```
Without `volatile`, another thread could see a **partially constructed** object because `instance = new Singleton()` is not atomic (allocate → construct → assign can be reordered).

## T2. `hashCode()`/`equals()` — write a correct pair and explain the pitfalls.
```java
public final class Money {
    private final long amountCents;
    private final String currency;
    // constructor + getters...
    @Override public boolean equals(Object o) {
        if (this == o) return true;
        if (!(o instanceof Money m)) return false;      // pattern matching (17)
        return amountCents == m.amountCents && currency.equals(m.currency);
    }
    @Override public int hashCode() {
        return Objects.hash(amountCents, currency);
    }
}
```
**Pitfalls interviewers probe:**
- Mutating a field used in `hashCode()` **after** putting the object in a `HashSet` → the object is "lost" (found in the wrong bucket).
- Using `==` on wrapper objects / `String` instead of `.equals()`.
- Inconsistent `equals` (not symmetric/transitive) when using `instanceof` vs `getClass()` across subclasses.
- Forgetting: equal objects **must** have equal hashcodes; unequal objects *may* share a hashcode (collision).

## T3. `ConcurrentHashMap` internals + `computeIfAbsent` atomicity.
Java 8+ CHM uses an array of bins; writes lock only the **head of a single bin** (via `synchronized` on the node) or use **CAS** for empty bins — so different buckets can be updated concurrently. Reads are lock-free (nodes/values are `volatile`).

**Tough gotcha — check-then-act is NOT atomic even on CHM:**
```java
// BROKEN: two ops, race between them
if (!map.containsKey(k)) map.put(k, compute());
// CORRECT: single atomic operation
map.computeIfAbsent(k, key -> compute());
```
`computeIfAbsent` guarantees the mapping function runs **at most once** per absent key atomically — great for lazy caches. (Caveat: don't call back into the same map inside the function → can deadlock/livelock.)

## T4. Why can `i++` lose updates across threads, and how do you fix it three ways?
`i++` = read-modify-write (3 ops), not atomic. Two threads can both read `5`, both write `6` → one increment lost.
- **`synchronized`** block/method (mutual exclusion).
- **`AtomicInteger.incrementAndGet()`** (lock-free CAS).
- **`LongAdder`** (better under high contention — striped counters, sums on demand).

## T5. Fail-fast iteration — how to remove safely while iterating?
```java
List<Integer> list = new ArrayList<>(List.of(1,2,3,4));
// BROKEN: ConcurrentModificationException
for (Integer x : list) if (x % 2 == 0) list.remove(x);
// CORRECT #1: Iterator.remove()
Iterator<Integer> it = list.iterator();
while (it.hasNext()) if (it.next() % 2 == 0) it.remove();
// CORRECT #2: removeIf (Java 8)
list.removeIf(x -> x % 2 == 0);
```

## T6. Stream pitfalls & performance — when NOT to use parallel streams.
- **Stateful lambdas** in streams are a bug (shared mutable state across parallel threads).
- `parallelStream()` uses the **common ForkJoinPool** — a slow blocking task can starve the whole app. Avoid parallel streams for I/O; use them only for CPU-bound, large, splittable data with no shared state.
- `Collectors.toMap` throws on **duplicate keys** unless you pass a merge function:
```java
Map<String,Integer> m = list.stream()
   .collect(Collectors.toMap(Item::getName, Item::getQty, Integer::sum)); // merge dup keys
```
- Streams are **single-use** — reusing a consumed stream throws `IllegalStateException`.

## T7. `equals` with inheritance — `instanceof` vs `getClass()`?
`getClass()` breaks Liskov substitution (a subclass instance never equals a superclass instance), but keeps symmetry. `instanceof` is more flexible but can break symmetry across subclasses. Modern advice: make value classes `final` (or use records) to sidestep the problem.

## T8. What actually happens in `String s = "a" + b + "c";`?
The compiler rewrites string concatenation (Java 9+ via `invokedynamic`/`StringConcatFactory`; earlier via `StringBuilder`). **But concatenation in a loop** creates a new builder each iteration — O(n²). Use an explicit `StringBuilder` in loops.

## T9. Try-with-resources & suppressed exceptions.
```java
try (var conn = ds.getConnection();
     var ps = conn.prepareStatement(sql)) {   // auto-closed in reverse order
    ...
} // close() called even on exception; if close() also throws, it's "suppressed"
```
Resources close in **reverse** order; exceptions from `close()` are attached as **suppressed** to the primary exception (`getSuppressed()`). This is why try-with-resources beats manual `finally`.

## T10. G1 vs ZGC — how do you choose, and how do you diagnose a GC problem?
- **G1** (default) — region-based, balances throughput & pause; good general default; target pause via `-XX:MaxGCPauseMillis`.
- **ZGC/Shenandoah** — sub-millisecond pauses on very large heaps (tens of GB to TB); slightly lower throughput.
**Diagnosis approach (say this):** enable GC logs (`-Xlog:gc*`), look for frequent Full GCs / long pauses / rising old-gen after GC (leak signal) → take a **heap dump** → analyze in **Eclipse MAT** (dominator tree) to find the retained-set root. Common culprit: an unbounded static/`ThreadLocal` cache.

## T11. `ThreadLocal` leak in a thread pool — explain.
Pool threads are reused and never die, so a `ThreadLocal` value set during one request **stays** on the thread for the next request → stale data + memory leak. **Always `remove()` in a finally block** (this is exactly why frameworks clear `SecurityContextHolder`/MDC after each request).

## T12. Design: build a thread-safe, bounded, blocking cache (LRU).
```java
// Simple LRU via LinkedHashMap (not thread-safe by itself)
Map<K,V> lru = Collections.synchronizedMap(
    new LinkedHashMap<>(16, 0.75f, true) {          // accessOrder=true
        protected boolean removeEldestEntry(Map.Entry<K,V> e) {
            return size() > MAX;                     // evict oldest
        }
    });
```
For production, mention **Caffeine** (high-perf, W-TinyLFU eviction, TTL, async loading) instead of rolling your own.

## T13. Checked vs unchecked — the real-world stance.
Many modern codebases (and Spring) favor **unchecked** exceptions to avoid `throws` clutter and leaky abstractions, wrapping checked ones in custom runtime exceptions at boundaries. Be ready to argue both sides: checked = compiler-enforced handling (good for truly recoverable I/O), unchecked = cleaner APIs + centralized handling (`@ControllerAdvice`).

## T14. Rapid tough one-liners
- **Can you override a `static` method?** No — static methods are *hidden*, not overridden (resolved at compile time by reference type).
- **Can a `final` method be overloaded?** Yes (overloading ≠ overriding). It just can't be *overridden*.
- **Why is `Integer` caching (`-128..127`) a trap?** `Integer a=127,b=127; a==b` is true (cached); `a=128,b=128; a==b` is false (new objects). Always `.equals()`.
- **`Comparator` inconsistency with equals** can corrupt `TreeMap`/`TreeSet` (two "equal-by-comparator" keys collapse).
- **`volatile` on a 64-bit `long`/`double`** also guarantees atomic reads/writes (non-volatile 64-bit writes can tear on some JVMs).
- **`Arrays.asList()`** returns a fixed-size list backed by the array — `add()`/`remove()` throw `UnsupportedOperationException`.

---
---

# PART 3 — More Real Interview Questions (Easy Language, No Repeats)

## Q1. What are the different types of inner classes in Java?
Simply put, a class inside another class. Four kinds:
- **Member inner class** — normal class inside a class, needs an outer object to create.
- **Static nested class** — declared `static`, doesn't need an outer object (like a normal top-level class placed inside for organization).
- **Local inner class** — defined inside a method, only usable in that method.
- **Anonymous inner class** — a class with no name, created and used at once (common before lambdas, e.g., old `Runnable r = new Runnable(){...}`).

## Q2. What is the diamond problem, and how does Java avoid it with interfaces?
If a class could inherit the same method from two parents, which one wins? That's the "diamond problem." Java avoids it for classes by not allowing multiple class inheritance. With interfaces (which can have `default` methods since Java 8), if two interfaces give the same default method, Java **forces you to override it explicitly** in the implementing class — so there's no silent ambiguity.

## Q3. What are varargs? Give a simple example.
Varargs let a method accept a variable number of arguments using `...`.
```java
int sum(int... nums) {          // can call sum(), sum(1), sum(1,2,3)
    int total = 0;
    for (int n : nums) total += n;
    return total;
}
```
Internally it's treated as an array. Only one varargs parameter is allowed, and it must be the last parameter.

## Q4. Why are enums better than plain constants (`public static final int`)?
Enums are **type-safe** (compiler stops you passing a wrong value), can have **fields, constructors, and methods**, work great in `switch`, and print nicely (`toString()` gives the name). Plain `int` constants are just numbers — easy to mix up and no compiler safety.
```java
enum Status { PENDING, APPROVED, REJECTED }
```

## Q5. What is serialization? What is `serialVersionUID` for?
**Serialization** converts an object into a byte stream (to save to a file, send over network, or store in cache). The class must implement `Serializable`. `serialVersionUID` is a version number for the class — if you change the class later, this ID helps Java decide whether an old serialized object is still compatible with the new class, avoiding a `InvalidClassException`.

## Q6. What is a marker interface? Give an example.
An interface with **no methods** — it just "marks" a class as having a certain capability. Example: `Serializable`, `Cloneable`. The JVM/libraries check `if (obj instanceof Serializable)` to decide behavior, even though there's nothing to implement.

## Q7. What is Java Reflection? Where is it used practically?
Reflection lets code **inspect and manipulate classes, methods, and fields at runtime** — even private ones. Used heavily by frameworks: Spring uses it to create beans and inject dependencies, JUnit uses it to find and run `@Test` methods, Jackson uses it to map JSON to objects. You rarely use it directly in business code — but frameworks depend on it.

## Q8. What's the difference between `throw` and `throws`?
- `throw` — actually **throws** an exception instance: `throw new IllegalArgumentException("bad input");`
- `throws` — used in a method **signature** to declare that this method *might* throw a checked exception: `void readFile() throws IOException { ... }`

## Q9. What is exception chaining, and why is it useful?
When you catch one exception and throw a new one, you can pass the original as the **cause** so you don't lose the real reason for the failure:
```java
try {
    parseFile();
} catch (IOException e) {
    throw new ServiceException("Failed to process file", e);   // e is the "cause"
}
```
Later, `getCause()` lets you see the original exception in logs — very useful for debugging in production.

## Q10. What is a multi-catch block?
Catching multiple exception types in one block if you handle them the same way:
```java
try {
    doSomething();
} catch (IOException | SQLException e) {
    log.error("Operation failed", e);
}
```
Saves duplicate code, but the caught types must not have a parent-child relationship.

## Q11. Can you have a `try` block without a `catch`?
Yes — `try` with only `finally` is legal. Used when you just want to guarantee cleanup, without needing to handle the exception there (it still propagates up).
```java
try {
    lock.lock();
    doWork();
} finally {
    lock.unlock();     // always runs, exception or not
}
```

## Q12. What is object cloning? Shallow vs deep clone, simply explained.
Cloning creates a copy of an object. A class must implement `Cloneable` and override `clone()`.
- **Shallow clone** — copies the object, but if it has fields that are objects (like a `List`), the copy still points to the **same** inner objects — change one, both are affected.
- **Deep clone** — copies the object **and** all the objects it refers to, so the copy is fully independent.
Most developers avoid Java's built-in `clone()` (it's clunky) and instead use a copy constructor or a library.

## Q13. What is the String pool, and what does `intern()` do?
Java keeps a special memory area called the **String pool** for string literals, so identical literals (`"hello"`) share the same object instead of creating duplicates — saves memory. `"a".intern()` forces a string (even one created with `new String("a")`) to use the pooled version, so `==` comparison would then work like `.equals()`.

## Q14. What's the difference between `transient` and `volatile`? (easy to confuse!)
- `transient` — tells **serialization** to skip this field (don't save it when converting the object to bytes). Example: skip saving a password field.
- `volatile` — tells **threads** to always read/write this field from main memory (visibility guarantee), nothing to do with serialization.
They solve completely different problems despite sounding similar.

## Q15. What happens if you call `.get()` on an empty `Optional`?
It throws `NoSuchElementException`. That's why you should use `orElse()`, `orElseGet()`, `orElseThrow()`, or check `isPresent()`/`isEmpty()` first, rather than blindly calling `.get()`.

## Q16. What is covariant return type?
When overriding a method, the child class method can return a **more specific (sub) type** than the parent's return type — not necessarily the exact same type.
```java
class Animal { Animal reproduce() { return new Animal(); } }
class Dog extends Animal { 
    @Override Dog reproduce() { return new Dog(); }   // covariant return - OK
}
```

## Q17. What are Java access modifiers, in one simple table?
| Modifier | Same class | Same package | Subclass (other package) | Everywhere |
|---|---|---|---|---|
| `private` | ✅ | ❌ | ❌ | ❌ |
| default (no modifier) | ✅ | ✅ | ❌ | ❌ |
| `protected` | ✅ | ✅ | ✅ | ❌ |
| `public` | ✅ | ✅ | ✅ | ✅ |

## Q18. What is the `var` keyword (local type inference), and what are its limits?
`var` lets the compiler figure out the type from the right side: `var list = new ArrayList<String>();` — it's still **statically typed** (not like JavaScript), just less typing. Limits: only for **local variables** (not fields, method params, or return types), must be initialized on the same line, and can't be assigned `null` without a type hint.

## Q19. What's the real difference between method overloading resolution when types are ambiguous?
If you call `print(null)` and there are overloads `print(String s)` and `print(Object o)`, Java picks the **most specific type** — `String` wins because it's more specific than `Object`. But if two unrelated overloads both match equally well, you'll get a **compile-time ambiguity error** — the compiler won't guess for you.

## Q20. Simple way to explain "Java is pass-by-value" (a very common trick question).
Java is **always pass-by-value** — but for objects, the "value" being passed is the **reference** (like a copy of an address). So:
- If you reassign the parameter inside the method, the caller's variable is untouched.
- If you mutate the object the reference points to (like `list.add(x)`), the caller **does** see the change — because both references point to the same object.
This is why people wrongly think Java is "pass-by-reference" for objects — it's actually pass-by-value **of the reference**.

---

## E. Real Interview Questions (Asked in Actual Interviews)

> These are questions asked in a real interview — answered at the depth the interviewer expected. Read these as a focused, high-yield set.

### RQ1. Difference between `WHERE` and `HAVING`?
Both filter rows, but they operate at **different stages** of query execution, and that stage difference is the whole answer:
- **`WHERE`** filters **individual rows *before* any grouping/aggregation happens**. It cannot use aggregate functions (`SUM`, `COUNT`, `AVG`) because those don't exist yet at this stage. Example: `WHERE salary > 50000` keeps only rows where each employee earns over 50k.
- **`HAVING`** filters **groups *after* `GROUP BY` and aggregation**. It's used to filter on aggregate results. Example: `HAVING SUM(salary) > 500000` keeps only departments whose total salary exceeds 500k.
- **Execution order (memorize this):** `FROM → WHERE → GROUP BY → HAVING → SELECT → ORDER BY`. So `WHERE` prunes rows first (efficient — smaller dataset to group), then `HAVING` prunes the grouped results.
- **Combined example:**
```sql
SELECT department, AVG(salary)
FROM employees
WHERE status = 'ACTIVE'        -- row filter first
GROUP BY department
HAVING AVG(salary) > 60000;    -- group filter after aggregation
```
- **Performance tip:** always push filters into `WHERE` when possible (it reduces the number of rows *before* grouping); only use `HAVING` for conditions that genuinely depend on an aggregate.

### RQ2. Does `HashMap` allow duplicate keys?
**No** — keys in a `HashMap` are **unique**. If you `put()` a key that already exists, it does **not** create a second entry; it **overwrites** the existing value and returns the old value.
```java
Map<String,Integer> m = new HashMap<>();
m.put("a", 1);
m.put("a", 2);   // overwrites — no duplicate key
System.out.println(m.get("a")); // 2
System.out.println(m.size());   // 1
```
- **Values** can be duplicated freely — only keys are unique.
- **How uniqueness is enforced:** when you `put`, `HashMap` computes the key's `hashCode()` to find the bucket, then uses `equals()` to check if the key already exists in that bucket. If `equals()` matches, it replaces the value. This is exactly why keys must have correct `hashCode()`/`equals()`.
- A `HashMap` allows **one `null` key** and multiple `null` values.

### RQ3. `HashSet` allows only one value at a time (no duplicates) — but how does it use key-value pairs internally?
A `HashSet` is essentially a **`HashMap` in disguise**. Internally, `HashSet` is **backed by a `HashMap`**:
- Each element you add to the set becomes a **key** in the internal `HashMap`.
- The **value** for every key is a single shared dummy constant — a `static final Object PRESENT = new Object();`.
```java
// Simplified from the JDK source:
public class HashSet<E> {
    private transient HashMap<E,Object> map;
    private static final Object PRESENT = new Object();

    public boolean add(E e) {
        return map.put(e, PRESENT) == null;  // returns true only if key was new
    }
}
```
- **Why this gives uniqueness for free:** because `HashMap` keys are unique, adding a duplicate element just re-`put`s the same key, which returns the old `PRESENT` value (non-null), so `add()` returns `false` and the set size doesn't grow.
- This is why `HashSet` elements need proper `hashCode()`/`equals()` — the set delegates all that logic to the underlying map's key handling.

### RQ4. What upgrades came from Java 11 to Java 17?
Java 17 (an **LTS** release, like 11) bundled several major language and JVM improvements introduced across versions 12–17:
- **Records (Java 16)** — concise immutable data classes: `record Point(int x, int y) {}` auto-generates constructor, getters, `equals()`, `hashCode()`, `toString()`. Great for DTOs.
- **Sealed classes (Java 17)** — restrict which classes can extend/implement a type: `sealed interface Shape permits Circle, Square {}`. Gives controlled, exhaustive hierarchies (pairs well with pattern matching).
- **Pattern matching for `instanceof` (Java 16)** — `if (obj instanceof String s) { use s; }` — no explicit cast needed.
- **Switch expressions (Java 14)** — switch can now return a value with arrow syntax and no fall-through:
```java
String type = switch (day) {
    case SATURDAY, SUNDAY -> "Weekend";
    default -> "Weekday";
};
```
- **Text blocks (Java 15)** — multi-line strings with `"""..."""`, great for JSON/SQL/HTML.
- **Helpful `NullPointerException` messages (Java 14)** — tells you *exactly which variable* was null.
- **New garbage collectors** — **ZGC** and **Shenandoah** became production-ready (low-latency, sub-millisecond pauses).
- **Performance & security** — stronger encapsulation of JDK internals (strong encapsulation of internal APIs in Java 16/17), new random number generator interfaces, macOS/AArch64 support.
- **Removed/deprecated** — the Applet API, Security Manager deprecated, RMI Activation removed.
- **One-liner:** "Java 17 brought records, sealed classes, pattern matching, switch expressions, and text blocks — code got much more concise and expressive, plus better GCs and NPE messages."

### RQ5. Difference between `Comparable` and `Comparator`?
Both define ordering, but the key difference is **where the sorting logic lives** and **how many orderings you can have**:
- **`Comparable<T>`** — implemented **by the class itself** (the class "knows how to compare itself"). It has **one** method `compareTo(T other)`. This defines the class's **natural ordering** — there can only be **one** natural order. Example: `String` and `Integer` implement `Comparable`. You use it when there's an obvious single default sort (e.g., employees by id).
```java
class Employee implements Comparable<Employee> {
    int id;
    public int compareTo(Employee o) { return Integer.compare(this.id, o.id); }
}
Collections.sort(list); // uses compareTo
```
- **`Comparator<T>`** — a **separate/external** object defining ordering. It has `compare(T a, T b)`. You can create **many different comparators** for the same class (by name, by salary, by date), and you don't need to modify the original class. Ideal when you need multiple sort orders or can't edit the class.
```java
list.sort(Comparator.comparing(Employee::getSalary).reversed());
list.sort(Comparator.comparing(Employee::getName));
```
- **Summary:** `Comparable` = one natural order, inside the class, `compareTo`. `Comparator` = many custom orders, outside the class, `compare`. Both return negative/zero/positive for less/equal/greater.

### RQ6. Why not use `equals()` for sorting — why `Comparable`?
Because they answer **different questions**:
- **`equals()`** answers a **boolean** question: "are these two objects the same?" It returns only `true`/`false`. It has **no notion of order** — it can't tell you whether A comes *before* or *after* B.
- **`compareTo()` / `compare()`** answers an **ordering** question: it returns a **negative, zero, or positive** integer telling you A is *less than*, *equal to*, or *greater than* B. That three-way result is exactly what sorting algorithms need to arrange elements.
- **Why sorting needs the int, not a boolean:** to sort, the algorithm must repeatedly decide relative position ("does this go left or right?"). A `true`/`false` from `equals()` can't express "before/after," so it's useless for ordering.
- **Consistency note:** it's good practice (though not strictly required) that `compareTo` be *consistent with* `equals` — i.e., `a.compareTo(b) == 0` should ideally mean `a.equals(b)`. Sorted collections like `TreeSet`/`TreeMap` use `compareTo`/`compare` (not `equals`) to decide uniqueness, so inconsistency there can cause surprising behavior.

### RQ7. Implement `Comparable` to sort an `Employee` class by employee id.
```java
public class Employee implements Comparable<Employee> {
    private int id;
    private String name;
    private double salary;

    public Employee(int id, String name, double salary) {
        this.id = id; this.name = name; this.salary = salary;
    }

    public int getId() { return id; }
    public String getName() { return name; }
    public double getSalary() { return salary; }

    // Natural ordering by id (ascending)
    @Override
    public int compareTo(Employee other) {
        return Integer.compare(this.id, other.id);
        // NEVER do (this.id - other.id) — can overflow for large ints
    }

    @Override
    public String toString() {
        return id + ":" + name + ":" + salary;
    }
}

// Usage:
List<Employee> employees = new ArrayList<>(List.of(
    new Employee(3, "Alice", 90000),
    new Employee(1, "Bob", 70000),
    new Employee(2, "Charlie", 80000)
));
Collections.sort(employees);          // uses compareTo -> sorted by id: 1,2,3
// or:  employees.sort(null);         // natural ordering
```
- **Key point:** use `Integer.compare(a, b)` instead of `a - b` to avoid integer overflow.
- If you later need a different order without editing the class, use a `Comparator`: `employees.sort(Comparator.comparing(Employee::getSalary));`

### RQ8. What is constructor chaining?
Constructor chaining is **one constructor calling another constructor** so initialization logic is written once and reused. Two forms:
- **`this(...)`** — calls **another constructor in the same class** (used for default values / reducing duplication). Must be the **first statement** in the constructor.
- **`super(...)`** — calls a **parent-class constructor**. Also must be the first statement. If you don't write it, the compiler inserts an implicit `super()` (no-arg) call automatically.
```java
class Employee {
    int id; String name; double salary;

    Employee() {
        this(0, "Unknown");            // chains to the 2-arg constructor
    }
    Employee(int id, String name) {
        this(id, name, 50000);         // chains to the 3-arg constructor
    }
    Employee(int id, String name, double salary) {
        this.id = id; this.name = name; this.salary = salary;
    }
}
```
- **Why it matters:** avoids duplicated initialization code, keeps a single source of truth, and guarantees the parent is initialized before the child (constructor runs top-down through the hierarchy).
- **Rule:** you can use `this(...)` **or** `super(...)` in a constructor, but not both, and whichever you use must be the first line.

### RQ9. Given a list of employees, parse it and get the second-highest salary.
Multiple approaches — show the modern Stream one and mention the classic single-pass one.

**Stream approach (clean, readable):**
```java
Optional<Employee> secondHighest = employees.stream()
    .sorted(Comparator.comparingDouble(Employee::getSalary).reversed())
    .distinct()                 // if you want distinct salaries, map first (below)
    .skip(1)                    // skip the highest
    .findFirst();
```
**If "second highest *distinct* salary" is required (handles ties):**
```java
Optional<Double> secondHighestSalary = employees.stream()
    .map(Employee::getSalary)
    .distinct()                                  // remove duplicate salaries
    .sorted(Comparator.reverseOrder())
    .skip(1)                                     // skip the top one
    .findFirst();

secondHighestSalary.ifPresentOrElse(
    s -> System.out.println("Second highest: " + s),
    () -> System.out.println("Not enough distinct salaries")
);
```
**Efficient single-pass approach (O(n), no sorting):**
```java
double highest = Double.NEGATIVE_INFINITY, second = Double.NEGATIVE_INFINITY;
for (Employee e : employees) {
    double s = e.getSalary();
    if (s > highest) { second = highest; highest = s; }
    else if (s > second && s < highest) { second = s; }
}
```
- **Talking points:** sorting is O(n log n); the single-pass loop is O(n). Always ask the interviewer: "should duplicate salaries count as one?" — it changes the answer. Handle the edge case of fewer than two distinct salaries.

### RQ10. Difference between INNER JOIN and OUTER JOIN?
Joins combine rows from two tables based on a matching condition; the difference is **what happens to non-matching rows**:
- **INNER JOIN** — returns **only rows that have a match in *both* tables**. Non-matching rows from either side are dropped. Example: employees who *have* a department; employees with no department are excluded.
- **OUTER JOIN** — keeps non-matching rows too, filling missing columns with `NULL`. Three variants:
  - **LEFT (OUTER) JOIN** — all rows from the **left** table + matching rows from the right; unmatched right side is `NULL`. (e.g., *all* employees, even those without a department.)
  - **RIGHT (OUTER) JOIN** — all rows from the **right** table + matching from the left; unmatched left side is `NULL`.
  - **FULL (OUTER) JOIN** — all rows from **both** tables; wherever there's no match, the missing side is `NULL`.
```sql
-- INNER: only employees WITH a matching department
SELECT e.name, d.name FROM employees e
INNER JOIN departments d ON e.dept_id = d.id;

-- LEFT OUTER: ALL employees, dept name NULL if none
SELECT e.name, d.name FROM employees e
LEFT JOIN departments d ON e.dept_id = d.id;
```
- **Mental picture:** INNER = intersection of two circles; LEFT = whole left circle; FULL = union of both circles.
- **Common use:** LEFT JOIN is great for "find records with no match" — `LEFT JOIN ... WHERE d.id IS NULL` finds employees with no department.

### RQ11. Explain the Open/Closed Principle (the "O" in SOLID).
**"Software entities should be open for extension but closed for modification."** Meaning: you should be able to **add new behavior without changing existing, tested code**.
- **Why:** every time you edit working code, you risk breaking it and must re-test it. Instead, design so new features are added by **writing new classes** that plug into an existing abstraction.
- **The technique:** depend on **abstractions (interfaces/abstract classes)**, then add new implementations rather than editing old ones (polymorphism).
- **Bad (violates OCP)** — adding a new shape forces you to edit this method every time:
```java
double area(Object shape) {
    if (shape instanceof Circle c) return Math.PI * c.r * c.r;
    else if (shape instanceof Square s) return s.side * s.side;
    // must EDIT this method for every new shape ❌
}
```
- **Good (follows OCP)** — add a new shape by writing a new class, no edits to existing code:
```java
interface Shape { double area(); }
class Circle implements Shape { double r; public double area(){ return Math.PI*r*r; } }
class Square implements Shape { double side; public double area(){ return side*side; } }
// New shape? Just add:  class Triangle implements Shape { ... }  ✅
```
- **Real-world tie-in:** payment processors, notification channels, discount strategies — all classic OCP via the Strategy pattern. "I add a new `PaymentProvider` implementation instead of editing a giant `switch`."

### RQ12. What is lazy loading in Spring Data JPA?
**Lazy loading** means a related entity/collection is **not fetched from the database immediately** — it's loaded **only when you actually access it**, saving unnecessary queries and memory.
- **Default fetch types:** `@OneToMany` and `@ManyToMany` are **LAZY** by default; `@ManyToOne` and `@OneToOne` are **EAGER** by default.
```java
@Entity
class Department {
    @OneToMany(mappedBy = "department", fetch = FetchType.LAZY)
    private List<Employee> employees;   // NOT loaded until you call getEmployees()
}
```
- **How it works:** Hibernate returns a **proxy** (a placeholder object) in place of the real collection/entity. The moment you access it (e.g., `dept.getEmployees().size()`), Hibernate fires a SQL query to load the real data.
- **Why:** avoids loading huge object graphs you may never use — e.g., loading a `Department` shouldn't drag in thousands of employees unless you need them.
- **The classic pitfall — `LazyInitializationException`:** if you try to access a lazy field **after the persistence context (session/transaction) is closed**, Hibernate can't run the query and throws this exception. Fixes: keep the transaction open (`@Transactional`), use a **fetch join** (`JOIN FETCH`), use an **entity graph**, or map to a DTO within the transaction.
- **EAGER vs LAZY tradeoff:** EAGER can cause the **N+1 query problem** and load too much; LAZY is more efficient but requires an open session. Prefer LAZY + explicit fetch joins where needed.

### RQ13. For a lazy-loaded list from the DB, what is there until it's loaded?
Until you access it, the field holds a **proxy / lazy placeholder** — specifically a Hibernate collection wrapper (e.g., `PersistentBag`, `PersistentList`, or `PersistentSet`), **not** the real data and **not** `null`.
- It's an object that "looks like" a `List` but contains **no elements yet** — it just holds a reference to the session and the info needed to fetch the data later.
- **The trigger:** the first time you call something that needs the actual contents (`size()`, `iterator()`, `get(0)`, a for-each loop), Hibernate executes the SQL and populates it — this is called **initialization**.
- **Key consequence:** if the Hibernate **session is already closed** when you first touch it, you get a **`LazyInitializationException`**, because the proxy has no open session to run its query.
- **How to check without triggering load:** `Hibernate.isInitialized(collection)` tells you whether it's been loaded yet; `Hibernate.initialize(collection)` forces the load while the session is open.

### RQ14. Explain the `final` keyword in Java.
`final` means **"cannot change / cannot be redefined."** It has three distinct uses:
1. **`final` variable** — can be assigned **only once**; after that it can't be reassigned. Used for constants (`static final double PI = 3.14159;`) and for values captured by lambdas/anonymous classes (they require effectively-final variables).
2. **`final` method** — **cannot be overridden** by a subclass. Used to lock down behavior you don't want changed (e.g., a security-critical algorithm).
3. **`final` class** — **cannot be extended** (subclassed). `String`, `Integer`, and all wrapper classes are `final`. Used for immutability and safety.
- **Crucial subtlety for reference variables:** `final` makes the **reference** unchangeable, **not the object it points to**. So `final List<String> list = new ArrayList<>();` means you can never make `list` point to a different list — but you **can still** call `list.add("x")` to mutate its contents. (See next question.)
- **Blank final:** a `final` field can be left unassigned at declaration if it's assigned exactly once in every constructor.

### RQ15. If a collection is a `final` variable, can it be updated?
**Yes — you can still add/remove/modify its elements.** `final` only prevents **reassigning the reference**, not mutating the object.
```java
final List<String> list = new ArrayList<>();
list.add("a");          // ✅ allowed — mutating contents
list.add("b");          // ✅ allowed
list.remove("a");       // ✅ allowed
// list = new ArrayList<>();   // ❌ COMPILE ERROR — can't reassign a final reference
```
- **Why:** `final` locks the *variable* (the "pointer"), not the *object's internal state*. The list object itself is fully mutable.
- **To make the contents truly unmodifiable**, you need something else:
  - `List<String> immutable = List.of("a", "b");` (Java 9+, throws `UnsupportedOperationException` on mutation)
  - `Collections.unmodifiableList(list)` (a read-only view)
- **Interview one-liner:** "`final` = you can't repoint the reference, but the object it points to can still be changed. To prevent element changes, use `List.of()` or `Collections.unmodifiableList()`."

### RQ16. Difference between `TreeSet` and `HashSet`?
Both are `Set`s (no duplicates), but they differ in **ordering, performance, and backing structure**:

| Aspect | `HashSet` | `TreeSet` |
|---|---|---|
| **Ordering** | **No order** — iteration order is unpredictable | **Sorted order** (natural or by `Comparator`) |
| **Backing structure** | Backed by a `HashMap` (hash table) | Backed by a `TreeMap` (Red-Black balanced BST) |
| **Performance** | `add`/`remove`/`contains` = **O(1)** average | `add`/`remove`/`contains` = **O(log n)** |
| **null** | Allows **one** `null` element | **No `null`** (would throw `NullPointerException` on compare) |
| **Requirements** | Needs correct `hashCode()`/`equals()` | Needs `Comparable` or a `Comparator` |
| **Extra methods** | Basic Set operations only | Navigation: `first()`, `last()`, `ceiling()`, `floor()`, `headSet()`, `tailSet()`, `subSet()` |

- **When to use `HashSet`:** you just need uniqueness and fastest possible lookups, order doesn't matter. (Most common.)
- **When to use `TreeSet`:** you need elements kept **sorted**, or need range/navigation queries (e.g., "give me all values ≥ x").
- **Also mention `LinkedHashSet`:** hash-based (O(1)) but preserves **insertion order** — a middle ground when you want fast ops *and* predictable iteration order.

---
---

# PART 5 — Senior Real-Interview Questions (concurrency, JVM, streams — deep)

> These probe depth. Answers are detailed and speak-out-loud ready.

### SQ1. How does `HashMap` work internally (buckets, collisions, resizing, Java 8 treeification)?
- A `HashMap` is an **array of buckets**. On `put(key, value)`: it computes `key.hashCode()`, applies an internal **spreading function** (`h ^ (h >>> 16)`) to mix high bits, then maps it to a bucket index with `(n - 1) & hash` (works because capacity is a power of two).
- **Collisions** (two keys landing in the same bucket) are stored as a **linked list**. Since **Java 8**, once a bucket's list exceeds **8 entries** (and capacity ≥ 64), it's **treeified** into a **balanced red-black tree**, improving worst-case lookup from **O(n) to O(log n)** (a defense against hash-collision DoS).
- **Load factor & resizing** — default load factor **0.75**; when `size > capacity × 0.75`, the map **resizes** (doubles capacity) and **rehashes** entries. Resizing is expensive, so pre-size with `new HashMap<>(expectedSize)` if you know the size.
- **Keys** need correct `hashCode()`/`equals()`; allows one `null` key.
- **One-liner:** "Array of buckets indexed by a spread hashcode; collisions are linked lists that treeify to red-black trees after 8 entries; resizes at 0.75 load factor by doubling and rehashing."

### SQ2. `HashMap` vs `ConcurrentHashMap` — why not just use a synchronized map?
- **`HashMap`** is **not thread-safe** — concurrent writes can corrupt it (in Java 7 an infinite loop during resize; in Java 8 lost updates / `ConcurrentModificationException`).
- **`Collections.synchronizedMap`** wraps every method in a **single lock** — thread-safe but serializes *all* access (poor concurrency).
- **`ConcurrentHashMap`** is designed for concurrency: it locks at a **fine granularity** (in Java 8+, per-bucket using CAS + `synchronized` on the bucket head, not the old segment locks). Reads are mostly **lock-free**; writes only contend on the specific bucket. It **doesn't allow null** keys/values (to avoid ambiguity in concurrent gets). Iterators are **weakly consistent** (no `ConcurrentModificationException`).
- **One-liner:** "Use `ConcurrentHashMap` for concurrent access — it locks per-bucket (CAS + synchronized head) so reads are lock-free and writes contend only on one bucket, unlike a globally-locked synchronized map."

### SQ3. Explain the Java Memory Model, `volatile`, and the happens-before relationship.
- Each thread may cache variables in registers/CPU caches, so one thread's write may not be visible to another — plus the compiler/CPU can **reorder** instructions. The **Java Memory Model (JMM)** defines when a write by one thread is guaranteed visible to another.
- **`volatile`** guarantees two things: (1) **visibility** — a write is flushed to main memory and reads always see the latest value (no caching); (2) **ordering** — it prevents reordering across the volatile access (a memory barrier). It does **NOT** provide atomicity for compound actions (`count++` is still not atomic even if `count` is volatile).
- **happens-before** — the JMM's ordering guarantee: if action A happens-before B, A's effects are visible to B. Established by: unlocking a monitor happens-before locking it; a volatile write happens-before a subsequent volatile read; `Thread.start()` happens-before the thread's actions; a thread's actions happen-before another thread's `join()` returns.
- **One-liner:** "`volatile` gives visibility + ordering (a memory barrier) but not atomicity; the JMM's happens-before rules define when one thread's writes are guaranteed visible to another."

### SQ4. `synchronized` vs `ReentrantLock` — when would you use each?
- **`synchronized`** — the built-in intrinsic lock (a keyword). Simple, automatically released on exit/exception, and JVM-optimized (biased/lightweight locking). Limitations: can't try-without-blocking, no timeout, not interruptible, only one implicit condition, and it's block/method-scoped.
- **`ReentrantLock`** (java.util.concurrent) — an explicit lock with more power: **`tryLock()`** (non-blocking or with timeout), **interruptible** locking (`lockInterruptibly()`), **fairness** option (FIFO), and **multiple `Condition`** objects for fine-grained wait/signal. Downside: you **must** `unlock()` in a `finally` block or you leak the lock.
- **`ReentrantReadWriteLock` / `StampedLock`** — allow many concurrent readers but exclusive writers (great for read-heavy data).
- **Guidance:** use `synchronized` by default for simplicity; reach for `ReentrantLock` when you need tryLock/timeout/interruptibility/fairness/multiple conditions.

### SQ5. What is a deadlock and how do you prevent it?
- **Deadlock** — two+ threads each hold a lock the other needs, so both wait forever. Requires four **Coffman conditions**: mutual exclusion, hold-and-wait, no preemption, and circular wait.
- **Prevention:**
  - **Lock ordering** — always acquire multiple locks in the **same global order** (breaks circular wait). Most common fix.
  - **`tryLock` with timeout** — back off and retry if you can't get all locks (breaks hold-and-wait).
  - **Reduce lock scope** / use a single coarser lock, or lock-free structures.
  - Avoid calling foreign/unknown code while holding a lock.
- **Detection:** thread dump (`jstack`) shows "deadlock detected" with the cycle.
- **One-liner:** "Deadlock is a circular wait on locks; I prevent it primarily with a consistent global lock-ordering, and `tryLock` with timeouts as a fallback."

### SQ6. Explain the `ExecutorService` / thread pools and how you size them.
- Creating a thread per task is expensive and unbounded (risk of OOM). A **thread pool** (`ExecutorService`) reuses a fixed set of threads and queues tasks.
- **Factory types:** `newFixedThreadPool(n)`, `newCachedThreadPool()` (grows/shrinks), `newSingleThreadExecutor()`, `newScheduledThreadPool()`, and (Java 21) `newVirtualThreadPerTaskExecutor()`.
- **Prefer building your own `ThreadPoolExecutor`** to control corePoolSize, maxPoolSize, the **queue** (bounded!), the **thread factory**, and the **rejection policy** — `Executors.newFixedThreadPool` uses an *unbounded* queue that can hide backpressure and OOM.
- **Sizing:** CPU-bound → ~**number of cores** (`Runtime.availableProcessors()`); I/O-bound → **more** threads (cores × (1 + wait/compute)) since threads block on I/O.
- **Always shut down** (`shutdown()` + `awaitTermination()`).
- **One-liner:** "Use a bounded `ThreadPoolExecutor` with an explicit queue and rejection policy; size ~cores for CPU-bound and higher for I/O-bound work — and prefer virtual threads (Java 21) for massive blocking I/O concurrency."

### SQ7. What are virtual threads (Project Loom, Java 21)?
- **Virtual threads** are lightweight threads managed by the **JVM**, not the OS. You can have **millions** of them; when one **blocks** on I/O, the JVM **unmounts** it from its carrier (platform) thread and runs another — so blocking code scales like async code but stays **simple and readable**.
- **Why it matters:** the classic "thread-per-request blocking" model becomes cheap again, reducing the need for complex reactive/async code for I/O-bound workloads.
- **Caveats:** they don't speed up **CPU-bound** work; avoid pinning (holding a `synchronized` block/native call while blocking pins the carrier thread — prefer `ReentrantLock`); pool sizing changes (use `newVirtualThreadPerTaskExecutor`).
- **One-liner:** "Virtual threads let you write simple blocking code that scales to millions of concurrent I/O tasks, because the JVM unmounts blocked threads from OS carriers — Loom's answer to reactive complexity."

### SQ8. `CompletableFuture` — how do you compose async work?
- `CompletableFuture` represents an async computation you can **chain and combine** without blocking:
  - **`thenApply`** (transform result), **`thenCompose`** (flatMap — chain another async call), **`thenCombine`** (combine two futures), **`allOf`/`anyOf`** (wait for all/any), **`exceptionally`/`handle`** (error handling).
```java
CompletableFuture.supplyAsync(() -> fetchUser(id))
  .thenCompose(user -> CompletableFuture.supplyAsync(() -> fetchOrders(user)))
  .thenApply(orders -> summarize(orders))
  .exceptionally(ex -> fallback());
```
- **Gotcha:** default async methods run on the common `ForkJoinPool` — pass a **custom executor** for blocking I/O so you don't starve the common pool.
- **One-liner:** "`CompletableFuture` composes async pipelines with `thenApply/thenCompose/thenCombine/allOf` plus `exceptionally/handle` for errors — and I supply a dedicated executor for blocking work."

### SQ9. How do Java Streams work? Intermediate vs terminal, and lazy evaluation.
- A **Stream** is a pipeline for processing a sequence of elements functionally. It has:
  - **Intermediate operations** (`map`, `filter`, `sorted`, `distinct`, `limit`) — **lazy**; they build up the pipeline and return a new stream, doing nothing until a terminal op runs.
  - **Terminal operations** (`collect`, `forEach`, `reduce`, `count`, `findFirst`, `anyMatch`) — **trigger execution** and produce a result or side effect.
- **Laziness enables fusion + short-circuiting:** elements flow through the whole pipeline one at a time, and ops like `findFirst`/`limit`/`anyMatch` can stop early without processing everything.
- **`Collectors`** — `toList`, `toMap`, `groupingBy`, `partitioningBy`, `joining`, `summingInt`.
- **Parallel streams** (`.parallel()`) split work across the common ForkJoinPool — only worth it for large datasets + CPU-bound, stateless, non-order-dependent ops; can hurt for small/IO-bound work.
- **One-liner:** "Intermediate ops are lazy and build the pipeline; the terminal op triggers a single pass with operation fusion and short-circuiting — that laziness is what makes streams efficient."

### SQ10. `Optional` — what problem does it solve and how should you use it?
- **`Optional<T>`** is a container that explicitly represents "a value that may be absent," making **null-handling explicit** in the type and reducing `NullPointerException`s.
- **Good use:** as a **return type** for methods that might not find a result (`findById` → `Optional<User>`). Chain with `map`, `filter`, `flatMap`, and resolve with `orElse`, `orElseGet` (lazy), `orElseThrow`, `ifPresent`.
- **Anti-patterns:** don't use `Optional` for **fields** or **method parameters** (overhead, not `Serializable`), don't call `.get()` without checking, and don't wrap collections (return an empty collection instead).
- **One-liner:** "`Optional` makes 'maybe absent' explicit in the API and lets you chain safely — use it as a return type, resolve with `orElseGet`/`orElseThrow`, and never as a field or parameter."

### SQ11. What is garbage collection and which collectors should you know?
- **GC** automatically reclaims memory of objects no longer reachable (from GC roots: stack refs, statics, etc.), so you don't manually free memory. The heap is generational: **Young gen** (Eden + Survivor, where most objects die young — minor GC) and **Old gen** (long-lived objects — major/full GC).
- **Collectors:**
  - **G1 GC** (default since Java 9) — region-based, balances throughput and pause times; good general default.
  - **Parallel GC** — throughput-focused (batch jobs), longer pauses.
  - **ZGC / Shenandoah** — **low-latency**, sub-millisecond pauses even on huge heaps (concurrent compaction); great for latency-sensitive services.
  - **Serial GC** — single-threaded, tiny heaps/containers.
- **Tuning basics:** set `-Xmx/-Xms`, pick a collector for your goal (throughput vs latency), monitor with GC logs. You don't call GC manually (`System.gc()` is a hint, discouraged).
- **One-liner:** "GC reclaims unreachable objects via a generational heap; G1 is the balanced default, ZGC/Shenandoah for ultra-low pause latency, Parallel for throughput."

### SQ12. Explain `equals()`/`hashCode()` contract and what breaks if you get it wrong.
- **Contract:** if `a.equals(b)` then `a.hashCode() == b.hashCode()`; equal objects must have equal hashcodes. Unequal objects *may* share a hashcode (collision). `equals` must be reflexive, symmetric, transitive, consistent.
- **What breaks:** if you override `equals` but not `hashCode`, hash-based collections (`HashMap`/`HashSet`) put the object in one bucket but look in another → you "lose" entries (put then can't get). If you make them inconsistent, you get duplicates in sets or missing map lookups.
- **Best practice:** override **both together**, use `Objects.equals`/`Objects.hash`, base them on the same immutable fields, and prefer **records** (auto-generate correct equals/hashCode).

### SQ13. `Comparable` vs `Comparator` and building complex sorts (modern Java).
- **`Comparable`** — natural ordering inside the class (`compareTo`), one order.
- **`Comparator`** — external, multiple orders, composable:
```java
list.sort(Comparator.comparing(Employee::getDept)
    .thenComparing(Employee::getSalary, Comparator.reverseOrder())
    .thenComparing(Employee::getName));
```
- Use `Integer.compare(a,b)` (not `a-b`, which can overflow), `nullsFirst`/`nullsLast` for nulls, and `reversed()` to flip.

### SQ14. Fail-fast vs fail-safe iterators; `ConcurrentModificationException`.
- **Fail-fast** (`ArrayList`, `HashMap`) — detect structural modification during iteration via a `modCount` check and throw **`ConcurrentModificationException`** immediately (even single-threaded, if you remove while iterating with a for-each). Fix: use the iterator's own `remove()`, or `removeIf`, or collect-then-remove.
- **Fail-safe** (`CopyOnWriteArrayList`, `ConcurrentHashMap`) — iterate over a snapshot/weakly-consistent view; no exception, but you may not see concurrent updates.
- **One-liner:** "Fail-fast iterators throw CME on concurrent structural change (via modCount); use `Iterator.remove`/`removeIf` or a concurrent/copy-on-write collection to avoid it."

### SQ15. What's new/important across Java 8→21 for a senior?
- **Java 8** — lambdas, streams, `Optional`, functional interfaces, default methods, new date/time API.
- **Java 9–10** — modules (JPMS), `var` local type inference, collection factory methods (`List.of`).
- **Java 11 (LTS)** — `HttpClient`, `String` methods, single-file run.
- **Java 14–16** — records, pattern matching for `instanceof`, switch expressions, text blocks.
- **Java 17 (LTS)** — sealed classes, finalized above features.
- **Java 21 (LTS)** — **virtual threads** (Loom), **pattern matching for switch**, **record patterns**, sequenced collections, structured concurrency (preview).
- **One-liner:** "8 brought functional Java (lambdas/streams); 17 brought records/sealed/pattern-matching for concise modeling; 21 brought virtual threads and pattern matching for switch — the biggest concurrency and expressiveness leaps."