# 15 — Situational / Scenario-Based Questions (Behavioral + Technical)

> "What would you do if…" questions test judgement, ownership, and communication. For **behavioral** ones use **STAR** (Situation, Task, Action, Result). For **technical** ones, state your **approach/steps + trade-offs**. Answers below are tailored to your experience (MGM, BMW, AgentPulse) — adapt the details.

---

## PART A — Behavioral Situational (STAR)

### S1. "Tell me about a time you missed a deadline. What happened?"
**S:** A dependency team delivered an API late, threatening our sprint commitment.
**T:** Still deliver as much value as possible and keep stakeholders informed.
**A:** I flagged the risk **early** (not at the deadline), re-scoped to ship the independent parts behind a feature flag, mocked the pending API for testing, and set a clear revised date once the dependency landed.
**R:** We delivered 80% on time and the rest two days later with zero surprises. **Lesson: communicate risk early and de-scope smartly rather than silently slip.**

### S2. "Describe a time you had a conflict with a coworker."
**S:** A teammate and I disagreed on sync REST vs event-driven for a new flow.
**T:** Reach the best technical decision without damaging the relationship.
**A:** I proposed we each list pros/cons, ran a quick spike to test failure behavior under load, and let the data decide. We chose async with a phased rollout.
**R:** We shipped a resilient design that later absorbed a 3x spike, and our working relationship stayed strong. **I make it about the problem and data, not egos.**

### S3. "Tell me about a time you took ownership of something outside your role."
**S:** On-call engineers at MGM kept struggling to find root causes; it wasn't officially "my" problem.
**T:** Reduce resolution time for the whole org.
**A:** I built a **reusable observability common module** (OpenTelemetry) and RAG-driven alert summarization so any service could onboard easily.
**R:** **MTTR dropped 25%, boilerplate 40%.** I saw a systemic problem and turned it into a platform capability.

### S4. "Give an example of handling an unhappy client/stakeholder."
**S:** A client was frustrated about slow defect-resolution visibility on the BMW PQM app.
**T:** Rebuild trust and improve transparency.
**A:** I listened to their actual pain, then delivered Angular dashboards with real-time (Kafka + Elasticsearch) defect visualization and gave weekly progress demos.
**R:** Transparency improved decision speed and the client relationship recovered. **Listen first, then show progress.**

### S5. "Tell me about a time you failed."
**S:** Early in my career I over-engineered a solution that took too long and was hard to maintain.
**T:** Deliver value faster.
**A:** I owned it, refactored to a simpler design, and adopted a "ship an MVP first, iterate" mindset with better tests.
**R:** Faster delivery and fewer bugs. **I now consciously avoid over-engineering** — start simple, scale when needed.

### S6. "Describe a time you had to convince others to adopt your idea."
**S:** I wanted the team to adopt MCP servers to standardize AI tooling.
**T:** Get buy-in from engineers used to bespoke integrations.
**A:** I built a working prototype showing 40% less boilerplate and a pluggable provider layer, then demoed the developer-experience win.
**R:** The team adopted it. **I persuade with a working proof, not just slides.**

### S7. "How did you handle a high-pressure production incident?"
**S:** A Kafka consumer's lag spiked and orders stalled in production.
**T:** Restore service fast and prevent recurrence.
**A:** I used the Grafana lag dashboard + OpenTelemetry trace to find a slow DB call (missing index), scaled consumers as a short-term fix, added the index + batching as the root fix, and added a lag alert.
**R:** Service restored quickly; added monitoring so we'd catch it earlier next time.

### S8. "Tell me about a time you mentored someone."
**S:** A junior engineer was struggling with code quality and confidence.
**T:** Help them grow.
**A:** I paired with them, gave small ownable tasks, did constructive reviews explaining the "why," and gradually increased their scope.
**R:** They became a confident, independent contributor. **I lead by growing others.**

### S9. "Describe adapting to a big change (new tech/process/team)."
**S:** The org needed AI-native capabilities I hadn't used before.
**T:** Get productive fast.
**A:** I self-taught RAG/MCP/LLM orchestration by building — shipped AgentPulse on PyPI and MCP tools.
**R:** Delivered real AI infrastructure quickly. **I adapt by building, not just reading.**

