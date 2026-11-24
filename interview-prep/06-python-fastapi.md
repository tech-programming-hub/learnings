# 06 — Python & FastAPI

> Anchor: You built FastAPI + Supabase async metrics pipeline (AgentPulse), Flask, and Python AI tooling. Speak from that.

> **How to read this file:** Every answer starts with a plain-English explanation and an analogy, then gives the technical detail, then (where useful) a small example. Read the analogy first — it makes the rest click.

---

## A. Python Core

### Q1. Python's key characteristics?

**Plain-English first:** Python is a language designed so humans can read and write code quickly. It trades a bit of raw speed for a lot of developer comfort.

Let's unpack each buzzword slowly:

- **Interpreted** — Think of two ways to cook: (1) write the full recipe, translate it into a language the oven understands, then run it (that's *compiled* languages like C/Java). (2) A chef reads your recipe one line at a time and cooks as they go (that's *interpreted* — Python). Python runs your code line-by-line through a program called "the interpreter." This makes it fast to write and test, but slower to run heavy math than a compiled language.

- **Dynamically typed** — You never write "this variable is an integer." You just say `x = 5`, and Python figures out at runtime that `x` is an integer. Later you could even do `x = "hello"` and Python is fine with it. The *type* travels with the *value*, not the variable name.

- **Strongly typed** — Even though you don't declare types, Python does not silently mix incompatible types. `"1" + 1` throws an error instead of guessing whether you meant `"11"` or `2`. (Contrast with JavaScript, which would guess.) "Strong" = it respects type boundaries; "dynamic" = it checks them at runtime, not before.

- **Garbage-collected** — You never manually free memory (unlike C where you `malloc`/`free`). Python automatically cleans up objects you're no longer using.

- **Multi-paradigm** — You can write in different styles: object-oriented (classes), functional (functions passed around, `map`/`filter`), or plain procedural (top-to-bottom scripts). You pick what fits the problem.

- **Huge ecosystem (PyPI)** — PyPI is Python's app store for libraries. Because almost everything already exists as a package (`pip install ...`), Python became the default for AI/ML, data science, scripting, and web APIs.

- **CPython is the reference implementation** — When people say "Python," they usually mean CPython, the standard interpreter written in the C language. Other versions exist (e.g., PyPy, which is faster because it uses JIT compilation).

**The one-line takeaway:** Python optimizes for **developer productivity and readability** over raw execution speed.

---

### Q2. What is the GIL (Global Interpreter Lock)?

**The one-sentence definition:** The **GIL is a mutex (a lock) inside the CPython interpreter that ensures only ONE thread executes Python bytecode at any given moment** — even on a machine with many CPU cores. A Python process can have many threads, but they take *turns* running Python code; they never run Python code *simultaneously*.

**The core mental model — the office with one pen:** Think of your Python **process** as an office:
- **CPU cores** = desks (say, 8 desks).
- **Threads** = workers (you can hire 8 workers).
- **The GIL** = a single pen.

**Rule of the office:** You can only write Python code if you're holding the pen. There's exactly one pen. So even with 8 workers at 8 desks, only the one holding the pen is actually writing Python at any instant. They pass the pen around very fast (every few milliseconds), which makes it *feel* concurrent — but it's not truly parallel.

