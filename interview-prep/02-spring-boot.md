# 02 — Spring Boot, Spring MVC, Data JPA, Security

> Anchor: You've built 100+ Spring Boot microservices. Own this section.

---

## A. Spring Core & IoC

### Q1. What is Inversion of Control (IoC) and Dependency Injection (DI)?
These are the core ideas Spring is built on:
- **IoC (Inversion of Control)** — normally *your* code controls creating and wiring objects (`new UserService(new UserRepo(...))`). With IoC you **hand that control to the framework** — Spring's "container" creates your objects (beans), figures out what each one needs, and wires them together. The control is "inverted" from your code to the framework. Think "Don't call us, we'll call you (Hollywood principle)."
- **DI (Dependency Injection)** is the *technique* Spring uses to achieve IoC: instead of a class creating its own dependencies, they are **passed in ("injected") from outside**. So `UserService` just declares "I need a `UserRepo`" and Spring supplies one.
- **Why it matters:** loose coupling (a class depends on an *interface*, not a concrete class it built itself), easy **testing** (inject mocks/fakes), and clearer single-responsibility (classes focus on logic, not wiring).
- **Three types of injection:** **constructor** (preferred — makes dependencies mandatory + `final`/immutable + easily testable with `new`), **setter** (for optional dependencies), and **field** (`@Autowired` directly on a field — convenient but discouraged because it hides dependencies and is hard to unit-test without reflection).

### Q2. What is the Spring ApplicationContext / BeanFactory?
The Spring **container** is the object that manages all your beans (creates, wires, and provides them). It comes in two flavors:
- **`BeanFactory`** — the most basic container. It's minimal and does **lazy initialization** (creates beans only when first requested). Rarely used directly.
- **`ApplicationContext`** — the one you actually use. It's a **superset** of `BeanFactory` with enterprise features: **eager initialization** (beans created at startup so problems surface early), **internationalization (i18n)**, **event publishing/listening**, **AOP support**, annotation-based configuration, and access to environment/properties. When a Spring Boot app starts, it builds an `ApplicationContext`.
- **In short:** `ApplicationContext` = `BeanFactory` + lots of production-ready extras.

### Q3. Explain Spring bean scopes.
A "scope" defines **how many instances** of a bean Spring creates and how long they live:
- **`singleton`** (the **default**) — **one shared instance per container** for the whole app. Most beans (services, repositories) are singletons and must be **stateless/thread-safe** since they're shared across all requests/threads.
- **`prototype`** — a **new instance every time** the bean is requested. Use for stateful/short-lived objects.
- **Web scopes** (only in web apps): **`request`** (one per HTTP request), **`session`** (one per user session), **`application`** (one per servlet context), and **`websocket`**.
- **Common gotcha:** injecting a `prototype` into a `singleton` — the prototype is only created *once* (when the singleton is built), so you don't get a fresh one each time; you need a scoped-proxy or `ObjectProvider` to fix that.

### Q4. Explain the Spring bean lifecycle.
Spring manages each bean from birth to death; knowing the order helps with init/cleanup hooks:
1. **Instantiate** — Spring creates the bean object (calls the constructor).
2. **Populate properties (DI)** — Spring injects the bean's dependencies.
3. **Aware callbacks** — if the bean implements `BeanNameAware`/`BeanFactoryAware`/`ApplicationContextAware`, Spring passes it those references.
4. **`BeanPostProcessor.postProcessBeforeInitialization`** — a hook to modify the bean before init.
5. **Initialization** — `@PostConstruct` method runs (or `InitializingBean.afterPropertiesSet()`, or a custom init-method) — good place for setup once dependencies are wired.
6. **`BeanPostProcessor.postProcessAfterInitialization`** — this is where Spring **wraps beans in proxies** (for AOP, `@Transactional`, etc.).
7. **Bean is ready** and used by the app.
8. **On shutdown** — `@PreDestroy` (or `DisposableBean.destroy()`) runs for cleanup (close resources).
- **Practical note:** understanding step 6 (proxy creation) explains why `@Transactional`/`@Async` self-invocation doesn't work — the proxy is on the outside.

### Q5. `@Component` vs `@Service` vs `@Repository` vs `@Controller`?
All four are **stereotype annotations** — they tell Spring "this class is a bean, please detect and manage it" during component scanning. `@Service`, `@Repository`, and `@Controller` are actually *specializations* of `@Component` — functionally similar but they **communicate intent (the layer)** and some add extra behavior:
- **`@Component`** — generic; use for any bean that doesn't fit the other categories (utilities, config helpers).
- **`@Service`** — marks the **business-logic layer**. Purely semantic (readability), but signals "this holds business rules."
- **`@Repository`** — marks the **data-access layer**. Beyond semantics, it adds **exception translation** — converting low-level `SQLException`/vendor-specific errors into Spring's consistent `DataAccessException` hierarchy.
- **`@Controller`** / **`@RestController`** — marks the **web layer** (handles HTTP requests). `@RestController` = `@Controller` + `@ResponseBody` (returns data/JSON, not view names).
- **Why use the specific ones?** clarity of layering, and you get the layer-specific extras (like repository exception translation).