### S10. "Tell me about balancing quality vs speed."
Answer with judgement: "I ask what kind of work it is. For a throwaway prototype, speed wins. For core production systems (payments, data), quality wins — I never cut corners on correctness/security, but I *can* cut scope. I ship an MVP with solid fundamentals (tests, observability) and iterate, rather than gold-plating upfront."

---

## PART B — Technical Situational ("What would you do if…")

### S11. "The application is suddenly slow in production. How do you investigate?"
1. **Check dashboards** (Grafana): is it CPU, memory, DB, or a specific service? (metrics first).
2. **Look at a distributed trace** (OpenTelemetry) for a slow request → find the slow span (DB call? external API?).
3. **Check logs** (same trace/correlation ID) for errors.
4. Common culprits: a **slow DB query** (missing index — run EXPLAIN), **connection pool exhaustion**, **GC pauses**, a downstream dependency, **Kafka consumer lag**, or a recent deploy.
5. **Short-term:** scale out / roll back the bad deploy / add a cache. **Long-term:** fix the root cause + add an alert. **Measure, don't guess.**

### S12. "A user reports data is wrong/missing. How do you handle it?"
1. **Reproduce** with the user's exact input/ID; get the correlation ID.
2. **Trace** the request path; check each service + the database.
3. Determine if it's a **bug**, a **race condition**, **eventual consistency lag**, or **bad input/validation**.
4. **Mitigate** (correct the data if safe, communicate to the user), then **fix the root cause** and add a test so it can't recur. Keep the user informed throughout.

### S13. "Two services need each other's data. How do you design it to avoid tight coupling?"
Prefer **asynchronous events** over synchronous calls: service A publishes events; service B keeps a local read model (CQRS) updated from those events. If a synchronous read is truly needed, use a well-defined API + **circuit breaker + timeout + cache**. Avoid a shared database. This keeps them independently deployable and resilient.

### S14. "A downstream service you depend on is unreliable. What do you do?"
Apply **resilience patterns**: **timeouts** (never wait forever), **retries with backoff + jitter** (for transient failures), a **circuit breaker** (fail fast when it's down, return a fallback), a **bulkhead** (isolate its thread pool), and **graceful degradation** (serve cached/partial data). Also add monitoring/alerts and, if possible, make the interaction async so their outage doesn't block you.

### S15. "How would you deploy a change with zero downtime?"
Use a **rolling update** (K8s) or **blue-green/canary**: bring up new instances, gate traffic with **readiness probes**, drain old ones gracefully (SIGTERM + preStop). For **DB changes**, use the **expand-contract** pattern (add new column, dual-write, migrate, switch reads, drop old) so old and new code both work during rollout. Keep a **rollback** path. Feature flags let you decouple deploy from release.

### S16. "You need to add a new column to a huge table in production. How?"
Never a blocking `ALTER` on a giant table at peak. Use **expand-contract**: add the column as **nullable** (fast), **backfill in batches** (off-peak), have the app dual-write, then switch reads, and finally enforce constraints. Use a migration tool (Flyway/Liquibase). On Postgres, be careful with rewrites; add indexes **concurrently**.

### S17. "How do you ensure a payment isn't charged twice if the network retries?"
**Idempotency:** the client sends an **Idempotency-Key**; the server checks if that key was already processed and returns the previous result instead of charging again. Combine with an append-only **ledger**, unique constraints, and dedup on event consumers. Never rely on the network being reliable.

### S18. "How would you handle sensitive data (passwords, PII) in your system?"
- Passwords: **hash + salt** (bcrypt/Argon2), never store plaintext.
- PII: **encrypt at rest** (KMS/Key Vault) and **in transit** (TLS), mask/redact in logs, restrict access (least privilege + RBAC), and follow data-retention/compliance rules.
- Secrets: in a **vault**, not code. Audit access.

### S19. "The database is becoming a bottleneck. How do you scale it?"
Step-wise: 1) **optimize queries + add indexes** (cheapest), 2) add a **cache** (Redis) for hot reads, 3) add **read replicas** and route reads there, 4) **partition** large tables, 5) **shard** as a last resort, and 6) consider **CQRS** (separate read model). Also connection pooling. Do the cheap wins first.