**Why does the GIL exist? (the real reason)** CPython manages memory using **reference counting** (see Q11). Every object has a hidden counter of "how many things point to me." When that counter hits zero, the object is freed.
```python
a = [1, 2, 3]   # list's refcount = 1
b = a           # refcount = 2
del a           # refcount = 1
del b           # refcount = 0 → memory freed
```
Now imagine **two threads** incrementing/decrementing that counter at the *exact same time*. The operation `refcount += 1` is not atomic at the CPU level (it's read → add → write). Two threads interleaving could corrupt the count → objects freed too early (crash) or never freed (memory leak). **The GIL is the simplest, cheapest fix:** if only one thread ever runs Python at a time, refcount updates can never collide. That's the historical trade-off — it made CPython simple, fast for single-threaded code, and easy to integrate with C libraries.

**The ONE thing you must remember — impact depends on your workload type:**

- **CPU-bound work** (heavy math, image processing, tight loops, number crunching) → Threads **don't help**. All the work *is* running Python bytecode, which needs the pen, so adding threads just makes them fight over the one pen (no speedup, sometimes slower from overhead). The fixes:
  - Use **`multiprocessing`** — start separate *processes*. Each process has its OWN interpreter and its OWN GIL (its own pen), so they genuinely run in parallel across cores. Cost: data must be serialized/copied between processes.
  - Or use **native libraries** (NumPy, Pandas, Polars, PyTorch) that do the heavy work in C/C++ code and **release the GIL** while working, so they use multiple cores under the hood.

- **I/O-bound work** (waiting on network calls, database queries, reading files, external APIs) → Threads and **asyncio work great**. Why? Because while a thread is *waiting* for a response, it isn't running Python code — so it **releases the pen**, and another thread can use it. This is exactly why FastAPI + `asyncio` scales so well for API workloads: mostly waiting on DB/HTTP, not computing.

| Workload | Best tool | Why |
|---|---|---|
| CPU-bound (compute) | `multiprocessing` / native libs | Bypass the GIL for true parallelism |
| I/O-bound (waiting) | `threading` / `asyncio` | GIL is released during waits |

**When exactly does a thread release the pen?**
1. During **blocking I/O** (socket, file, DB call) — the big one.
2. Periodically on a timer (roughly every 5ms by default — `sys.setswitchinterval()`), so no single CPU-bound thread hogs the interpreter forever.
3. Inside C extensions that explicitly call `Py_BEGIN_ALLOW_THREADS` (that's how NumPy releases it).

**A quick demonstration you can describe:**
```python
import time, threading

def count(n):
    while n > 0:
        n -= 1

# Single-threaded: 2 x work
start = time.time()
count(50_000_000); count(50_000_000)
print("Sequential:", time.time() - start)

# Two threads: SAME work split across 2 threads
start = time.time()
t1 = threading.Thread(target=count, args=(50_000_000,))
t2 = threading.Thread(target=count, args=(50_000_000,))
t1.start(); t2.start(); t1.join(); t2.join()
print("Threaded:", time.time() - start)
```
**Result:** the threaded version is **NOT faster** (often slightly slower). That's the GIL for CPU-bound work. Swap `threading` for `multiprocessing` and it *does* speed up.

**Is the GIL going away? (bonus — shows you're current)** Yes — **PEP 703** introduces an optional **"free-threaded" (no-GIL) build** of CPython, experimental in **Python 3.13** and maturing in 3.14+. It removes the GIL by making reference counting thread-safe in other ways. It's opt-in today because it can slow single-threaded code, but it's the future direction. Also note: **only CPython has a GIL** — Jython (JVM) and IronPython (.NET) don't; PyPy does.

**Interview gold (20-second answer):** "The GIL is a lock in CPython that lets only one thread run Python bytecode at a time. It exists to make reference-counting memory management thread-safe. The practical consequence: threads don't speed up CPU-bound work — for that I use `multiprocessing` or native libraries like NumPy that release the GIL. But for I/O-bound work the GIL is released during waits, so `threading` and `asyncio` scale well — which is why it's a non-issue for a FastAPI service that's mostly waiting on databases and downstream APIs. And Python 3.13+ now ships an experimental free-threaded build that removes it." This connects to AgentPulse: an async FastAPI metrics pipeline is I/O-bound (DB writes, network), so `asyncio` is the right model and the GIL never becomes a bottleneck.

---

### Q3. `list` vs `tuple` vs `set` vs `dict`?

These are Python's four main "containers" for holding multiple values. Each is good at a different job.

- **`list`** — `[1, 2, 3]`
  - **Ordered** (keeps the order you put things in) and **mutable** (you can add, remove, change items).
  - **Analogy:** a shopping list you keep editing.
  - Use when order matters and the collection changes.

- **`tuple`** — `(1, 2, 3)`
  - **Ordered** but **immutable** (once created, you can't change it).
  - Because it can't change, it's **hashable** — meaning it can be used as a dictionary key or put inside a set. (More on hashable in Q4.)
  - **Analogy:** a printed receipt — fixed, can't be edited.
  - Use for a fixed group of values, like GPS coordinates `(lat, lng)`.

- **`set`** — `{1, 2, 3}`
  - **Unordered** collection of **unique** items (no duplicates allowed).
  - Super fast at answering "is X in here?" and at operations like union/intersection.
  - **Analogy:** a bag of unique stickers — you can't have two identical ones, and they're not in any particular order.
  - Use for de-duplication and fast membership checks.

- **`dict`** — `{"name": "Anup", "age": 30}`
  - A **key → value** lookup table. Finding a value by its key is **O(1)** on average (instant, regardless of size).
  - Since Python 3.7 it **remembers insertion order**.
  - **Analogy:** a labeled filing cabinet — you go straight to the drawer labeled "age."
  - The workhorse for structured / JSON-like data.

**Memory hook:** list = editable line, tuple = frozen record, set = bag of unique things, dict = labeled lookup table.

---

### Q4. Mutable vs immutable types?

**Plain-English first:** "Mutable" = can be changed after you create it. "Immutable" = once created, it can never change; any "change" actually makes a brand-new object.

- **Immutable:** `int`, `float`, `str`, `tuple`, `frozenset`, `bytes`.
- **Mutable:** `list`, `dict`, `set`, `bytearray`, and most custom objects you write.

**Example that surprises beginners:**
```python
s = "hello"
s.upper()      # returns "HELLO" — a NEW string
print(s)       # still "hello" — the original never changed
```
Strings are immutable, so `.upper()` can't modify `s`; it hands you a new string.

**Why does this matter?**
1. **Immutable objects are hashable** → they can be dict keys and set members. Mutable ones generally can't (because their "identity" could change).
2. **Mutable objects can cause shared-state bugs.** If you pass a list into a function and the function changes it, the caller's list changes too — because they're the *same* object in memory.

**The most famous trap — mutable default argument:**
```python
def add_item(item, bucket=[]):   # ⚠️ BUG
    bucket.append(item)
    return bucket

add_item("a")   # ['a']
add_item("b")   # ['a', 'b']  ← surprise! The list was reused
```
The default list `[]` is created **once** when the function is defined, then reused on every call. Fix it by defaulting to `None`:
```python
def add_item(item, bucket=None):
    if bucket is None:
        bucket = []
    bucket.append(item)
    return bucket
```

---

### Q5. `*args` and `**kwargs`?

**Plain-English first:** These let a function accept *any number* of arguments when you don't know in advance how many will be passed.

- **`*args`** collects extra **positional** arguments into a **tuple**.
- **`**kwargs`** collects extra **keyword** arguments (name=value) into a **dict**.

**Example:**
```python
def demo(*args, **kwargs):
    print(args)     # a tuple of positional args
    print(kwargs)   # a dict of keyword args

demo(1, 2, 3, name="Anup", age=30)
# args   = (1, 2, 3)
# kwargs = {'name': 'Anup', 'age': 30}
```

**Where you'll actually use it:** decorators and wrapper functions. A wrapper doesn't know what arguments the real function needs, so it captures *everything* with `*args, **kwargs` and forwards it:
```python
def wrapper(*args, **kwargs):
    return real_function(*args, **kwargs)   # pass everything through
```
At the call site, `*` and `**` also **unpack** a list/dict back into arguments:
```python
nums = [1, 2, 3]
print(*nums)   # same as print(1, 2, 3)
```

---

### Q6. List comprehension vs generator?

Both create a series of values, but the difference is **when** they do the work and **how much memory** they use.

- **List comprehension** — `[x*2 for x in xs]`
  - **Eager:** builds the ENTIRE list in memory right away.
  - Good: fast to reuse and index (`result[5]`).
  - Bad: if `xs` has 100 million items, you now hold 100 million results in RAM.

- **Generator expression** — `(x*2 for x in xs)` (note the round brackets)
  - **Lazy:** computes ONE value at a time, only when asked. Holds just the current item in memory.
  - **Analogy:** a list comprehension is like cooking all 1000 meals upfront and stacking them; a generator is a chef who cooks each meal only when a customer orders it.
  - Perfect for huge or streaming data (a giant file, a database cursor).
  - Trade-off: you can only loop through it **once**, and you can't index into it.

```python
# Eager — 1 million ints in memory at once
squares = [x*x for x in range(1_000_000)]

# Lazy — memory stays tiny, one at a time
squares_gen = (x*x for x in range(1_000_000))
```

**Rule of thumb:** big dataset, or you only need to iterate once → use a generator.

---

### Q7. What are decorators?

**Plain-English first:** A decorator is a function that *wraps* another function to add extra behavior — like logging, timing, caching, or auth — **without changing the original function's code.**

**Analogy:** Think of gift-wrapping. The gift (your function) stays exactly the same, but you add a wrapper (extra behavior) around it. From the outside, people interact with the wrapped version.

**The syntax:** you put `@decorator` above a function. Under the hood, this:
```python
@timed
def my_func():
    ...
```
is just shorthand for:
```python
my_func = timed(my_func)
```
So `timed` receives your function, and returns a NEW function that runs some extra code plus the original.

**Full example — a timer decorator:**
```python
import functools, time

def timed(fn):
    @functools.wraps(fn)          # keeps original name/docstring
    def wrapper(*args, **kwargs):
        start = time.time()
        result = fn(*args, **kwargs)   # call the real function
        print(f"{fn.__name__} took {time.time() - start:.3f}s")
        return result
    return wrapper

@timed
def slow_add(a, b):
    time.sleep(1)
    return a + b

slow_add(2, 3)   # prints "slow_add took 1.001s", returns 5
```

**Why it matters:** decorators cleanly handle "cross-cutting concerns" (things needed by many functions). FastAPI/Flask use them to register routes: `@app.get("/users")`.

**Tip:** always add `@functools.wraps(fn)` inside your wrapper so the wrapped function keeps its real name and docstring (otherwise debugging gets confusing).

---

### Q8. What are context managers (`with`)?

**Plain-English first:** A context manager guarantees cleanup happens — even if an error occurs. It handles "set up a resource, then always tear it down."

**Analogy:** It's like a self-closing door. You walk through (`with` block), do your thing, and the door *always* closes behind you — even if you trip and fall (an exception). You can't forget to close it.

**The classic example:**
```python
with open("data.txt") as file:
    contents = file.read()
# file is AUTOMATICALLY closed here — even if read() crashed
```

**How it works under the hood:** the object has two special methods:
- `__enter__` — runs when you enter the block (acquire the resource).
- `__exit__` — runs when you leave the block (release it), whether normally or via an exception.

**When to use it:** anything that must be reliably released — **files, database sessions, network connections, locks.**

**Building your own** (the easy way, with a generator):
```python
from contextlib import contextmanager

@contextmanager
def db_session():
    session = open_session()      # setup (before yield)
    try:
        yield session            # hand it to the 'with' block
    finally:
        session.close()          # teardown (after yield), always runs
```

**The benefit:** no leaked file handles or forgotten locks, and cleaner than writing `try/finally` everywhere.

---

### Q9. `@staticmethod` vs `@classmethod` vs instance method?

The difference is simply **what each method automatically receives as its first argument.**

- **Instance method** — receives **`self`** (the specific object).
  - Use it to read or change that object's data. This is the default, most common kind.
  ```python
  class Dog:
      def bark(self):            # self = this particular dog
          return f"{self.name} says woof"
  ```

- **`@classmethod`** — receives **`cls`** (the class itself, not one object).
  - Great for **alternative constructors / factory methods** — different ways to build an object.
  ```python
  class User:
      @classmethod
      def from_json(cls, data):   # cls = the User class
          return cls(name=data["name"])   # builds a User
  ```

- **`@staticmethod`** — receives **nothing** automatically.
  - It's just a plain helper function that lives inside the class because it's logically related, but it doesn't touch the object or the class.
  ```python
  class Math:
      @staticmethod
      def add(a, b):
          return a + b
  ```

**Quick decision rule:**
- Need the object's data? → instance method (`self`)
- Need the class (e.g., to construct it)? → `@classmethod` (`cls`)
- Need neither? → `@staticmethod`

---

### Q10. Shallow vs deep copy?

**Plain-English first:** Both make a copy, but they differ in whether they also copy the *nested* things inside.

**Analogy:** Imagine copying a folder that contains shortcuts to files.
- **Shallow copy** = you copy the folder, but the shortcuts inside still point to the SAME original files. Edit a file through the shortcut, and the original folder sees the change too.
- **Deep copy** = you copy the folder AND make real copies of every file inside. Fully independent.

- **Shallow copy** (`copy.copy(x)`) — new outer container, but **inner objects are shared** (same references).
- **Deep copy** (`copy.deepcopy(x)`) — **recursively copies everything**, giving a fully independent clone.

**Example showing the trap:**
```python
import copy

original = [[1, 2], [3, 4]]

shallow = copy.copy(original)
shallow[0].append(99)
print(original)   # [[1, 2, 99], [3, 4]]  ← original changed too!

deep = copy.deepcopy(original)
deep[0].append(77)
print(original)   # unchanged — deep copy is independent
```

**When it matters:** nested mutable structures (lists of lists, dicts of objects). Deep copy is safer but slower and uses more memory.

---

### Q11. How does Python manage memory?

CPython uses **two mechanisms working together.**

**1. Reference counting (the main one):**
Every object keeps a count of how many things point to it. When that count hits **zero**, the object is freed *immediately*.
```python
a = [1, 2, 3]   # list has 1 reference (a)
b = a           # now 2 references (a and b)
del a           # back to 1
del b           # 0 references → list is freed right away
```
This is prompt and predictable, but it has one blind spot...

**2. Generational garbage collector (for cycles):**
Reference counting can't handle **reference cycles** — objects that point to each other:
```python
a = {}
b = {}
a["b"] = b      # a points to b
b["a"] = a      # b points to a
del a, b        # nothing outside points to them, but they still
                # point to EACH OTHER, so refcount never hits 0
```
These would leak forever. So Python adds a garbage collector that periodically finds and cleans up such unreachable cycles.

**"Generational"** means objects are grouped by age. New objects are checked often (most objects die young), older survivors less often — a performance optimization.

**Tools you can use:**
- `gc.collect()` — manually force a cycle cleanup.
- `weakref` — a "weak" reference that doesn't keep an object alive (useful for caches, so the cache doesn't prevent cleanup).

**Takeaway:** memory is mostly automatic; the edge cases to know are reference cycles and `__del__` finalizers.

---

### Q12. Type hints & their value?

**Plain-English first:** Type hints let you *write down* what type you expect, like `def f(x: int) -> str:` ("x should be an int, and this returns a str").

**Important:** Python **ignores these at runtime** — they don't force anything. You can pass a string where an int is hinted and Python won't stop you.

**So why bother?** The value comes from **tooling and readability:**
- **Static checkers (mypy, pyright)** read the hints and catch type bugs *before you run the code* — like a spellchecker for types.
- **IDEs** use them for better autocomplete and safer refactoring.
- They act as **living documentation** — the code tells you what it expects.

**The one big exception:** **FastAPI and Pydantic deliberately DO read type hints at runtime** to automatically validate requests and serialize responses. That's why type hints are central to FastAPI, not just a nice-to-have.
```python
@app.post("/users")
def create(user: User):   # FastAPI reads 'User' to validate the request body
    ...
```

---

## B. Async Python

### Q13. Explain `asyncio` — async/await.

**Plain-English first:** `asyncio` lets ONE thread juggle thousands of tasks that spend most of their time *waiting* (for network, database, files). It doesn't make things run in parallel on multiple cores — it makes waiting efficient.

**Analogy (the waiter):** One waiter (one thread) serves many tables. When a table orders food, the waiter doesn't stand frozen while the kitchen cooks — they go take other tables' orders. `await` is the waiter saying "this will take a while, I'll go do useful work meanwhile."

**The key word is "cooperative":** tasks *voluntarily* give up control at `await` points. This is different from OS threads, which can be interrupted at any moment. Here, a task keeps running until it hits an `await`.

**How the pieces fit:**
- **`async def`** defines a **coroutine** (a pausable function).
- **`await`** is used on something slow (a network call). At that point, the coroutine *pauses and hands control back* to the event loop.
- The **event loop** is the manager that runs whichever coroutines are ready while others wait.
- When the awaited operation finishes, the loop resumes that coroutine.

```python
import asyncio

async def fetch_user(id):
    await asyncio.sleep(1)      # pretend this is a slow DB call
    return f"user-{id}"

async def main():
    # These 3 run CONCURRENTLY — total ~1 second, not 3
    results = await asyncio.gather(
        fetch_user(1), fetch_user(2), fetch_user(3)
    )
    print(results)

asyncio.run(main())
```

**The crucial limitation:** because it's a single thread, asyncio gives you **concurrency, not CPU parallelism**. If one coroutine does heavy math (or calls a blocking library), it **freezes the entire loop** — the waiter is stuck at one table and nobody else gets served. So asyncio is for **I/O-bound** work, not CPU-heavy work.

---

### Q14. Concurrency options in Python — when to use what?

Three models. The right choice comes back to **I/O-bound vs CPU-bound** (and the GIL from Q2).

- **`asyncio`** — best for **I/O-bound, high-concurrency** work (thousands of simultaneous network/DB calls) in a **single thread**.
  - Very memory-efficient.
  - Catch: you need async-compatible libraries all the way through (e.g., `httpx` instead of `requests`, `asyncpg` instead of a sync DB driver).

- **`threading`** — also for **I/O-bound** work, and easier to add to existing blocking code.
  - GIL-bound → gives NO CPU parallelism.
  - Uses more memory per thread than a coroutine.
  - Good for moderate concurrency when you're stuck with blocking libraries.

- **`multiprocessing`** — the answer for **CPU-bound** work.
  - Spawns **separate processes**, each with its own interpreter and GIL → **true parallelism** across cores.
  - Cost: heavier memory use and overhead to pass data between processes.

**Summary cheat-sheet:**
- I/O-bound + huge scale → **asyncio**
- I/O-bound + blocking libraries → **threading**
- CPU-bound → **multiprocessing**

---

### Q15. `asyncio.gather` vs `asyncio.create_task`?

Both run coroutines concurrently, but for different intents.

- **`asyncio.gather(*coros)`** — "Run all of these together, and give me ALL the results when they're done."
  - Waits for every coroutine and returns results as a list (in order).
  - Add `return_exceptions=True` to collect errors instead of crashing the whole batch on the first failure.
  ```python
  results = await asyncio.gather(fetch(1), fetch(2), fetch(3))
  # waits for all 3, returns [r1, r2, r3]
  ```

- **`asyncio.create_task(coro)`** — "Start this running in the background NOW; I'll deal with it later (or never)."
  - Returns a `Task` handle you can await whenever you want.
  - Good for fire-and-forget, or letting work proceed alongside other code.
  ```python
  task = asyncio.create_task(send_email())   # starts immediately
  # ... do other work ...
  await task                                  # wait for it when ready
  ```

**One-liner:** `gather` = "run these together, give me all results now"; `create_task` = "start this in the background."

**Modern note:** In Python 3.11+, **`asyncio.TaskGroup`** is the cleaner, safer way to manage a group of tasks (it automatically cancels siblings if one fails).

---

## C. FastAPI

### Q16. What is FastAPI? Why choose it?

**Plain-English first:** FastAPI is a modern Python framework for building web APIs quickly. Its superpower: it turns your normal **type hints** into automatic validation, documentation, and serialization — so you write less boilerplate.

**Built on two foundations:**
- **Starlette** — provides the async web machinery (the engine).
- **Pydantic** — provides data validation from type hints (the quality control).

**Why teams pick it — the main benefits:**
- **Async-first** — built on ASGI (see Q21), so it handles thousands of concurrent I/O requests with high throughput.
- **Automatic validation** — type hints + Pydantic parse and check every request. Bad input? It auto-returns a clear **422 error** — you write zero validation code.
- **Auto docs** — it generates interactive API docs (**Swagger UI** at `/docs`, **ReDoc** at `/redoc`) for free.
- **Dependency injection** — a clean `Depends()` system for reusable logic (DB sessions, auth, config).
- **Speed** — performance comparable to Node.js/Go, which is unusual for Python.

**When to choose it:** fast, well-documented, strongly-validated async APIs and microservices with minimal boilerplate — which is exactly why it's the go-to for AI/ML-facing services.

---

### Q17. Basic FastAPI endpoint with validation.

```python
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

app = FastAPI()

# The request body shape — FastAPI validates against this automatically
class OrderIn(BaseModel):
    item: str = Field(min_length=1)   # must be a non-empty string
    qty: int = Field(gt=0)            # must be greater than 0

@app.post("/orders", status_code=201)   # 201 = "Created"
async def create_order(order: OrderIn):
    # If we got here, 'order' is already validated (valid item + qty > 0)
    if not in_stock(order.item):
        raise HTTPException(status_code=409, detail="Out of stock")
    return {"id": save(order), **order.model_dump()}
```

**What happens step by step:**
1. A client POSTs JSON like `{"item": "book", "qty": 2}`.
2. FastAPI reads the `OrderIn` type hint and validates the JSON against it.
3. If invalid (e.g., `qty: 0`), the client automatically gets a 422 error — your function never even runs.
4. If valid, your function runs with a clean, typed `order` object.

---

### Q18. What is Pydantic and its role?

**Plain-English first:** Pydantic is the "bouncer at the door" for your data. It takes messy external input (JSON), checks it against rules you defined with type hints, cleans it up, and only lets valid data through.

**What it does across the data lifecycle:**
- **Parses** incoming JSON into Python objects.
- **Validates** it against your declared types and constraints.
- **Coerces** sensible types (the string `"5"` becomes the int `5`).
- **Serializes** models back out to JSON when responding.
- On failure, raises **clear, structured errors** telling you exactly which field was wrong and why.

**The key pieces:**
- **`BaseModel`** — you subclass this to define a schema (the shape of your data).
- **`Field`** — adds constraints/metadata (`gt=0`, `min_length=1`).
- **Validators** — custom rules for complex checks.
- **`BaseSettings`** — loads configuration from environment variables (12-factor config).

```python
from pydantic import BaseModel, Field

class Product(BaseModel):
    name: str = Field(min_length=1)
    price: float = Field(gt=0)

Product(name="Book", price="9.99")   # "9.99" is coerced to float 9.99
Product(name="", price=-1)           # raises a clear validation error
```

**Performance note:** **Pydantic v2** rewrote its core in **Rust** (`pydantic-core`), making it dramatically faster than v1.

**Big-picture value:** it pushes validation to the **edge** of your app declaratively, so the rest of your code can trust its data is clean.

---

### Q19. FastAPI dependency injection?

**Plain-English first:** Dependency injection (DI) means: instead of each endpoint creating the things it needs (a DB session, the logged-in user), it just *declares* what it needs, and FastAPI *provides* it automatically.

**Analogy:** At a restaurant you don't go into the kitchen to grab utensils — you sit down and they're *provided* to you. Your endpoint just says "I need a DB session," and FastAPI delivers one.

**How it works:** you write a function (the "dependency") and reference it with `Depends()` in your endpoint's parameters. FastAPI calls that function, resolves anything *it* needs (dependencies can be **nested**: `auth → current_user → db`), and injects the result.

```python
def get_db():
    db = SessionLocal()
    try:
        yield db          # this value is injected into the endpoint
    finally:
        db.close()        # cleanup runs AFTER the response is sent

@app.get("/users/{id}")
async def get_user(id: int, db=Depends(get_db)):
    # 'db' was provided automatically; we didn't create it here
    return db.query(User).get(id)
```

**Powerful features:**
- **`yield` dependencies** give **per-request setup/teardown** (open before, clean up after).
- Results are **cached within a single request** (same dependency isn't recomputed).
- You can **override dependencies in tests** with `app.dependency_overrides` to inject fakes/mocks — huge for testing.

It's the same "Inversion of Control" idea as Spring's DI, applied cleanly to route handlers.

---

### Q20. How do you secure a FastAPI app?

Security in FastAPI is **layered**, and most of it plugs into the **dependency injection** system so it applies consistently.

**1. Authentication ("who are you?")** — commonly OAuth2/JWT:
- Use `OAuth2PasswordBearer` to pull the bearer token out of the `Authorization` header.
- Write a **dependency that validates the JWT** (checks signature, expiry, issuer) and returns the current user.
- Any endpoint that declares this dependency is automatically protected and receives the authenticated user.

**2. Authorization ("what are you allowed to do?")**:
- Use `Security()` with **scopes**, or do role checks inside a dependency.
- This enforces permission for a specific action, not just "you're logged in."

**3. Transport & browser security**:
- Always serve over **HTTPS** (usually terminated at the reverse proxy / ingress).
- Configure **CORS middleware** to control which front-end origins may call your API.

**4. Abuse protection**:
- **Rate limiting** (e.g., `slowapi`) to throttle clients and defend against brute-force / DoS attacks.

**The clean one-liner for an interview:** "I validate the token in a **dependency**, inject the current user into the endpoint, and enforce scopes/roles there — plus HTTPS, CORS, and rate limiting at the edge."

---

### Q21. WSGI vs ASGI?

**Plain-English first:** Both are "contracts" (standards) that define how a web server talks to your Python app. WSGI is the old synchronous one; ASGI is the modern asynchronous one.

- **WSGI (Web Server Gateway Interface)** — the older, **synchronous** standard (classic Flask, Django).
  - Each request is handled by a worker that **blocks** until it's finished.
  - This limits concurrency for waiting-heavy (I/O) workloads and can't natively handle long-lived connections like WebSockets.
  - **Analogy:** a phone line where the operator handles one call fully before picking up the next.

- **ASGI (Asynchronous Server Gateway Interface)** — the modern, **asynchronous** successor (FastAPI, Starlette).
  - Because it's async, it handles **many concurrent connections** efficiently.
  - Supports things WSGI can't: **WebSockets, long-polling, HTTP/2.**
  - **Analogy:** an operator who can juggle many calls, switching whenever one is on hold.

**How you run it in production:** an ASGI app runs on **Uvicorn** (an ASGI server), often managed by **Gunicorn** using Uvicorn worker processes for multi-process scaling.

**One-liner:** WSGI = sync / request-per-worker; ASGI = async / high-concurrency + real-time protocols.

---

### Q22. FastAPI vs Flask vs Django?

All three are Python web frameworks, but they sit at different points on two spectrums: "minimal ↔ batteries-included" and "sync ↔ async."

- **FastAPI** — **async**, automatic validation and docs from type hints.
  - Best for: **APIs and microservices**, especially high-concurrency and AI/ML-facing services. Modern and fast.

- **Flask** — a **minimal, synchronous micro-framework**.
  - Gives you routing and little else; you pick your own libraries.
  - Best for: flexibility, simplicity, small apps and prototypes where you want full control.

- **Django** — a **batteries-included** framework.
  - Ships with an ORM, admin panel, auth, migrations, templating, and more.
  - Best for: full, monolithic web applications (especially server-rendered) where conventions and productivity out of the box matter.

**Rule of thumb:**
- API/microservice + async → **FastAPI**
- Small/flexible → **Flask**
- Full-featured web app fast → **Django**

---

### Q23. How do you do background tasks in FastAPI?

**Plain-English first:** "Background task" = work you want to do *after* responding to the user, so they don't wait for it. The right tool depends on how heavy the work is.

**1. Light, fire-and-forget work → FastAPI's built-in `BackgroundTasks`:**
For things like sending a confirmation email or writing an audit log. FastAPI runs the task *after* returning the response, in the same process.
```python
from fastapi import BackgroundTasks

@app.post("/signup")
async def signup(email: str, tasks: BackgroundTasks):
    user = create_user(email)
    tasks.add_task(send_welcome_email, email)   # runs after response
    return {"status": "ok"}
```
**Caution:** it's in-process, so if the app restarts, the task is lost. No retries, no durability.

**2. Heavy / long-running / distributed work → a dedicated task queue:**
For video processing, batch ETL, or anything needing retries, scheduling, or to survive a restart. Use **Celery, RQ, or ARQ** (ARQ is asyncio-native), backed by a broker like Redis or a message queue.

**The key judgment call:** `BackgroundTasks` is fine for quick, unimportant work; anything important or heavy belongs in a proper external worker with durability and retries.

---

### Q24. How do you handle DB access?

**Plain-English first:** The idiomatic approach is an ORM (a library that maps database rows to Python objects) with a fresh database **session provided per request** via dependency injection.

**The typical stack:**
- **SQLAlchemy** — the most common ORM/toolkit. Use its **async** engine with **`asyncpg`** for Postgres to stay non-blocking on the event loop.
- Or **SQLModel** — SQLAlchemy + Pydantic combined (built by FastAPI's author).

**The pattern — session per request:**
```python
async def get_db():
    async with AsyncSessionLocal() as session:
        yield session      # one session per request, auto-closed after

@app.get("/items")
async def list_items(db=Depends(get_db)):
    return await db.execute(select(Item))
```

**Supporting concepts:**
- **Connection pooling** — reuse a pool of open connections instead of opening a new one per request (much faster).
- **Alembic migrations** — version-controlled, repeatable schema changes (like Git for your DB structure).

**The important async caveat:** in `async def` endpoints, use an **async driver end-to-end**. A synchronous DB call inside an async endpoint would **block the event loop** and freeze all other requests.

---

### Q25. Middleware & lifespan events?

These are two different hooks: one runs per-request, the other runs once per app lifetime.

**Middleware — wraps every request/response:**
Lets you run logic *before* the request reaches your endpoint and *after* the response leaves.
- **Analogy:** airport security — every passenger (request) passes through it on the way in.
- Classic uses: **logging, metrics/timing, CORS, correlation IDs, auth pre-checks, compression.**
- The right place for concerns that apply to ALL routes.

```python
@app.middleware("http")
async def add_timing(request, call_next):
    start = time.time()
    response = await call_next(request)          # run the endpoint
    response.headers["X-Time"] = str(time.time() - start)
    return response
```

**Lifespan events — run once at startup and once at shutdown:**
The modern `lifespan` context manager replaces the older `@app.on_event("startup"/"shutdown")`.
- Use it to **initialize and cleanly close shared resources**: DB connection pools, Kafka producers, HTTP clients, OpenTelemetry exporters.
- Setup happens before `yield`, teardown after.

```python
from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.pool = await create_pool()    # startup
    yield
    await app.state.pool.close()            # shutdown

app = FastAPI(lifespan=lifespan)
```

**Summary:** middleware = per-request cross-cutting logic; lifespan = per-application startup/shutdown resource management.

---

## D. Testing & Quality

### Q26. How do you test Python/FastAPI?

**The standard stack:**
- **`pytest`** — the test runner (finds and runs your tests, gives clear failure output).
- **An HTTP client** to hit your endpoints:
  - FastAPI's **`TestClient`** (synchronous, simple), or
  - **`httpx.AsyncClient`** for testing async code properly.
- **Fixtures** — reusable setup (a test DB, a client, sample data).
- **`pytest-asyncio`** — lets you write `async def` test functions.
- **Mocking** (`unittest.mock`) — replace external dependencies with fakes so tests are isolated and fast.

**FastAPI's special advantage:** `app.dependency_overrides` lets you cleanly swap real dependencies (DB, auth) for fakes during tests.

**What to actually test** (aim for the behaviors that matter):
- Happy paths (successful requests).
- **Validation errors (422)**.
- **Auth failures (401/403)**.
- Edge and error cases.

Track **coverage** to find untested gaps, and use **Testcontainers** to spin up a real database for high-fidelity DB tests.

```python
from fastapi.testclient import TestClient

client = TestClient(app)

def test_create_order():
    r = client.post("/orders", json={"item": "book", "qty": 2})
    assert r.status_code == 201

def test_invalid_order_returns_422():
    r = client.post("/orders", json={"item": "book", "qty": 0})
    assert r.status_code == 422
```

---

### Q27. Python best-practice tooling?

A healthy Python project automates quality so it isn't left to memory:

- **Formatting & linting:**
  - **`black`** — an opinionated auto-formatter (ends style debates).
  - **`ruff`** — an extremely fast linter/formatter that catches common mistakes.

- **Type checking:**
  - **`mypy`** (or `pyright`) — statically verifies type hints and catches bugs before runtime.

- **Dependency & environment management:**
  - **`poetry`** or **`uv`** with lock files → reproducible installs, always inside a **virtualenv** per project.

- **Automation:**
  - **pre-commit hooks** — run format/lint/type checks automatically on every commit, so bad code never lands.

- **Runtime hygiene:**
  - **Structured logging** (JSON logs for observability).
  - **12-factor config** via Pydantic's `BaseSettings` (config from environment variables; secrets never committed).

**The theme:** make correctness and consistency **automatic and enforced**, not manual.

---

## ⚡ Rapid-Fire (with quick explanations)

- **`is` vs `==`** — `is` checks *identity* (same object in memory); `==` checks *equality* (same value). Use `is` only for `None`.
- **`__init__` vs `__new__`** — `__new__` *allocates/creates* the object; `__init__` *initializes* it (sets attributes). You almost always only write `__init__`.
- **f-strings** — the modern way to format strings: `f"Hello {name}"`. The `f"{x=}"` trick prints `x=<value>` (great for debugging).
- **`enumerate`, `zip`, `map`, `filter`, comprehensions** — idiomatic iteration tools. `enumerate` gives index+item; `zip` pairs up lists.
- **`dataclass`** — auto-generates boilerplate (`__init__`, `__repr__`, etc.) for classes that mostly hold data — like Java records.
- **EAFP** — "Easier to Ask Forgiveness than Permission" — the Pythonic style of just *trying* something and catching the exception, rather than checking first.
- **PEP 8** — the official Python style guide (naming, spacing, layout).
- **virtualenv per project; pin deps; never commit secrets** — foundational hygiene rules.

---
---

# PART 2 — Advanced & Tough Questions (with detailed explanations + examples)

## T1. The GIL in depth — how do you actually achieve parallelism in Python?

**Recap:** the GIL means only one thread runs Python bytecode at a time, so pure-Python CPU work doesn't parallelize across threads.

**How to actually get parallelism:**
- **CPU-bound:** use **`multiprocessing`** or **`ProcessPoolExecutor`** — separate processes, each with its own interpreter and GIL, so they truly run in parallel. Or push heavy work into C/Rust extensions (NumPy, Polars) that **release the GIL** while computing.
- **I/O-bound:** **`asyncio`** or **threads** work fine, because the GIL is released while waiting on I/O syscalls.
- **Future:** Python 3.13 introduces an experimental **free-threaded (no-GIL) build**.

**Great interview answer:** "I pick the concurrency model by workload — asyncio for thousands of concurrent HTTP calls (like my AgentPulse proxy), multiprocessing for CPU-bound batch work."

---

## T2. Common closure/late-binding gotcha in loops.

```python
funcs = [lambda: i for i in range(3)]
print([f() for f in funcs])          # [2, 2, 2]  ← NOT [0, 1, 2]!
```

**Why?** Each lambda captures the *variable* `i`, not its value at the moment it was created. By the time you *call* the functions, the loop has finished and `i` is `2`. So all three see `2`.

**The fix — bind the value per iteration using a default argument:**
```python
funcs = [lambda i=i: i for i in range(3)]
print([f() for f in funcs])          # [0, 1, 2]
```
Here `i=i` captures the *current value* at creation time (defaults are evaluated immediately).

**One-liner:** Closures capture the **variable**, not its value at creation time.

---

## T3. Mutable default argument trap (very common interview catch).

```python
def add(item, bucket=[]):     # BUG: default list created ONCE, shared across calls
    bucket.append(item)
    return bucket

add(1)   # [1]
add(2)   # [1, 2]  ← surprise! Same list reused
```

**Why?** The default `[]` is created a single time when the function is *defined*, not each time it's called. Every call without a `bucket` argument reuses that same list.

**The fix:**
```python
def add(item, bucket=None):
    if bucket is None:
        bucket = []          # fresh list each call
    bucket.append(item)
    return bucket
```

---

## T4. `@lru_cache` / memoization and its pitfalls.

**What it does:** `@lru_cache` remembers a function's results so repeated calls with the same arguments return instantly instead of recomputing. ("Memoization.")

```python
from functools import lru_cache

@lru_cache(maxsize=1024)
def fib(n):
    return n if n < 2 else fib(n-1) + fib(n-2)
```
Without the cache, `fib` recomputes the same values exponentially. With it, each `n` is computed once.

**Pitfalls to mention:**
- Only works with **hashable** arguments (no lists/dicts as args).
- Can **leak memory** if `maxsize=None` (unbounded).
- Caches across calls — **bad if the function isn't pure** (e.g., depends on time, DB, randomness) or the underlying data changes.
- On **instance methods**, `self` becomes part of the cache key → can keep objects alive in memory longer than expected.

---

## T5. `asyncio` — the #1 mistake: blocking the event loop.

**The core rule:** in an async app, a single blocking call (`time.sleep`, heavy CPU, a sync DB driver, `requests`) **freezes ALL coroutines** on that loop. Remember the waiter analogy — one blocking call is the waiter standing frozen at a table while everyone else waits.

```python
# ❌ BAD inside an async endpoint:
time.sleep(2)                  # blocks the whole event loop
result = requests.get(url)     # sync HTTP blocks everything

# ✅ GOOD — use async equivalents:
await asyncio.sleep(2)
async with httpx.AsyncClient() as c:
    result = await c.get(url)

# ✅ If you MUST run blocking/CPU work, offload it:
await asyncio.to_thread(cpu_bound_fn, data)   # run in a thread
# or run_in_executor(ProcessPoolExecutor(), ...) for CPU-bound work
```

**Rule:** inside `async def`, everything must be non-blocking or offloaded.

---

## T6. Run N calls concurrently and handle partial failures.

```python
async def fetch_all(urls):
    async with httpx.AsyncClient() as c:
        tasks = [c.get(u) for u in urls]
        # return_exceptions=True → don't crash the whole batch if one fails
        results = await asyncio.gather(*tasks, return_exceptions=True)
    # keep only the successful responses
    return [r for r in results if not isinstance(r, Exception)]
```

**Key point:** by default, `gather` *fails fast* — one exception cancels the batch. With `return_exceptions=True`, failures are returned as objects in the results list instead, so you can handle partial success.

**Modern alternative:** `asyncio.TaskGroup` (3.11+) gives structured concurrency — it automatically cancels sibling tasks if one fails.

---

## T7. FastAPI: sync `def` vs `async def` endpoints — what really happens?

This trips people up, so know it precisely:

- **`async def` endpoint** — runs directly on the event loop. It **must be non-blocking** (use async libraries). If you block here, you freeze the whole server.

- **plain `def` endpoint** — FastAPI is smart: it runs it in a **threadpool** (a separate thread). So a blocking DB call in a `def` endpoint won't freeze the event loop — but the threadpool has a limited size, which caps concurrency.

**Rule of thumb:**
- Have async libraries (httpx, asyncpg)? → use `async def`.
- Stuck with a blocking library? → a plain `def` endpoint is *safer* than blocking inside `async def`.

---

## T8. Pydantic v2 — custom validation and why v2 is faster.

```python
from pydantic import BaseModel, field_validator, model_validator

class Order(BaseModel):
    qty: int
    price: float

    @field_validator("qty")          # validates ONE field
    @classmethod
    def positive(cls, v):
        if v <= 0:
            raise ValueError("qty must be > 0")
        return v

    @model_validator(mode="after")   # validates the WHOLE model after fields
    def check_total(self):
        if self.qty * self.price > 1_000_000:
            raise ValueError("too large")
        return self
```

- **`field_validator`** — custom rule for a single field.
- **`model_validator(mode="after")`** — rule that needs multiple fields together (runs after individual fields are validated).

**Why v2 is faster:** its core validation logic was rewritten in **Rust** (`pydantic-core`).

**API changes to know:** `model_dump()` and `model_validate()` replace v1's `dict()` and `parse_obj()`.

---

## T9. FastAPI dependency injection with lifecycle + `yield` (setup/teardown).

```python
async def get_db():
    session = AsyncSessionLocal()
    try:
        yield session          # injected into the endpoint
        await session.commit()  # commit if the endpoint succeeded
    except Exception:
        await session.rollback()  # roll back on any error
        raise
    finally:
        await session.close()  # teardown — always runs after the response
```

**What's happening:** the code *before* `yield` is setup, the value *at* `yield` is injected, and the code *after* `yield` runs as teardown once the response is sent. This gives clean per-request resource management.

**Bonus features:** dependencies can be **nested** (auth → current_user → db), are **cached per request**, and can be **overridden in tests** via `app.dependency_overrides`.

---

## T10. How do you handle app-wide resources (DB pool, Kafka producer, OTel)?

Use the **lifespan** context manager — resources created once at startup, closed once at shutdown (not per-request).

```python
from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.pool = await create_pool()   # startup — create once
    yield
    await app.state.pool.close()           # shutdown — clean up once

app = FastAPI(lifespan=lifespan)
```

This is the modern replacement for the older `@app.on_event("startup"/"shutdown")` decorators.

---

## T11. Production deployment — Uvicorn/Gunicorn workers & scaling.

**Typical command:**
```bash
gunicorn -k uvicorn.workers.UvicornWorker -w <2*cores+1> app:app
```

- **Gunicorn** manages multiple worker **processes**; each worker uses a **Uvicorn** ASGI worker with its own event loop.
- Multiple processes **sidestep the GIL** across workers → real parallelism at the process level.

**Production checklist to mention:**
- Put it behind **Nginx / an ingress**.
- Add **timeouts** and **`--max-requests`** to recycle workers periodically (mitigates memory leaks).
- Add **health checks** and **structured logging**.
- For CPU-bound endpoints, **offload to Celery / a queue** rather than blocking a worker.

---

## T12. Testing async FastAPI properly.

```python
import pytest, httpx

@pytest.mark.asyncio
async def test_create_order():
    async with httpx.AsyncClient(app=app, base_url="http://test") as ac:
        r = await ac.post("/orders", json={"item": "x", "qty": 2})
    assert r.status_code == 201
```

**Key tools:**
- **`pytest-asyncio`** to run async test functions.
- **`app.dependency_overrides`** to inject fakes (fake DB, fake auth).
- **Testcontainers** to spin up a real DB for high-fidelity tests.

**Always test:** validation errors (422), auth failures (401/403), and edge cases — not just the happy path.

---

## T13. Memory management + the cyclic GC.

CPython combines two things (see Q11 for the beginner version):
- **Reference counting** — frees an object the instant its reference count hits 0.
- **Generational cyclic collector** — handles reference cycles (e.g., `a.b = b; b.a = a`) that reference counting alone can't free.

**Gotchas to mention:**
- A `__del__` method on objects that are part of a cycle can complicate collection.
- Use **`weakref`** for caches / back-references so they don't keep objects alive unnecessarily.
- **`gc.collect()`** forces a cycle collection when you need it.

---

## T14. Tough rapid-fire

- **`__slots__`** — declaring `__slots__ = ("x", "y")` fixes the allowed attributes → less memory and faster attribute access (no per-instance `__dict__`). Trade-off: you can't add new attributes dynamically.
- **`@dataclass(frozen=True)`** — creates immutable, hashable value objects (can be used as dict keys / set members).
- **Generators for streaming** — process a huge file or DB cursor without loading it all into memory, using `yield`.
- **`is` vs `==`** — `is` is identity (same object); never use `is` to compare values, except `is None`.
- **GIL + async myth** — asyncio gives *concurrency* (efficient waiting), not CPU *parallelism*.
- **`asyncio.gather` vs `TaskGroup`** — `gather` returns results/exceptions; `TaskGroup` (3.11+) cancels siblings on failure (structured concurrency).
- **Type checking at runtime?** — type hints are ignored at runtime, except where tools like Pydantic/FastAPI explicitly read them.

---
---

# PART 3 — More Real Interview Questions (Easy Language, No Repeats)

## Q1. What does "Python is dynamically typed" mean?

You don't declare variable types — Python figures out the type at runtime, and a variable can even change type:
```python
x = 5        # x is an int
x = "hi"     # now x is a string — totally fine
```
Convenient and fast to write, but the downside is type errors only appear *when the code runs*, not before. That's why type hints + tools like mypy help catch bugs early.

---

## Q2. What is the difference between a list and a tuple, and when would you use each?

- **List** `[1, 2, 3]` — changeable (mutable). Use when the collection will grow, shrink, or be reordered.
- **Tuple** `(1, 2, 3)` — fixed (immutable), slightly faster, and can be used as a dictionary key. Use for fixed groups of values (like coordinates) or when you want to prevent accidental changes.

---

## Q3. What is a dictionary and why is it so commonly used?

A key-value store: `{"name": "Anup", "age": 30}`. Looking up a value by its key is very fast (O(1) on average). It's Python's workhorse for structured data, counting, grouping, caching, and representing JSON.

---

## Q4. What is list/dict comprehension? Give an example.

A compact way to build a list or dict in one line:
```python
squares  = [x*x for x in range(5)]           # [0, 1, 4, 9, 16]
even_map = {x: x % 2 == 0 for x in range(3)} # {0: True, 1: False, 2: True}
```
It's more readable and often faster than writing a manual `for` loop with `.append()`.

---

## Q5. What is the difference between `append()` and `extend()`?

- `list.append(x)` — adds `x` as a **single** element (even if `x` is itself a list).
- `list.extend([a, b])` — adds each item of the iterable individually.
```python
a = [1]; a.append([2, 3])   # [1, [2, 3]]   ← the list went in as one item
b = [1]; b.extend([2, 3])   # [1, 2, 3]     ← items added individually
```

---

## Q6. What is `if __name__ == "__main__":` for?

It means "only run this block when the file is executed *directly*, not when it's *imported* as a module."

**Why it exists:** when Python imports a file, it runs all top-level code. This guard lets a file be BOTH a reusable module AND a runnable script — the script part only runs when you do `python myfile.py`, not when another file does `import myfile`. Common place for the app's entry point.

---

## Q7. What are Python's main data-serialization options?

Serialization = turning objects into a storable/sendable format and back.
- **`json`** — for JSON (APIs, config). Human-readable and cross-language.
- **`pickle`** — Python-specific binary format. Convenient but **never unpickle untrusted data** (it can execute arbitrary code — a security risk).

For APIs you'll almost always use JSON (and in FastAPI, Pydantic handles it for you).

---

## Q8. What is a virtual environment and why use it?

An isolated folder with its own Python and packages for ONE project, so different projects don't clash over dependency versions (project A needs library v1, project B needs v2 — both can coexist).

Create one with `python -m venv venv` (or use `poetry`/`uv`). Always use one per project; never install everything globally.

---

## Q9. What is `pip` and `requirements.txt`?

- **`pip`** is Python's package installer (`pip install requests`).
- **`requirements.txt`** lists your project's dependencies and versions, so anyone can recreate the exact same environment with `pip install -r requirements.txt`.

Modern alternatives: `poetry` / `uv` with lock files for even more reliable, reproducible installs.

---

## Q10. What is the difference between `==` and `is` (very common)?

- `==` checks if two values are **equal** (same content).
- `is` checks if two variables point to the **exact same object** in memory.
```python
a = [1, 2, 3]
b = [1, 2, 3]
a == b   # True  — same contents
a is b   # False — two different objects
```
Use `==` for value comparison; use `is` only for `None` (`if x is None:`).

---

## Q11. What are Python's truthy and falsy values?

In a boolean check, these count as **False**: `False`, `0`, `0.0`, `""` (empty string), `[]`, `{}`, `()`, `None`. Everything else is **truthy**.

This lets you write clean checks:
```python
if my_list:          # means "if the list is NOT empty"
    process(my_list)
```

---

## Q12. How do you handle exceptions in Python?

```python
try:
    result = risky()
except ValueError as e:
    print("bad value:", e)          # handle a specific error
except (KeyError, TypeError):
    print("key/type problem")       # handle multiple types
else:
    print("ran only if NO exception occurred")
finally:
    cleanup()                        # ALWAYS runs, error or not
```
**Best practice:** catch *specific* exceptions, not a bare `except:` (which hides real bugs by swallowing everything).

---

## Q13. What is FastAPI's automatic documentation?

FastAPI reads your type hints and Pydantic models and **auto-generates interactive API docs**:
- **Swagger UI** at `/docs` — you can even test endpoints right in the browser.
- **ReDoc** at `/redoc` — a clean, readable reference.

Zero extra work — a big reason FastAPI is loved.

---

## Q14. How does FastAPI validate incoming data automatically?

You declare a Pydantic model as the request body type. FastAPI parses the JSON, checks types and constraints, and if anything's wrong it **automatically returns a clear 422 error** listing the problems — you write no validation code.
```python
from pydantic import BaseModel, Field

class User(BaseModel):
    name: str
    age: int = Field(ge=0)          # must be >= 0

@app.post("/users")
def create(user: User):
    ...                              # invalid input → automatic 422
```

---

## Q15. What is the difference between path, query, and body parameters in FastAPI?

- **Path** — part of the URL itself: `/items/{id}` → identifies a specific resource.
- **Query** — after the `?`: `/items?limit=10` → filters or options.
- **Body** — the JSON payload (a Pydantic model) → the actual data being sent.

FastAPI figures out which is which from your function signature automatically:
```python
@app.get("/items/{id}")
def read(id: int, limit: int = 10):   # id=path, limit=query
    ...
```

---

## Q16. How do you return proper HTTP status codes and errors in FastAPI?

Set a default success code with `status_code`, and raise `HTTPException` for errors:
```python
from fastapi import HTTPException

@app.get("/users/{id}")
def get(id: int):
    user = repo.find(id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user
```

---

## Q17. What is CORS in FastAPI and how do you enable it?

**CORS (Cross-Origin Resource Sharing)** is a browser security rule: a frontend on one domain is blocked from calling an API on a different domain unless the API explicitly allows it.

Enable it with middleware:
```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://myapp.com"],   # which frontends may call us
    allow_methods=["*"],
    allow_headers=["*"],
)
```

---

## Q18. When would you choose Python over Java for a service?

- **Python** for **AI/ML, data pipelines, scripting, rapid prototyping, and FastAPI microservices** — concise, with a huge AI ecosystem.
- **Java** for **CPU-heavy, high-throughput, strongly-typed enterprise backends** where the JVM's performance and mature tooling shine.

Many teams (and this JD) use **both**: Python/FastAPI for AI-facing services, Java/Spring for core enterprise services.

---

## Q19. What is a generator and why is it memory-efficient?

A generator produces values **one at a time, on demand**, using `yield`, instead of building the whole list in memory first. Perfect for reading a huge file or streaming data:
```python
def read_lines(path):
    with open(path) as f:
        for line in f:
            yield line.strip()   # one line at a time, tiny memory footprint
```
You could process a 50 GB file this way while using only a few KB of RAM at any moment.

---

## Q20. What are Python's `*args` and `**kwargs` used for in real code?

They let functions accept any number of arguments — most commonly in **decorators** and **wrapper functions** that pass arguments through to another function without knowing them in advance:
```python
def logger(fn):
    def wrapper(*args, **kwargs):
        print("calling", fn.__name__)
        return fn(*args, **kwargs)   # forward EVERYTHING to the real function
    return wrapper
```

---

## Q21. How do you connect FastAPI to a database simply?

Use SQLAlchemy (or async `asyncpg`/SQLModel), create a session per request via a dependency, and use Alembic for migrations:
```python
@app.get("/items")
def list_items(db: Session = Depends(get_db)):
    return db.query(Item).all()
```
The `get_db` dependency opens a session, `yield`s it to the endpoint, and closes it after the response is sent.

---

## Q22. What's the simplest way to explain async/await to a beginner?

Imagine a waiter (one thread) serving many tables. While one table's food is cooking (I/O wait), the waiter doesn't stand there doing nothing — they go serve other tables. `await` is the waiter saying "this will take a while, I'll go do something useful meanwhile."

This lets one thread handle thousands of waiting requests efficiently — perfect for I/O-heavy APIs.