### Q6. `@Autowired`, `@Qualifier`, `@Primary`?
These control how Spring picks and injects dependencies:
- **`@Autowired`** — tells Spring to **inject a matching bean by type**. It works on constructors, setters, or fields. (On a single-constructor class, it's even optional now.)
- **The problem:** what if there are **two beans of the same type** (e.g., two `PaymentService` implementations)? Spring can't decide and throws `NoUniqueBeanDefinitionException`. Two ways to resolve:
  - **`@Qualifier("beanName")`** — explicitly name *which* bean to inject at the injection point ("use the `stripePaymentService`").
  - **`@Primary`** — mark one bean as the **default** choice when there's ambiguity, so it wins unless a `@Qualifier` overrides it.

### Q7. `@Bean` vs `@Component`?
Both register a bean in the container, but they're used in different situations:
- **`@Component`** (and its stereotypes) is put **on your own class**, and Spring auto-detects it via **component scanning**. Use it for classes you write and control.
- **`@Bean`** is put **on a method inside a `@Configuration` class**, and the method's return value becomes a bean. Use it when you **can't annotate the class** — e.g., a **third-party library class** (you can't add `@Component` to someone else's code) — or when creating the bean needs **custom/programmatic logic** (build it, configure it, then return it).
```java
@Configuration
class AppConfig {
  @Bean RestClient restClient() { return RestClient.builder().baseUrl("...").build(); }
}
```

### Q8. What is Spring AOP?
**AOP (Aspect-Oriented Programming)** solves the problem of **cross-cutting concerns** — things like logging, security checks, transactions, and metrics that are needed in *many* places but aren't the core business logic. Without AOP, you'd copy that code into every method (scattered, hard to maintain). AOP lets you **write it once and apply it declaratively** across many methods. Key terms:
- **Aspect** — the module holding the cross-cutting logic (e.g., a `LoggingAspect`).
- **Advice** — the actual code to run, and *when*: `@Before`, `@After`, `@AfterReturning`, `@AfterThrowing`, `@Around` (wraps the method — most powerful).
- **Pointcut** — an expression that selects *which* methods the advice applies to (e.g., "all methods in the service package").
- **JoinPoint** — a specific point in execution where advice runs (a method call).
- **How Spring does it:** by creating a **proxy** around your bean (JDK dynamic proxy for interfaces, CGLIB subclass otherwise). The proxy intercepts calls and runs the advice around them. This is *exactly* how `@Transactional`, `@Cacheable`, `@Async`, and `@PreAuthorize` work under the hood.


---

## B. Spring Boot Essentials

### Q9. What is Spring Boot and why use it over Spring?
Plain Spring is powerful but requires a lot of **manual setup** — XML/Java config, choosing dependency versions, configuring a servlet container, wiring boilerplate. **Spring Boot** is an *opinionated* layer on top that makes "getting a production app running" fast and easy:
- **Auto-configuration** — it looks at what's on your classpath and configures sensible defaults automatically (add a DB driver → it configures a DataSource).
- **Starter dependencies** — curated dependency bundles with compatible versions, so you don't fight version conflicts.
- **Embedded server** — Tomcat/Netty is *inside* your JAR, so you run the app with `java -jar` (no separate server to install/deploy) — perfect for containers/microservices.
- **Actuator** — production endpoints for health/metrics out of the box.
- **Externalized config, no XML, sensible defaults.** Net effect: you write far less boilerplate and focus on business logic.

### Q10. How does auto-configuration work?
It's the "magic" behind Spring Boot, and it's actually simple: `@EnableAutoConfiguration` (included in `@SpringBootApplication`) makes Spring load a list of **candidate configuration classes** (from `META-INF/spring/...AutoConfiguration.imports`). Each candidate is guarded by **`@Conditional`** annotations that decide whether it should activate:
- **`@ConditionalOnClass`** — only if a certain class is on the classpath (e.g., Hibernate present → configure JPA).
- **`@ConditionalOnMissingBean`** — only if *you* haven't already defined that bean (so your config always wins).
- **`@ConditionalOnProperty`** — only if a property is set.
So adding `spring-boot-starter-data-jpa` → Hibernate is on the classpath → JPA auto-config kicks in and gives you an `EntityManagerFactory` — unless you define your own. You can always **override any default** by declaring your own bean. Run with `--debug` to see the "conditions evaluation report" showing what activated and why.

### Q11. What does `@SpringBootApplication` combine?
It's a convenience annotation that bundles three others:
- **`@Configuration`** — marks the class as a source of bean definitions.
- **`@EnableAutoConfiguration`** — turns on the auto-configuration described above.
- **`@ComponentScan`** — tells Spring to scan the current package (and sub-packages) for your `@Component`/`@Service`/`@Repository`/`@Controller` classes and register them as beans.
That's why you put your main class at the **top-level package** — so component scanning finds everything below it.

### Q12. What are starter dependencies?
A "starter" is a **curated bundle of dependencies** for a purpose, with **compatible versions already chosen** for you (managed by Spring Boot's BOM — Bill of Materials). For example, `spring-boot-starter-web` pulls in Spring MVC, Jackson (JSON), validation, and an embedded Tomcat — all version-aligned. This solves **dependency hell** (mismatched library versions causing runtime errors). Common ones: `-web`, `-data-jpa`, `-security`, `-actuator`, `-test`, `-validation`. You just add one line and get a working, compatible stack.

### Q13. How do you externalize configuration? Property precedence?
"Externalized config" means keeping settings (DB URLs, credentials, feature flags) **outside your code** so the same build runs in dev/test/prod with different values. Sources include `application.properties`/`.yml`, **profile-specific** files (`application-prod.yml`), **environment variables**, **command-line arguments**, and a central config server. When the same property is defined in multiple places, Spring uses a defined **precedence (highest wins):** command-line args > environment variables > profile-specific files > `application.properties` > defaults. Read them in code via **`@ConfigurationProperties`** (type-safe, grouped, validated — preferred) or **`@Value("${...}")`** (single values). This maps to the 12-factor principle "store config in the environment."

### Q14. What is Spring Boot Actuator?
Actuator adds **production-ready management endpoints** so you can monitor and manage a running app without writing that code yourself. Key endpoints: **`/health`** (is the app + its dependencies up? — used by Kubernetes liveness/readiness probes), **`/metrics`** and **`/prometheus`** (numeric metrics for Grafana dashboards via Micrometer), **`/info`** (build/version info), **`/loggers`** (change log levels at runtime), **`/env`**, **`/httpexchanges`**. This is exactly the foundation for observability (which you built on at MGM). **Security note:** only expose safe endpoints publicly (`health`, `info`) and lock down the rest, since some reveal sensitive internals.

### Q15. How do Spring profiles work?
Profiles let one codebase behave differently per environment. You tag beans/config with **`@Profile("dev")`** (so a bean only loads in that profile) and create **profile-specific property files** (`application-dev.yml`, `application-prod.yml`). You activate a profile with **`spring.profiles.active=prod`** (usually set as an environment variable in each environment). Example: use an in-memory H2 database in `dev` but real PostgreSQL in `prod`, or enable verbose logging only in `dev`. This keeps environment differences clean and out of the code.

---

## C. Spring MVC / REST

### Q16. Explain the DispatcherServlet flow.
The **DispatcherServlet** is the "front controller" — a single servlet that receives **every** incoming HTTP request and orchestrates handling it. The flow:
1. Request arrives → **DispatcherServlet** receives it.
2. It asks **HandlerMapping**: "which controller method handles this URL/verb?"
3. It uses a **HandlerAdapter** to actually invoke that controller method (binding path variables, query params, and the request body to method arguments).
4. The controller runs your logic and returns a result (an object, or a view name).
5. For REST APIs, an **HttpMessageConverter** (Jackson) serializes the returned object to **JSON** for the response body.
6. The response goes back to the client.
Interceptors (before/after) and exception handlers (`@ControllerAdvice`) plug in around this pipeline. Understanding this explains where things like auth filters, validation, and JSON conversion happen.

### Q17. Key REST annotations?
These map HTTP requests to your Java methods and extract data from them:
- **`@RestController`** — marks the class as a REST handler (returns JSON, not views).
- **`@RequestMapping`** / **`@GetMapping`, `@PostMapping`, `@PutMapping`, `@DeleteMapping`, `@PatchMapping`** — map a URL path + HTTP verb to a method.
- **`@PathVariable`** — pull a value from the URL path (`/users/{id}`).
- **`@RequestParam`** — pull a query-string parameter (`?page=1`).
- **`@RequestBody`** — bind the JSON request body to a Java object (Jackson deserializes it).
- **`@ResponseBody`** — write the return value as the response body (implied by `@RestController`).
- **`@ResponseStatus`** — set the HTTP status code for a response/exception.
- **`@RequestHeader`** — read a specific HTTP header.


### Q18. How do you handle exceptions globally?
`@RestControllerAdvice` + `@ExceptionHandler` methods returning a consistent error response (with `ResponseEntity` + status). Optionally extend `ResponseEntityExceptionHandler`.
```java
@RestControllerAdvice
public class GlobalExceptionHandler {
  @ExceptionHandler(ResourceNotFoundException.class)
  public ResponseEntity<ApiError> handle(ResourceNotFoundException ex) {
    return ResponseEntity.status(HttpStatus.NOT_FOUND)
        .body(new ApiError("NOT_FOUND", ex.getMessage()));
  }
}
```

### Q19. How do you validate request payloads?
You use **Bean Validation** (the `jakarta.validation` standard) to declaratively check incoming data instead of writing manual `if` checks. You annotate your DTO fields with constraints (`@NotNull`, `@NotBlank`, `@Size`, `@Email`, `@Min`, `@Max`, `@Pattern`), then put **`@Valid`** on the `@RequestBody` parameter. If validation fails, Spring throws `MethodArgumentNotValidException` and returns a **400 Bad Request** automatically — you handle it in your `@RestControllerAdvice` to shape a clean error response listing which fields failed. This centralizes validation and keeps controllers clean.
```java
record CreateUser(@NotBlank String name, @Email String email, @Min(18) int age) {}
@PostMapping("/users") User create(@Valid @RequestBody CreateUser req) { ... }
```

### Q20. `@RequestParam` vs `@PathVariable`?
Both pull values out of the incoming URL, but from different parts:
- **`@PathVariable`** reads a value **embedded in the URL path** — used to *identify a specific resource*. e.g., `GET /users/42` → `@PathVariable Long id` captures `42`.
- **`@RequestParam`** reads a value from the **query string** (after the `?`) — used for *optional filtering, sorting, pagination*. e.g., `GET /users?page=1&size=20` → `@RequestParam int page`.
- **Rule of thumb:** path variable = "which resource"; request param = "how to filter/modify the response."

### Q21. How do you version REST APIs?
Once clients depend on your API, you can't break it — so you version it and run old + new side by side during migration. Common approaches:
- **URI versioning** — `/api/v1/orders`, `/api/v2/orders`. Most common and explicit (easy to see/route/cache).
- **Header versioning** — the client sends `Accept: application/vnd.app.v1+json`. Keeps URLs clean but is less visible/testable.
- **Query param** — `/orders?version=1`. Simple but less RESTful.
- **Best practice:** version explicitly, keep the old version alive during a deprecation window, communicate timelines, and make additive (backward-compatible) changes where possible so you don't need a new version at all.

### Q22. What is content negotiation?
Content negotiation is how the server decides **what format to return** based on what the client asks for. The client sends an **`Accept`** header (e.g., `Accept: application/json` or `application/xml`), and Spring picks the matching **`HttpMessageConverter`** to serialize the response in that format. Most APIs just return JSON (via Jackson), but the mechanism lets the same endpoint serve JSON or XML depending on the client. (Similarly, `Content-Type` tells the server what format the *request body* is in.)

---

## D. Spring Data JPA / Persistence

### Q23. What is Spring Data JPA? JPA vs Hibernate?
These three terms confuse people — here's the layering:
- **JPA (Java Persistence API)** is a **specification** (a standard set of interfaces/rules) for **ORM** — Object-Relational Mapping, i.e., mapping Java objects to database tables so you work with objects instead of raw SQL. JPA itself is just the contract, not an implementation.
- **Hibernate** is the most popular **implementation** of the JPA spec — the actual engine that does the mapping, generates SQL, manages the persistence context, caching, lazy loading, etc.
- **Spring Data JPA** is a **higher-level abstraction from Spring** that sits on top of JPA/Hibernate and removes boilerplate: you just declare a **repository interface** (`interface UserRepo extends JpaRepository<User, Long>`) and Spring auto-generates the implementation, including CRUD methods and **derived queries** (methods whose SQL is inferred from the method name).
- **Analogy:** JPA = the rulebook, Hibernate = the player following the rules, Spring Data JPA = the assistant that writes most of your code for you.

### Q24. Derived queries & custom queries?
Spring Data JPA gives you three ways to define queries, from least to most control:
- **Derived queries** — Spring **parses the method name** and generates the SQL for you. `findByLastNameAndActiveTrue(...)` becomes `WHERE last_name = ? AND active = true`. Zero SQL to write for common cases.
- **`@Query` (JPQL)** — when the method name gets unwieldy, write the query yourself in JPQL (object-oriented query language over entities).
- **Native query** — drop to raw SQL with `nativeQuery = true` when you need DB-specific features.
```java
List<User> findByLastNameAndActiveTrue(String lastName);   // derived
@Query("SELECT u FROM User u WHERE u.email = :email")       // JPQL
Optional<User> findByEmail(@Param("email") String email);
@Query(value = "SELECT * FROM users WHERE ...", nativeQuery = true)  // raw SQL
```

### Q25. What is the N+1 query problem? Fix?
This is the most common JPA performance trap. You run **1 query** to fetch a list of parent entities (say 100 orders), but then, because each order's items are **LAZY**-loaded, accessing them fires **1 additional query per order** — so 1 + 100 = **101 queries** instead of a couple. It silently kills performance under load. **Fixes:**
- **`JOIN FETCH`** — `@Query("select distinct o from Order o join fetch o.items")` fetches parents + children in **one** query.
- **`@EntityGraph`** — declaratively tell the repo method which associations to fetch eagerly.
- **Batch fetching** — `@BatchSize` / `hibernate.default_batch_fetch_size` turns N queries into N/batchSize (e.g., IN clauses).
- **DTO projections** — select only the columns you need directly into a DTO, avoiding loading full entities.
Always watch the SQL logs (`spring.jpa.show-sql=true`) to catch N+1 early.

### Q26. FetchType LAZY vs EAGER?
This controls **when** an entity's associated data is loaded from the DB:
- **LAZY** — the associated data is **not loaded until you actually access it**. This is the default for collections (`@OneToMany`, `@ManyToMany`) and is generally what you want (don't load data you don't need). Catch: if you access it *after* the DB session has closed (e.g., in the controller), you get a **`LazyInitializationException`**.
- **EAGER** — the associated data is **loaded immediately** with the parent (default for `@ManyToOne`/`@OneToOne`). Convenient but dangerous: EAGER associations always load even when unneeded, and they're a major cause of N+1 and huge queries.
- **Best practice:** make everything **LAZY** by default, and explicitly fetch what you need per use case (JOIN FETCH / entity graph). Avoid EAGER as a blanket setting.

### Q27. Entity lifecycle states?
An entity (a mapped object) moves through states relative to the **persistence context** (Hibernate's "session" that tracks managed objects):
- **Transient** — a brand-new object (`new User()`) that Hibernate doesn't know about yet; not in the DB.
- **Managed/Persistent** — attached to the persistence context (after `persist()` or a query load). Hibernate **tracks changes** to it and will auto-save them ("dirty checking") at commit — you often don't even call save().
- **Detached** — was managed, but the session closed; changes are no longer tracked (needs `merge()` to re-attach).
- **Removed** — marked for deletion (`remove()`); will be deleted at flush/commit.
Key operations: `persist` (transient→managed), `merge` (detached→managed), `remove` (managed→removed), `detach` (managed→detached).

### Q28. First-level vs second-level cache?
Caching avoids hitting the DB repeatedly:
- **First-level (L1) cache** — **always on**, scoped to a **single persistence context/session** (typically one transaction). Within one transaction, loading the same entity twice hits the DB only once — the second read comes from L1. You get it for free.
- **Second-level (L2) cache** — **optional**, **shared across sessions/transactions** for the whole app (or cluster). Backed by providers like EhCache, Hazelcast, or Redis. Use it for **read-mostly, rarely-changing** entities (reference data, catalogs) to cut DB load. Needs care with invalidation so you don't serve stale data.

### Q29. Optimistic vs pessimistic locking?
Both prevent two users from clobbering each other's updates (the "lost update" problem), but with opposite strategies:
- **Optimistic locking** — assume conflicts are **rare**. Add a **`@Version`** field; when you update, Hibernate checks the version hasn't changed since you read it. If it did (someone else updated first), it throws `OptimisticLockException` and you **retry**. No DB locks held → great for **high-read, low-contention** web apps. This is the default choice.
- **Pessimistic locking** — assume conflicts are **likely**. Take an actual **DB lock** on the row when you read it (`SELECT ... FOR UPDATE` / `@Lock(PESSIMISTIC_WRITE)`), so no one else can modify it until you're done. Prevents conflicts up front but **blocks** other transactions and risks deadlocks. Use for **high-contention, must-not-fail** cases (inventory decrement, seat booking).

---

## E. Transactions

### Q30. Explain `@Transactional`.
`@Transactional` gives you **declarative transaction management** — you just annotate a method, and Spring (via an AOP proxy) automatically **starts a transaction before** the method, **commits** if it returns normally, and **rolls back** if it throws. This means a group of DB operations is **all-or-nothing** (atomic) — e.g., debit + credit in a money transfer either both happen or neither does. **Key default behavior:** it rolls back automatically only on **unchecked (RuntimeException) and Error** — **checked exceptions do NOT trigger rollback** unless you specify `@Transactional(rollbackFor = Exception.class)`. This surprises many developers.

### Q31. Propagation levels?
Propagation controls **what happens when a transactional method is called from within another transaction** — join the existing one, or start a new one? The main ones:
- **`REQUIRED`** (default) — **join** the caller's transaction if one exists, otherwise **create** a new one. 90% of cases.
- **`REQUIRES_NEW`** — **always suspend** any existing transaction and start a **brand-new independent** one. Useful for things that must commit even if the outer transaction rolls back (e.g., audit logging).
- **`NESTED`** — a **savepoint** within the current transaction; the inner part can roll back to the savepoint without killing the whole outer transaction.
- Others: `SUPPORTS` (join if exists, else run non-transactionally), `MANDATORY` (must have one, else error), `NEVER`, `NOT_SUPPORTED`.

### Q32. Isolation levels?
Isolation controls **how much one transaction is affected by other concurrent transactions** — trading consistency for concurrency:
- **READ_UNCOMMITTED** — can see others' uncommitted changes (**dirty reads**). Fastest, least safe.
- **READ_COMMITTED** (common default) — only sees committed data (no dirty reads), but the same query in the same transaction might return different results if another commits in between (**non-repeatable read**).
- **REPEATABLE_READ** — the same rows read twice give the same result (prevents non-repeatable reads), but new matching rows can still appear (**phantom reads**).
- **SERIALIZABLE** — full isolation, as if transactions ran one at a time. Safest but slowest (most locking/aborts).
Higher isolation = more consistency but less concurrency. Pick the lowest level that's still correct for your case.

### Q33. Common `@Transactional` pitfalls?
Several traps catch even experienced developers:
- **Self-invocation** — calling a `@Transactional` method from *another method in the same class* bypasses the proxy, so **no transaction starts** (the proxy only wraps external calls). Fix by moving it to another bean.
- **Applying to `private` methods** — the proxy can't intercept private methods, so `@Transactional` is silently ignored. Use `public`.
- **Expecting rollback on a checked exception** — won't happen by default; add `rollbackFor`.
- **Long transactions** — holding a transaction (and its DB connection) open while doing slow work (external API calls, heavy computation) exhausts the connection pool. Keep transactions short and focused on DB work.

---

## F. Spring Security (bridges to file 10)

### Q34. How does Spring Security work (filter chain)?
Spring Security works as a **chain of servlet filters** that sits in front of your app and inspects every request **before** it reaches your controllers. Each filter has a job, and the request passes through them in order. The flow is essentially: first **authentication** ("who are you?" — validate credentials/token) and then **authorization** ("what are you allowed to do?" — check roles/permissions). Key pieces: the **`SecurityFilterChain`** (the ordered filters), the **`AuthenticationManager`** (verifies identity), **`UserDetailsService`** (loads user + roles, for username/password auth), and the **`SecurityContextHolder`** (stores the authenticated user for the current request, in a ThreadLocal). If auth fails you get a **401**; if authorization fails, a **403**.


### Q35. Modern security config (Spring Security 6)?
```java
@Bean
SecurityFilterChain filterChain(HttpSecurity http) throws Exception {
  http.csrf(csrf -> csrf.disable())
      .authorizeHttpRequests(auth -> auth
          .requestMatchers("/api/public/**").permitAll()
          .requestMatchers("/api/admin/**").hasRole("ADMIN")
          .anyRequest().authenticated())
      .oauth2ResourceServer(o -> o.jwt(Customizer.withDefaults()));
  return http.build();
}
```

### Q36. Method-level security?
`@PreAuthorize("hasRole('ADMIN')")`, `@PostAuthorize`, `@Secured`. Enable with `@EnableMethodSecurity`.

---

## G. Testing

### Q37. How do you test Spring Boot apps?
- **Unit:** JUnit 5 + Mockito (`@Mock`, `@InjectMocks`), no Spring context.
- **Slice tests:** `@WebMvcTest` (controllers + MockMvc), `@DataJpaTest` (repositories + in-memory/Testcontainers DB).
- **Integration:** `@SpringBootTest` (full context), `TestRestTemplate`/`WebTestClient`, **Testcontainers** for real DB/Kafka.

### Q38. MockMvc example?
```java
mockMvc.perform(get("/api/users/1"))
       .andExpect(status().isOk())
       .andExpect(jsonPath("$.name").value("Anup"));
```

---

## H. Reactive (if asked — you know WebFlux basics)

### Q39. Spring MVC vs WebFlux?
- **MVC** — servlet, thread-per-request, blocking. Simpler, mature.
- **WebFlux** — reactive, non-blocking (Reactor `Mono`/`Flux`), event-loop, backpressure. Better for high-concurrency I/O with limited threads. Note: Java 21 virtual threads reduce the need for reactive in many cases.

---

## ⚡ Rapid-Fire
- **`@ControllerAdvice`** — global exception/model handling.
- **`CommandLineRunner`/`ApplicationRunner`** — run code on startup.
- **`RestTemplate` (legacy) vs `WebClient` (modern, reactive) vs `RestClient` (new synchronous, SB 3.2)**.
- **Actuator + Micrometer** → Prometheus/Grafana (you did this at MGM).
- **`@Async`** — async method execution (needs `@EnableAsync` + executor).
- **`@Scheduled`** — cron/fixed-rate jobs.
- **Spring Cloud** — Config Server, Eureka (discovery), Gateway, OpenFeign, Resilience4j, Sleuth/Micrometer Tracing.

---
---

# PART 2 — Advanced & Tough Questions (with detailed explanations + examples)

## T1. Why does `@Transactional` silently fail on self-invocation, and how do you fix it?
**The trap:** Spring's `@Transactional` works via a **proxy** that wraps your bean. When method A (no `@Transactional`) calls method B (`@Transactional`) **inside the same class**, the call goes through `this` — **bypassing the proxy** — so no transaction starts.
```java
@Service
public class OrderService {
    public void placeOrder(Order o) {
        saveOrder(o);          // internal call → proxy bypassed → NO transaction!
    }
    @Transactional
    public void saveOrder(Order o) { repo.save(o); }
}
```
**Fixes:** (1) split into two beans so the call crosses a proxy boundary; (2) self-inject the proxy (`@Autowired OrderService self; self.saveOrder(o);`); (3) use `AopContext.currentProxy()`; (4) programmatic `TransactionTemplate`. Same reasoning applies to `@Async`, `@Cacheable`, `@PreAuthorize` — all proxy-based.

**Fix 1 — Split into two beans (cleanest):**
```java
@Service
public class OrderService {
    private final OrderPersistenceService persistence;
    public OrderService(OrderPersistenceService persistence) { this.persistence = persistence; }

    public void placeOrder(Order o) {
        persistence.saveOrder(o);   // call crosses a proxy boundary → transaction applies
    }
}

@Service
public class OrderPersistenceService {
    private final OrderRepository repo;
    public OrderPersistenceService(OrderRepository repo) { this.repo = repo; }

    @Transactional
    public void saveOrder(Order o) { repo.save(o); }
}
```

**Fix 2 — Self-inject the proxy:**
```java
@Service
public class OrderService {
    private final OrderRepository repo;
    @Autowired
    private OrderService self;      // Spring injects the PROXY, not `this`

    public OrderService(OrderRepository repo) { this.repo = repo; }

    public void placeOrder(Order o) {
        self.saveOrder(o);         // goes through proxy → transaction applies
    }

    @Transactional
    public void saveOrder(Order o) { repo.save(o); }
}
```

**Fix 3 — `AopContext.currentProxy()`** (requires `@EnableAspectJAutoProxy(exposeProxy = true)`):
```java
@Configuration
@EnableAspectJAutoProxy(exposeProxy = true)   // exposes the proxy on a ThreadLocal
public class AopConfig { }

@Service
public class OrderService {
    private final OrderRepository repo;
    public OrderService(OrderRepository repo) { this.repo = repo; }

    public void placeOrder(Order o) {
        ((OrderService) AopContext.currentProxy()).saveOrder(o);  // proxy call
    }

    @Transactional
    public void saveOrder(Order o) { repo.save(o); }
}
```

**Fix 4 — Programmatic `TransactionTemplate`** (no proxy needed at all):
```java
@Service
public class OrderService {
    private final OrderRepository repo;
    private final TransactionTemplate txTemplate;

    public OrderService(OrderRepository repo, PlatformTransactionManager txManager) {
        this.repo = repo;
        this.txTemplate = new TransactionTemplate(txManager);
    }

    public void placeOrder(Order o) {
        txTemplate.executeWithoutResult(status -> repo.save(o));  // explicit transaction
    }
}
```

## T2. Constructor vs field injection — why is constructor injection strongly preferred?
- **Immutability & final fields** — dependencies can be `final`, guaranteeing they're set.
- **Testability** — you can `new OrderService(mockRepo)` without Spring/reflection.
- **Fails fast** on missing/circular dependencies at startup, not at runtime.
- **No hidden NPEs** — field injection can leave fields null in unit tests.
- Field injection also hides that a class has too many dependencies (a design smell).

## T3. How do you resolve a circular dependency? Should you?
Spring can resolve some circular singleton deps via a 3-level cache (early references), but **constructor-based** cycles fail at startup (`BeanCurrentlyInCreationException`). Options: refactor (best — extract a third bean), use setter/`@Lazy` injection, or redesign responsibilities. In interviews: "A circular dependency is usually a design smell — I'd break it by extracting the shared logic."

## T4. Explain how auto-configuration is implemented under the hood.
`@EnableAutoConfiguration` triggers loading of candidate config classes listed in `META-INF/spring/org.springframework.boot.autoconfigure.AutoConfiguration.imports` (Spring Boot 3; previously `spring.factories`). Each is guarded by **`@Conditional`** annotations:
- `@ConditionalOnClass` (a class is on the classpath),
- `@ConditionalOnMissingBean` (user hasn't defined their own),
- `@ConditionalOnProperty`, `@ConditionalOnBean`, etc.
So adding `spring-boot-starter-data-jpa` puts Hibernate on the classpath → `DataSourceAutoConfiguration` + `HibernateJpaAutoConfiguration` activate → you get an `EntityManagerFactory` unless you define your own. Debug with `--debug` (prints the **conditions evaluation report**).

## T5. How would you write your own Spring Boot starter / auto-configuration?
Create an `@AutoConfiguration` class with `@Conditional` guards + `@ConfigurationProperties`, register it in `AutoConfiguration.imports`, and package it as `xxx-spring-boot-starter`. (You essentially did this at MGM with the reusable observability common module — mention it!)

## T6. N+1 problem — show it and three fixes.
```java
// Entity: Order has @OneToMany List<LineItem> items (LAZY)
List<Order> orders = orderRepo.findAll();          // 1 query
orders.forEach(o -> o.getItems().size());          // N more queries (one per order!)
```
**Fixes:**
1. **JOIN FETCH:** `@Query("select distinct o from Order o join fetch o.items")`.
2. **`@EntityGraph`:** `@EntityGraph(attributePaths = "items")` on the repo method.
3. **Batch fetching:** `@BatchSize(size = 50)` or `hibernate.default_batch_fetch_size` → turns N queries into N/50.
Also: use **DTO projections** to fetch only needed columns and avoid loading entities entirely.

## T7. `LazyInitializationException` — root cause and correct fixes.
Accessing a LAZY association **after** the persistence context (session) is closed (e.g., in the controller/view). **Wrong fix:** `spring.jpa.open-in-view=true` (Open Session In View — keeps session open through the request; convenient but causes DB connections held too long + hidden N+1). **Right fixes:** fetch what you need inside the `@Transactional` service layer (JOIN FETCH / entity graph / map to DTO before returning).

## T8. `save()` vs `saveAndFlush()`, and the dirty-checking mechanism.
Within a transaction, Hibernate tracks managed entities and **auto-flushes** changes at commit (or before a query) — you often don't need to call `save()` on an already-managed entity (dirty checking updates it). `saveAndFlush()` forces an immediate flush (e.g., to get a generated ID or trigger constraint errors early). `save()` on a new entity persists; on a detached one it does a `merge`.

## T9. How do transaction propagation levels behave in a real scenario?
Example: an `OrderService.place()` (`REQUIRED`) calls `AuditService.log()` marked `REQUIRES_NEW`. Even if the order transaction **rolls back**, the audit log is in a **separate committed transaction** → the audit survives. Contrast with `REQUIRED` where the audit would roll back too. `NESTED` uses savepoints — inner can roll back to a savepoint without killing the outer.

## T10. Why doesn't a checked exception roll back a transaction by default?
Spring's default is to roll back on `RuntimeException`/`Error` only (following EJB convention that checked exceptions are "business" exceptions you might recover from). To change: `@Transactional(rollbackFor = Exception.class)`. Common bug: throwing a checked exception expecting rollback and getting a partial commit.

## T11. Bean scopes gotcha: injecting a prototype into a singleton.
A `prototype` bean injected into a `singleton` is created **once** (at singleton creation) — you don't get a new instance per use. Fixes: `@Lookup` method injection, `ObjectProvider<T>`, or scoped proxy (`@Scope(value="prototype", proxyMode=TARGET_CLASS)`). Same issue with request-scoped beans in singletons → use scoped proxies.

## T12. `RestTemplate` vs `WebClient` vs `RestClient` — which and why?
- `RestTemplate` — synchronous, **maintenance mode** (not deprecated, but no new features).
- `WebClient` — reactive, non-blocking (`Mono`/`Flux`); use in WebFlux or when you need concurrency/streaming.
- `RestClient` (Spring 6.1) — modern **synchronous** fluent client with WebClient-style API — the recommended replacement for RestTemplate in servlet apps. Always configure **connect/read timeouts** (RestTemplate has none by default → a hung dependency can exhaust your thread pool).

## T13. How do you handle validation + a consistent error contract across a large API?
Combine `@Valid` + a `@RestControllerAdvice` that handles `MethodArgumentNotValidException`, `ConstraintViolationException`, and your domain exceptions, returning **RFC 7807 `ProblemDetail`** (built into Spring 6):
```java
@ExceptionHandler(MethodArgumentNotValidException.class)
ProblemDetail handle(MethodArgumentNotValidException ex) {
    var pd = ProblemDetail.forStatus(HttpStatus.BAD_REQUEST);
    pd.setTitle("Validation failed");
    pd.setProperty("errors", ex.getBindingResult().getFieldErrors().stream()
        .collect(Collectors.toMap(FieldError::getField, FieldError::getDefaultMessage)));
    return pd;
}
```

## T14. How does Spring Security's filter chain actually process a JWT request?
**The big picture:** Spring Security is a **chain of servlet filters** (the `FilterChainProxy`) that sits in front of your `DispatcherServlet`. Every request passes through these filters **in a fixed order** before it ever reaches your controller. For a stateless JWT API, the important ones are the **`BearerTokenAuthenticationFilter`** (authenticates the token) and the **`AuthorizationFilter`** (enforces access rules). Nothing is stored in a session — the identity is re-established **on every request** from the token.

**Step-by-step flow of one JWT request:**
1. Request arrives with header `Authorization: Bearer eyJhbGci...`.
2. It enters the **`SecurityFilterChain`** and passes through filters in order.
3. **`BearerTokenAuthenticationFilter`** extracts the raw token via a `BearerTokenResolver`.
4. It hands the token to the **`AuthenticationManager`** → `JwtAuthenticationProvider`.
5. The **`JwtDecoder`** validates the token: **signature** (using public keys fetched from the **JWKS** endpoint), **expiry (`exp`)**, `nbf`, `iss`, `aud`.
6. On success, a **`JwtAuthenticationConverter`** turns JWT claims (e.g., `scope`/`roles`) into Spring **`GrantedAuthority`** objects and builds an `Authentication`.
7. That `Authentication` is stored in the **`SecurityContextHolder`** (a **ThreadLocal** for the current request thread).
8. The **`AuthorizationFilter`** checks your `authorizeHttpRequests` rules (and later `@PreAuthorize` at the method level).
9. If everything passes → the request reaches your **controller**. If not:
   - Token missing/invalid/expired → **`AuthenticationEntryPoint`** returns **401 Unauthorized**.
   - Authenticated but lacks the role/authority → **`AccessDeniedHandler`** returns **403 Forbidden**.
10. After the response is written, Spring **clears the `SecurityContextHolder`** so the thread is clean for the next request.

**Visualization — the filter chain for a JWT request:**
```
                         ┌──────────────────────────────────────────────┐
Client                   │            Spring SecurityFilterChain          │
  │  GET /api/orders     │  (ordered servlet filters, run top → bottom)   │
  │  Authorization:      │                                                │
  │  Bearer eyJhbGci...  │                                                │
  ▼                      │                                                │
┌─────────┐   request    │  1. SecurityContextPersistenceFilter           │
│ Browser ├──────────────►     (sets up empty context)                    │
└─────────┘              │            │                                   │
                         │            ▼                                   │
                         │  2. BearerTokenAuthenticationFilter            │
                         │       • extract "Bearer <token>"               │
                         │       • AuthenticationManager                  │
                         │            │                                   │
                         │            ▼                                   │
                         │       JwtDecoder validates:                    │
                         │       ┌───────────────────────────┐           │
                         │       │ signature (via JWKS keys)  │           │
                         │       │ exp / nbf / iss / aud      │           │
                         │       └───────────────────────────┘           │
                         │            │ valid?                            │
                         │      ┌─────┴─────┐                             │
                         │  NO  │           │ YES                         │
                         │      ▼           ▼                             │
                         │  401 via    JwtAuthenticationConverter         │
                         │  Entry      → GrantedAuthorities               │
                         │  Point      → store in SecurityContextHolder   │
                         │                 (ThreadLocal)                  │
                         │                 │                              │
                         │                 ▼                              │
                         │  3. AuthorizationFilter                        │
                         │       • authorizeHttpRequests rules            │
                         │       • hasRole / hasAuthority                 │
                         │            │ allowed?                          │
                         │      ┌─────┴─────┐                             │
                         │  NO  │           │ YES                         │
                         │      ▼           ▼                             │
                         │  403 via    ┌──────────────────┐               │
                         │  Access     │ DispatcherServlet│               │
                         │  Denied     │   → @Controller  │               │
                         │  Handler    └──────────────────┘               │
                         └──────────────────────────────────────────────┘
```

**Sample config — JWT resource server (Spring Security 6):**
```java
@Configuration
@EnableWebSecurity
@EnableMethodSecurity                     // enables @PreAuthorize / @PostAuthorize
public class SecurityConfig {

    @Bean
    SecurityFilterChain filterChain(HttpSecurity http) throws Exception {
        http
            .csrf(csrf -> csrf.disable())                         // stateless API → no CSRF
            .sessionManagement(sm -> sm
                .sessionCreationPolicy(SessionCreationPolicy.STATELESS))  // no HTTP session
            .authorizeHttpRequests(auth -> auth
                .requestMatchers("/api/public/**").permitAll()
                .requestMatchers("/api/admin/**").hasRole("ADMIN")
                .anyRequest().authenticated())
            .oauth2ResourceServer(oauth -> oauth
                .jwt(jwt -> jwt.jwtAuthenticationConverter(jwtAuthConverter())))
            .exceptionHandling(ex -> ex
                .authenticationEntryPoint((req, res, e) ->
                    res.sendError(HttpStatus.UNAUTHORIZED.value(), "Invalid or missing token"))
                .accessDeniedHandler((req, res, e) ->
                    res.sendError(HttpStatus.FORBIDDEN.value(), "Insufficient privileges")));
        return http.build();
    }

    // Tells Spring where to fetch public keys (JWKS) to verify the token signature
    @Bean
    JwtDecoder jwtDecoder() {
        return NimbusJwtDecoder
            .withJwkSetUri("https://your-idp.com/.well-known/jwks.json")
            .build();
    }

    // Map a custom "roles" claim → ROLE_* authorities (default expects "scope"/"scp")
    private JwtAuthenticationConverter jwtAuthConverter() {
        JwtGrantedAuthoritiesConverter authorities = new JwtGrantedAuthoritiesConverter();
        authorities.setAuthoritiesClaimName("roles");   // e.g. claim: "roles": ["ADMIN","USER"]
        authorities.setAuthorityPrefix("ROLE_");

        JwtAuthenticationConverter converter = new JwtAuthenticationConverter();
        converter.setJwtGrantedAuthoritiesConverter(authorities);
        return converter;
    }
}
```

**application.yml (simplest form — no custom JwtDecoder bean needed):**
```yaml
spring:
  security:
    oauth2:
      resourceserver:
        jwt:
          # Spring auto-discovers the JWKS endpoint from the issuer's metadata
          issuer-uri: https://your-idp.com/
```

**Using the authenticated user in a controller / method security:**
```java
@RestController
@RequestMapping("/api/orders")
public class OrderController {

    @GetMapping
    @PreAuthorize("hasRole('USER')")          // checked by AuthorizationManager
    public List<Order> myOrders(@AuthenticationPrincipal Jwt jwt) {
        String userId = jwt.getSubject();     // "sub" claim
        String email  = jwt.getClaim("email");
        return orderService.findByUser(userId);
    }

    @DeleteMapping("/{id}")
    @PreAuthorize("hasRole('ADMIN')")         // 403 if the JWT lacks ROLE_ADMIN
    public void delete(@PathVariable Long id) {
        orderService.delete(id);
    }
}
```

**Key gotchas to mention:**
- The `SecurityContextHolder` uses a **ThreadLocal**, so `@Async`/`CompletableFuture` methods **lose the security context** unless you use `DelegatingSecurityContextExecutor` or set `SecurityContextHolder.setStrategyName(MODE_INHERITABLETHREADLOCAL)`.
- Always validate **`iss`**, **`aud`**, and **`exp`** — not just the signature.
- Prefer **`issuer-uri`** so keys are fetched (and rotated) automatically from JWKS; hardcoding keys breaks on key rotation.
- **Order matters:** authentication filters run **before** the authorization filter — that's why `@PreAuthorize` can rely on the populated `SecurityContext`.

**One-liner:** "It's an ordered servlet-filter pipeline: `BearerTokenAuthenticationFilter` extracts the token, `JwtDecoder` validates the signature (via JWKS) and claims, a converter maps claims to authorities stored in the ThreadLocal `SecurityContextHolder`, then `AuthorizationFilter`/`@PreAuthorize` enforce access — failures short-circuit to 401 (auth) or 403 (authz)."

## T15. Startup performance & GraalVM native images (modern topic).
Spring Boot 3 supports **AOT processing** + **GraalVM native images** → millisecond startup, low memory (great for serverless/Azure Functions). Trade-offs: build complexity, reflection needs hints, some libraries unsupported. Also mention **virtual threads** (`spring.threads.virtual.enabled=true`) for high-concurrency blocking workloads on Boot 3.2+.

## T16. Tough rapid-fire
- **How to run code after startup but before serving traffic?** `ApplicationRunner`/`CommandLineRunner`, or `@EventListener(ApplicationReadyEvent.class)`.
- **How to conditionally load a bean only in prod?** `@Profile("prod")` or `@ConditionalOnProperty`.
- **Why prefer `@ConfigurationProperties` over scattered `@Value`?** type-safe, validated, grouped, testable, supports relaxed binding + nested objects.
- **Actuator endpoint security?** expose only `health`/`info` publicly; secure the rest; use a separate management port.
- **How to test only the web layer fast?** `@WebMvcTest` (loads controllers + `MockMvc`, mocks services).
- **How to test with a real Postgres/Kafka?** `@SpringBootTest` + **Testcontainers** (`@ServiceConnection` auto-wires the container in Boot 3.1+).

---
---

# PART 3 — More Real Interview Questions (Easy Language, No Repeats)

## Q1. In one line, what does Spring Boot actually do for me?
It removes the tedious setup. Instead of manually configuring a web server, JSON converter, database connection, etc., Spring Boot looks at what libraries you added and **auto-configures sensible defaults**, gives you an **embedded server**, and lets you run the app with a single `main()` method. You focus on business logic.

## Q2. What is a Spring Bean, in simple words?
A **bean** is just an object that Spring creates and manages for you (instead of you doing `new`). Spring keeps these objects in a container, wires them together, and hands them out wherever needed. Anything annotated `@Component`/`@Service`/`@Repository`/`@Bean` becomes a bean.

## Q3. What is the difference between `@RestController` and `@Controller`?
- `@Controller` — traditional MVC; methods usually return a **view name** (like an HTML page).
- `@RestController` = `@Controller` + `@ResponseBody` — methods return **data** (JSON/XML) directly, not a view. Use `@RestController` for REST APIs.

## Q4. What is the difference between PUT, POST, and PATCH?
- **POST** — create a new resource (not idempotent — calling twice makes two resources).
- **PUT** — replace/update a resource fully (idempotent — calling twice gives the same result).
- **PATCH** — partially update a resource (only the fields you send).

## Q5. How do you read a value from `application.properties` into your code?
Two ways:
```java
@Value("${app.timeout:30}")   // :30 is a default if missing
private int timeout;
```
Or type-safe grouping with `@ConfigurationProperties`:
```java
@ConfigurationProperties(prefix = "app")
public class AppProps { private int timeout; /* getters/setters */ }
```

## Q6. What is `application.yml` and how is it different from `.properties`?
Same purpose (configuration), different format. YAML is **hierarchical/indented**, cleaner for nested config:
```yaml
app:
  timeout: 30
  db:
    url: jdbc:postgresql://localhost/mydb
```
vs properties: `app.db.url=...`. Boot supports both.

## Q7. How do you connect Spring Boot to a database?
Add the JDBC driver + `spring-boot-starter-data-jpa`, then set 4 properties: URL, username, password, and (optionally) the JPA/Hibernate settings. Boot auto-creates the `DataSource`, connection pool (**HikariCP** by default), and `EntityManager`.
```properties
spring.datasource.url=jdbc:postgresql://localhost:5432/mydb
spring.datasource.username=admin
spring.datasource.password=secret
spring.jpa.hibernate.ddl-auto=validate
```

## Q8. What is `spring.jpa.hibernate.ddl-auto` and its safe values?
It controls whether Hibernate changes your DB schema on startup:
- `none` / `validate` — **safe for production** (validate just checks the schema matches).
- `update` — adds missing columns/tables (convenient in dev, risky in prod).
- `create` / `create-drop` — wipes and recreates (dev/testing only).
In production use `validate` + a proper migration tool (Flyway/Liquibase).

## Q9. What is `CrudRepository` vs `JpaRepository`?
- `CrudRepository` — basic CRUD methods (save, findById, delete, etc.).
- `JpaRepository` (extends the above) — adds JPA extras: pagination (`findAll(Pageable)`), sorting, batch operations, `flush()`. In practice most people just use `JpaRepository`.

## Q10. How do you add pagination to an API?
Return a `Page<T>` and accept a `Pageable`:
```java
@GetMapping("/users")
Page<User> list(@RequestParam int page, @RequestParam int size) {
    return userRepo.findAll(PageRequest.of(page, size, Sort.by("name")));
}
```
The response includes content + total pages + total elements — the frontend uses it to render page controls.

## Q11. What is a DTO and why not just return entities?
A **DTO (Data Transfer Object)** is a simple object shaped exactly for the API response. Returning JPA entities directly is risky: it can leak internal fields (passwords), cause lazy-loading errors, and tightly couple your API to your DB schema. DTOs give you a clean, stable API contract. Map entity→DTO with MapStruct or manually.

## Q12. What is CORS and how do you enable it in Spring Boot?
CORS is a browser rule that blocks a webpage from calling an API on a different domain unless the API allows it. Enable it:
```java
@CrossOrigin(origins = "https://myapp.com")   // per controller
// or globally:
@Bean
WebMvcConfigurer cors() {
  return new WebMvcConfigurer() {
    public void addCorsMappings(CorsRegistry r) {
      r.addMapping("/api/**").allowedOrigins("https://myapp.com");
    }
  };
}
```

## Q13. What is an Interceptor, and how is it different from a Filter?
Both intercept requests, but:
- **Filter** (Servlet level) — runs before Spring's DispatcherServlet; good for logging, auth, compression, CORS.
- **Interceptor** (Spring MVC level) — runs around controller methods (`preHandle`/`postHandle`); has access to the handler/controller info. Use interceptors for things needing Spring context (e.g., adding data to the model).

## Q14. How do you schedule a recurring task in Spring Boot?
Add `@EnableScheduling` and annotate a method:
```java
@Scheduled(cron = "0 0 2 * * *")   // every day at 2 AM
public void nightlyCleanup() { ... }

@Scheduled(fixedRate = 5000)        // every 5 seconds
public void poll() { ... }
```

## Q15. How do you run code asynchronously?
Add `@EnableAsync`, then annotate a method `@Async` — it runs on a separate thread and returns immediately (or a `CompletableFuture`). Remember: `@Async` works via proxy, so calling it from within the same class won't work (same self-invocation rule as `@Transactional`).

## Q16. What is the difference between `@Mock` and `@MockBean`?
- `@Mock` (Mockito) — a plain mock object for **unit tests**, no Spring context.
- `@MockBean` (Spring Boot) — puts a mock **into the Spring context**, replacing the real bean, for **integration/slice tests** like `@WebMvcTest`.

## Q17. How do you handle different configs for dev, test, and prod?
Use **profiles**: create `application-dev.yml`, `application-prod.yml`, and activate with `spring.profiles.active=prod` (via env variable in each environment). Beans can be profile-specific with `@Profile("prod")`.

## Q18. What is HATEOAS (you may just need to recognize it)?
It's a REST principle where API responses include **links** to related actions (e.g., an order response includes a link to "cancel" or "pay"). Spring HATEOAS supports it. Rarely mandatory, but good to know the term.

## Q19. How does Spring Boot handle logging by default?
It uses **Logback** via SLF4J out of the box. You set levels in properties (`logging.level.com.myapp=DEBUG`), and can switch to Log4j2 if needed. For production, output **structured JSON logs** with correlation IDs so they're searchable in a central system.

## Q20. What is the difference between `@RequestBody` and `@ModelAttribute`?
- `@RequestBody` — binds the **JSON body** of the request to an object (typical for REST APIs).
- `@ModelAttribute` — binds **form data / query params** to an object (typical for HTML form submissions).

## Q21. What are common reasons a Spring Boot app fails to start?
- Port already in use → change `server.port`.
- Missing DB connection / wrong credentials.
- Two beans of the same type without `@Primary`/`@Qualifier` (ambiguity).
- A required bean not found (missing dependency/annotation).
- Circular dependency between beans.
Read the **first** error in the stack trace + the auto-configuration report (`--debug`).

## Q22. How do you expose application health and metrics?
Add **Actuator** (`spring-boot-starter-actuator`). It gives `/actuator/health` (up/down + DB/disk checks), `/actuator/metrics`, and `/actuator/prometheus` (for Grafana). Kubernetes uses `/actuator/health/liveness` and `/readiness` for probes.

---
---

# PART 4 — Real Interview-Level Questions (deep, exactly how they're asked)

> These are phrased the way interviewers actually ask them — short, pointed, and probing. Each answer is detailed and speak-out-loud ready.

### IQ1. What is Spring Boot and how is it different from Spring?
- **Spring (the framework)** is a large, modular ecosystem (Core/IoC, MVC, Data, Security, etc.) that is **powerful but requires a lot of manual configuration** — XML or Java config, choosing versions, setting up a servlet container, wiring everything yourself.
- **Spring Boot** sits **on top of Spring** and makes it **production-ready with almost zero configuration**. Its three big ideas:
  1. **Auto-configuration** — it looks at what's on your classpath and configures sensible beans automatically (e.g., see `spring-webmvc` → configure a `DispatcherServlet`; see an H2 driver → configure an in-memory DataSource).
  2. **Starters** — curated dependency bundles (`spring-boot-starter-web`, `-data-jpa`, `-security`) that pull in compatible versions together, ending "dependency hell."
  3. **Embedded server** — Tomcat/Jetty/Undertow is embedded, so you run a **single executable JAR** (`java -jar`) with no external server to install.
- **Plus:** Actuator (production endpoints), sensible defaults, externalized config (`application.yml`), and easy profiles.
- **One-liner:** "Spring gives you the building blocks; Spring Boot assembles them into a runnable, production-ready app with auto-configuration, starters, and an embedded server — convention over configuration."

### IQ2. How does auto-configuration actually work under the hood?
- It's driven by **`@EnableAutoConfiguration`** (included in `@SpringBootApplication`).
- Spring Boot ships hundreds of **auto-configuration classes**, each guarded by **`@Conditional`** annotations:
  - `@ConditionalOnClass` — apply only if a class is on the classpath.
  - `@ConditionalOnMissingBean` — back off if *you* already defined that bean (so your config wins).
  - `@ConditionalOnProperty` — apply only if a property is set.
- **Discovery mechanism:** in modern Boot (2.7+/3.x) these classes are listed in `META-INF/spring/org.springframework.boot.autoconfigure.AutoConfiguration.imports` (older Boot used `spring.factories`). At startup Boot reads that list and evaluates each class's conditions.
- **How to see what happened:** run with `--debug` to get the **auto-configuration report** showing which configs matched ("positive matches") and which backed off ("negative matches").
- **One-liner:** "Auto-config is conditional bean registration — classes annotated with `@ConditionalOnClass`/`@ConditionalOnMissingBean` are discovered from the AutoConfiguration.imports file and applied only when their conditions hold, and they always back off if you define your own bean."

### IQ3. What does `@SpringBootApplication` combine?
It's a convenience meta-annotation bundling three:
- **`@Configuration`** — marks the class as a source of bean definitions.
- **`@EnableAutoConfiguration`** — turns on the auto-configuration mechanism (IQ2).
- **`@ComponentScan`** — scans the current package and sub-packages for `@Component`/`@Service`/`@Repository`/`@Controller` beans.
- **Gotcha:** put your main class in a **top-level package** so component scanning covers everything beneath it.

### IQ4. Constructor vs field vs setter injection — which and why?
- **Constructor injection (preferred):** dependencies are **mandatory, final, immutable**, and the object is always in a valid state once constructed. Easiest to unit-test (`new Service(mockRepo)`), and it **exposes** heavy dependencies (a huge constructor is a design smell nudging you to refactor). Since Spring 4.3, a single constructor doesn't even need `@Autowired`.
- **Field injection (`@Autowired` on a field):** convenient but **discouraged** — hides dependencies, can't be `final`, needs reflection to test, and allows too-many-dependencies to sneak in unnoticed.
- **Setter injection:** good for **optional/changeable** dependencies.
- **One-liner:** "Constructor injection by default — immutable, testable, and it surfaces bad design. Field injection is convenient but hides dependencies and hurts testing."

### IQ5. How do transactions work in Spring? Explain `@Transactional`, propagation, and isolation.
- **`@Transactional`** wraps a method in a database transaction: begin on entry, **commit** on normal return, **rollback** on a runtime (unchecked) exception. It works via a **Spring AOP proxy** around the bean.
- **Rollback rule (classic gotcha):** by default Spring rolls back on **`RuntimeException`/`Error`** but **NOT on checked exceptions**. Use `@Transactional(rollbackFor = Exception.class)` to change that.
- **Propagation** — what happens if a transaction already exists:
  - `REQUIRED` (default) — join the existing one, or start a new one.
  - `REQUIRES_NEW` — always suspend the current and start a fresh independent transaction (useful for audit logs that must commit even if the outer fails).
  - `NESTED`, `SUPPORTS`, `MANDATORY`, `NEVER`, `NOT_SUPPORTED`.
- **Isolation** — how much concurrent transactions see each other: `READ_COMMITTED` (typical default), `REPEATABLE_READ`, `SERIALIZABLE` (safest, slowest), `READ_UNCOMMITTED`. Controls dirty/non-repeatable/phantom reads.
- **The #1 gotcha — self-invocation:** calling a `@Transactional` method **from another method in the same class** bypasses the proxy, so the transaction **doesn't apply**. Fix: call it from another bean, or self-inject the proxy.
- **Another gotcha:** `@Transactional` on a **private** method does nothing (proxy can't intercept it).
- **One-liner:** "`@Transactional` is AOP-proxy-based: commits on success, rolls back on unchecked exceptions by default. Watch self-invocation (proxy bypass), checked-exception rollback, and propagation like REQUIRES_NEW for independent commits."

### IQ6. What is the N+1 query problem in JPA/Hibernate and how do you fix it?
- **The problem:** you load a list of N parent entities (1 query), then accessing a **lazy** association on each triggers **one more query per parent** → **1 + N queries**. E.g., load 100 departments, then loop and call `dept.getEmployees()` → 1 + 100 = 101 queries. It silently kills performance.
- **Fixes:**
  - **`JOIN FETCH`** in JPQL — load parents and children in **one** query: `SELECT d FROM Department d JOIN FETCH d.employees`.
  - **`@EntityGraph`** — declaratively specify what to fetch eagerly on a repository method.
  - **Batch fetching** — `@BatchSize(size = n)` / `hibernate.default_batch_fetch_size` to load children in batches (1 + N/n queries).
  - **DTO projections** — select only the fields you need directly into a DTO.
- **How to detect it:** enable `spring.jpa.show-sql=true` or use a tool that counts queries; a spike of identical queries is the tell.
- **One-liner:** "N+1 is one query for parents plus one per child access; fix with `JOIN FETCH`, `@EntityGraph`, batch fetching, or DTO projections — and prefer LAZY + explicit fetch over EAGER."

### IQ7. Explain `FetchType.LAZY` vs `EAGER` and the `LazyInitializationException`.
- **LAZY** — related data is loaded **only when accessed** (Hibernate returns a proxy). Efficient; default for `@OneToMany`/`@ManyToMany`.
- **EAGER** — related data is loaded **immediately** with the parent. Default for `@ManyToOne`/`@OneToOne`. Can cause N+1 and over-fetching.
- **`LazyInitializationException`** — thrown when you access a lazy association **after the persistence context (Hibernate session) is closed** (e.g., in the controller/view after the `@Transactional` service method returned). Fixes: fetch it within the transaction (`JOIN FETCH`/entity graph), map to a DTO inside the transaction, or keep the session open (Open-Session-In-View — generally discouraged).
- **Best practice:** prefer **LAZY everywhere** and fetch explicitly what you need per use case.

### IQ8. How do you handle exceptions globally in a Spring Boot REST API?
- Use **`@RestControllerAdvice`** (a global exception handler) with **`@ExceptionHandler`** methods that map exceptions to clean HTTP responses:
  ```java
  @RestControllerAdvice
  public class GlobalExceptionHandler {
    @ExceptionHandler(EntityNotFoundException.class)
    public ResponseEntity<ApiError> handleNotFound(EntityNotFoundException ex) {
      return ResponseEntity.status(404).body(new ApiError("NOT_FOUND", ex.getMessage()));
    }
    @ExceptionHandler(MethodArgumentNotValidException.class)  // @Valid failures
    public ResponseEntity<ApiError> handleValidation(MethodArgumentNotValidException ex) { ... }
  }
  ```
- **Benefits:** centralizes error handling, consistent error payload shape, keeps controllers clean.
- **Modern option:** return **RFC 7807 `ProblemDetail`** (built into Spring 6) for standardized error bodies.
- **One-liner:** "`@RestControllerAdvice` + `@ExceptionHandler` centralizes error-to-HTTP mapping with a consistent error contract — I return a standard error DTO (or `ProblemDetail`) and appropriate status codes."

### IQ9. How do you validate request data in Spring Boot?
- Use **Bean Validation (Jakarta Validation)** annotations on the DTO (`@NotNull`, `@NotBlank`, `@Size`, `@Email`, `@Min`, `@Pattern`) and trigger with **`@Valid`** on the controller parameter:
  ```java
  public ResponseEntity<?> create(@Valid @RequestBody UserDto dto) { ... }
  ```
- Validation failures throw `MethodArgumentNotValidException` → handle it in your `@RestControllerAdvice` to return field-level errors.
- **Custom validators** — implement `ConstraintValidator` for domain rules; use `@Validated` at class level for group validation and method-level validation on services.

### IQ10. How do you secure a Spring Boot REST API (Spring Security + JWT)?
- **Spring Security** adds a **filter chain** in front of your endpoints. For stateless REST APIs:
  - Disable session creation (`SessionCreationPolicy.STATELESS`) — no server sessions.
  - Add a **JWT authentication filter** that reads the `Authorization: Bearer <token>` header, **validates the signature + expiry**, extracts the user/roles, and sets the `SecurityContext`.
  - Configure endpoint authorization: `authorizeHttpRequests` with role/authority rules; use **method security** (`@PreAuthorize("hasRole('ADMIN')")`) for fine-grained control.
- **Flow:** client logs in → server issues a signed JWT → client sends it on every request → filter validates it → request proceeds with the authenticated principal.
- **Best practices:** short-lived access tokens + refresh tokens, validate `iss`/`aud`/`exp`, use HTTPS, store secrets securely, and never trust the client — always re-check on the server.
- **One-liner:** "Stateless JWT: a custom filter validates the bearer token's signature and claims, populates the SecurityContext, and `@PreAuthorize`/`authorizeHttpRequests` enforce authorization — no server-side sessions."

### IQ11. How do you write tests in Spring Boot? `@SpringBootTest` vs slice tests?
- **`@SpringBootTest`** — loads the **full application context**; use for **integration tests**. Heavier/slower.
- **Slice tests** load only part of the context (faster, focused):
  - **`@WebMvcTest`** — just the web layer (controllers + MVC), mock the services with `@MockBean`.
  - **`@DataJpaTest`** — just the JPA layer with an in-memory DB + transaction rollback per test.
  - **`@RestClientTest`, `@JsonTest`**, etc.
- **`@MockBean`** — replaces a bean in the context with a Mockito mock.
- **Testcontainers** — spin up a **real Postgres/Kafka in Docker** for high-fidelity integration tests.
- **One-liner:** "Slice tests (`@WebMvcTest`, `@DataJpaTest`) for fast, focused layer testing; `@SpringBootTest` + Testcontainers for full integration against real infrastructure."

### IQ12. How do you manage configuration and profiles across environments?
- **Externalized config** — `application.yml` + environment-specific files (`application-dev.yml`, `application-prod.yml`), activated with **profiles** (`spring.profiles.active=prod`).
- **Property precedence** — command-line args > env vars > profile files > `application.yml` > defaults (Spring's ordered property sources).
- **Type-safe config** — `@ConfigurationProperties(prefix = "app")` binds a group of properties to a POJO (preferred over scattered `@Value`).
- **Secrets** — never commit them; inject via environment variables, Azure Key Vault, or a config server.
- **`@Profile`** — register beans only for certain environments (e.g., a mock mailer in dev).

### IQ13. What is the difference between `@Controller` and `@RestController`?
- **`@Controller`** — classic MVC; returns **view names** (templates like Thymeleaf). To return data you'd add `@ResponseBody`.
- **`@RestController`** — `@Controller` + `@ResponseBody` combined; every method returns **data serialized to JSON/XML** (the default for REST APIs).

### IQ14. What is Spring AOP and where have you used it?
- **AOP (Aspect-Oriented Programming)** lets you apply **cross-cutting concerns** (logging, security, transactions, metrics) **without cluttering business code**. You write an **aspect** with **advice** (`@Before`, `@After`, `@Around`) that runs at matching **join points** defined by a **pointcut** expression.
- Spring implements it with **proxies** (JDK dynamic proxies for interfaces, CGLIB for classes).
- **Real uses:** `@Transactional` and Spring Security are themselves AOP; I've used custom aspects for **method-timing metrics** and **audit logging** across services.
- **Gotcha:** because it's proxy-based, **self-invocation** and **private/final methods** aren't advised (same reason `@Transactional` self-calls fail).

### IQ15. How does Spring Boot handle circular dependencies, and how do you avoid them?
- A **circular dependency** is A needs B and B needs A. With **constructor injection**, Spring **can't** build either and fails at startup (which is good — it surfaces the design flaw). Spring Boot 2.6+ **disallows** circular refs by default.
- **Fixes (best first):** **redesign** to remove the cycle (extract a third component holding the shared logic); use **setter/`@Lazy`** injection to break the cycle; or (last resort) `spring.main.allow-circular-references=true`.
- **One-liner:** "Circular deps usually signal a design problem — I refactor to a third collaborator rather than paper over it with `@Lazy`."