### S20. "You're asked to design a feature but requirements are unclear. What do you do?"
Don't guess in silence: **ask targeted clarifying questions** (who's it for, scale, must-haves vs nice-to-haves, edge cases), make **reasonable documented assumptions**, and if needed build a **small prototype** to make it concrete and get fast feedback. I'd rather validate direction early than build the wrong thing perfectly.

### S21. "A teammate's pull request has a design flaw. How do you give feedback?"
Be **kind, specific, and about the code, not the person**. Ask questions ("what happens if X is null here?") rather than commands, explain the **why**, suggest an alternative, and acknowledge the good parts. For a bigger design concern, discuss it directly (call/pairing) instead of a wall of PR comments. Goal: better code + a teammate who feels respected.

### S22. "How would you handle a request to cut testing to meet a deadline?"
I'd push back constructively: explain the **risk** (bugs, incidents, slower future delivery), and propose a middle path — **prioritize tests on the highest-risk/critical paths**, cut **scope** instead of quality, or add a fast-follow. If the business truly accepts the risk for a genuine emergency, I'd document the decision and add the tests right after. I don't silently skip quality on core systems.

### S23. "Your service must handle a 10x traffic spike next week (a sale). How do you prepare?"
1. **Load test** to find current limits.
2. **Autoscaling** (HPA + cluster autoscaler) with headroom.
3. **Cache aggressively** (Redis + CDN) to offload reads.
4. **Queue** writes (Kafka/Service Bus) to absorb bursts and process steadily.
5. **Rate limiting + graceful degradation** to protect core flows.
6. **Circuit breakers** on dependencies, and a **runbook + war room** for the day. Monitor dashboards live.

### S24. "How do you decide between a monolith and microservices for a new project?"
Start **monolith-first** unless there's a clear reason not to — it's simpler, faster to build, and easier to change early. Move to microservices when you have **clear bounded contexts, large teams needing independent deployment, or parts needing independent scaling**. Don't add distributed-system complexity before you need it.

### S25. "You inherit a legacy system with no tests and must add a feature. How?"
1. **Understand** the area you're touching (read code, add logging/tracing).
2. Write **characterization tests** around the existing behavior first (a safety net).
3. Make the change in **small, reversible steps**.
4. Refactor cautiously (Strangler Fig if larger).
5. Add monitoring and deploy behind a **feature flag** so you can roll back fast. Never do a big-bang rewrite.

### S26. "How would you handle a security vulnerability found in a dependency?"
Assess **severity + exploitability** (is it in a used code path? internet-facing?). If critical, **patch/upgrade immediately** (or apply a mitigation), deploy through the pipeline, and verify. Add **dependency scanning** (Snyk/Dependabot/Trivy) to CI so these are caught automatically going forward. Communicate to stakeholders if data was at risk.

### S27. "A microservice keeps running out of memory (OOM) in Kubernetes. What do you do?"
1. `kubectl describe pod` → confirm OOMKilled; check memory **limits**.
2. Look at metrics/heap usage over time — is it a **leak** (grows forever) or just **under-provisioned**?
3. If under-provisioned → raise the memory **request/limit**.
4. If a leak → take a **heap dump**, analyze (MAT) for the retained objects (often an unbounded cache or ThreadLocal), and fix the code.
5. Add memory alerts. Right-size from real data.

### S28. "How do you keep two data stores (e.g., DB and search index) in sync?"
Use **Change Data Capture (Debezium) → Kafka → sink connector** to stream DB changes into the search index (Elasticsearch), or the **Outbox pattern** so updates are reliably published. Accept **eventual consistency** between them, make consumers **idempotent**, and monitor lag. This is exactly the DB→ES sync pattern (you used ES at BMW).

---

## 🧭 Templates to structure any situational answer
- **Behavioral (STAR):** "The situation was… my task was… I did… the result was… and I learned…"
- **Technical ("what if"):** "First I'd clarify/reproduce… then investigate using [tools]… the likely causes are [A/B/C]… I'd mitigate with [short-term] and fix root cause with [long-term]… and add [monitoring/tests] to prevent recurrence. The trade-off is…"
- **Golden rules:** communicate early, own the outcome, use data, state trade-offs, and always mention how you'd **prevent it recurring** (tests/monitoring/process).
