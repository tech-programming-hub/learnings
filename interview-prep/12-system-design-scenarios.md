# 12 — System Design Scenarios (End-to-End)

> For a 7–11 yr Full Stack role, expect 1–2 design questions. Use a consistent framework and narrate trade-offs. Lean on your event-driven + Azure + microservices experience.

---

## 🧭 The Framework (use for EVERY design question)

1. **Clarify requirements** (functional + non-functional). Ask: scale (users/RPS), read/write ratio, latency, consistency, availability.
2. **Estimate** (back-of-envelope): traffic, storage, bandwidth.
3. **High-level architecture** (draw boxes: client → gateway → services → DB/queue/cache).
4. **API design** (key endpoints/contracts).
5. **Data model** (schema, choice of DB, indexing/partitioning).
6. **Deep dive** on 1–2 components the interviewer cares about.
7. **Scaling & bottlenecks** (caching, sharding, async, CDN, replication).
8. **Reliability** (failover, retries, circuit breakers, DLQ, monitoring).
9. **Trade-offs & alternatives** (say them out loud).

**Non-functional checklist:** Scalability, Availability, Reliability, Latency/Performance, Consistency, Security, Observability, Cost, Maintainability.

---

## Scenario 1: Design an Event-Driven Order Processing System (very likely — matches JD)

**Requirements:** place orders, process payment, reserve inventory, ship, notify. High volume, resilient, eventually consistent.

**Architecture:**
- **API Gateway** → **Order Service** (REST, writes order as `PENDING`).
- Order Service publishes **`OrderPlaced`** event to **Kafka** (via **Outbox pattern** for atomicity).
- **Payment Service** consumes → charges → emits `PaymentCompleted`/`PaymentFailed`.
- **Inventory Service** reserves stock → `InventoryReserved`/`OutOfStock`.
- **Shipping Service** → `Shipped`.
- **Notification Service** → email/SMS.
- Coordinate via **Saga** (choreography via events, or orchestration with an Order orchestrator).

**Key decisions:**
- **Kafka** for high-throughput, replayable, decoupled events; partition by `orderId` for per-order ordering.
- **Saga + compensating transactions** (refund on failure) since no distributed ACID.
- **Idempotent consumers** (dedup by event id) — Kafka is at-least-once.
- **Outbox** to avoid dual-write inconsistency.
- **DLQ** for poison messages; retries with backoff.
- **CQRS** for an order status read model (fast queries).
- **Database-per-service** (Postgres for orders/payments).
- Observability: OpenTelemetry tracing across services, consumer lag alerts.

**Trade-offs:** eventual consistency (order "processing" state) vs simplicity; choreography (decoupled, harder to trace) vs orchestration (clear, single coordinator).

---

## Scenario 2: Design a URL Shortener (classic)

**Requirements:** shorten URL, redirect, analytics; read-heavy (100:1).

**Design:**
- **Encode:** base62 of an auto-increment id, or hash (MD5) + collision check. 7 chars → 62^7 ≈ 3.5T URLs.
- **API:** `POST /shorten {url}` → short code; `GET /{code}` → 301/302 redirect.
- **Storage:** key-value (short→long) — Redis cache + durable store (Cassandra/DynamoDB/Postgres). Read-heavy → **cache aggressively**.
- **Scale:** CDN + cache for redirects; DB sharding by code; async analytics via Kafka.
- **Trade-off:** 301 (cached by browser, fewer hits but no analytics) vs 302 (every hit counts).

---

## Scenario 3: Design a Real-Time Monitoring/Observability Dashboard (YOUR domain — MGM)

**Requirements:** ingest metrics/logs from 200+ microservices, live dashboards, alerting.

**Design:**
- Services expose metrics (Micrometer) → **Prometheus** scrapes; logs → **Loki**; traces → **OpenTelemetry → Tempo**.
- **Ingestion buffer:** Kafka/Event Hubs for high-volume telemetry.
- **Storage:** time-series DB (Prometheus/Mimir) for metrics; object store for logs.
- **Frontend:** React dashboard, **WebSocket/SSE** for live updates, virtualized lists, memoized charts.
- **Alerting:** Alertmanager → routing; **RAG-driven summarization** for root-cause context (your innovation).
- **Scale:** downsampling/retention tiers, sharded scraping, aggregation.
- **Trade-off:** pull (Prometheus) vs push (for short-lived jobs → pushgateway/OTel).

---

## Scenario 4: Design a Scalable Chat/Notification System

**Design:**
- **WebSocket** gateway for real-time; fallback to SSE/long-poll.
- **Message broker** (Kafka) for fan-out; **Redis pub/sub** for presence.
- Store messages (Cassandra — write-heavy, time-ordered).
- Delivery: at-least-once + client dedup; read receipts.
- **Notification service** consumes events → push/email/SMS (RabbitMQ/Service Bus for reliable per-message delivery).
- Scale via horizontal WebSocket servers + sticky sessions / connection registry.

---

## Scenario 5: Design a Rate Limiter

**Algorithms:**
- **Token bucket** (allows bursts) — most common.
- **Leaky bucket** (smooths rate).
- **Fixed window** (simple, boundary spikes) / **sliding window log/counter** (accurate).
**Design:** Redis (atomic INCR + TTL / Lua script) for distributed counting, at the API Gateway. Return `429` + `Retry-After`. Per-user/API-key/IP.

---

## Scenario 6: Design an E-commerce Product Catalog + Search

**Design:**
- **Product Service** (Postgres for source of truth) + **Elasticsearch** for search/faceting (you used ES at BMW).
- Sync DB → ES via **CDC (Debezium) → Kafka → ES sink** (Kafka Connect).
- **Cache** hot products (Redis, cache-aside).
- **CDN** for images.
- Pagination, filters, autocomplete (ES completion suggester).
- **Trade-off:** eventual consistency between DB and search index.

---

## Scenario 7: Design a File Upload / Storage Service

**Design:**
- Pre-signed URLs → client uploads directly to **object storage** (S3/Blob) — offload from app servers.
- Metadata in DB. Async processing (thumbnails/virus scan) via queue.
- CDN for delivery, chunked/multipart upload for large files, resumable uploads.

---

## Scenario 8: Add an AI Assistant / RAG to an Enterprise App (matches JD Agentic AI)

**Design:**
- Ingest docs → chunk → embed → **vector DB (pgvector)**.
- Query → retrieve top-k (hybrid + re-rank) → augment prompt → LLM → cited answer.
- **Agent layer** with tools (search internal APIs, DB queries) via **MCP**, orchestrated with LangGraph.
- **Guardrails**, structured outputs, caching, observability (token/cost/trace).
- Auth: OAuth2 + RBAC on tools; audit logging; PII redaction.
- **Trade-off:** RAG (fresh, grounded) vs fine-tuning (behavior/style); cost vs latency via model routing.

---

## 💡 Reusable Building Blocks (mention where relevant)
- **Caching:** Redis (cache-aside), CDN for static.
- **Async:** Kafka/RabbitMQ/Service Bus to decouple + absorb spikes.
- **DB scaling:** read replicas → partitioning → sharding; right DB per need (SQL vs NoSQL).
- **Resilience:** circuit breaker, retry+backoff, bulkhead, timeout, DLQ, idempotency.
- **Consistency:** Saga, Outbox, CQRS, event sourcing, idempotency keys.
- **Gateway:** auth, rate limit, routing, aggregation.
- **Observability:** metrics/logs/traces (RED/USE), alerting, correlation IDs.
- **Scaling compute:** stateless services + HPA on K8s + load balancer.

---

## 🗣️ How to narrate (sample opening)
> "Let me first clarify the requirements and scale. Assuming ~X RPS, read-heavy, needing high availability and eventual consistency... I'll start with a high-level design, then deep-dive into the data model and the event flow, and call out trade-offs as I go."

## ⚠️ Common mistakes to avoid
- Jumping to a solution without clarifying requirements/scale.
- No mention of trade-offs.
- Ignoring failure handling & observability.
- Over-engineering (adding Kafka/microservices when a monolith suffices) — mention "start simple, scale when needed."
- Forgetting security (auth, secrets, encryption).

---
---

# PART 2 — Advanced Deep-Dives, Estimation & Tougher Scenarios

## 🔢 Back-of-envelope estimation cheat sheet (say numbers out loud)
- **1 day ≈ 86,400 s ≈ 10^5 s.** So **1M/day ≈ ~12/s**; **100M/day ≈ ~1,200/s** average (×2–3 for peak).
- **Latency ladder:** memory ns → SSD ~100µs → **network round-trip ~0.5ms (same DC)** → cross-region ~50–150ms.
- **Storage:** 1M rows × 1KB = 1GB/day → ~365GB/yr (×replication). Plan retention + tiering.
- **QPS → servers:** if one instance does ~1k rps and peak is 12k rps → ~12–15 instances + headroom.
Always state assumptions: "Assume 10M DAU, 100M writes/day → ~1.2k writes/s avg, ~5k peak; read:write 100:1 → ~500k reads/s → cache + replicas."

## Deep-Dive 1 — Event-Driven Order System: the FULL failure analysis (they'll drill this)
Beyond the happy path, be ready for:
- **Atomic publish:** DB write + event publish → **Outbox + CDC (Debezium)** (no dual-write loss).
- **Duplicate delivery:** consumers **idempotent** (dedup by `eventId`), because Kafka is at-least-once.
- **Ordering:** partition by `orderId` so all events for an order are ordered.
- **Payment fails after inventory reserved:** **Saga compensation** → release inventory, cancel order.
- **Poison message:** retries + backoff → **DLT**; alert + replay after fix.
- **Consumer down:** Kafka retains events; consumer resumes from committed offset (no loss).
- **Read side:** **CQRS** — a materialized `order_status` view for fast queries.
- **Observability:** trace the order across services (OTel), alert on consumer lag.
- **Trade-off statement:** "I accept eventual consistency for availability/scale, and make it safe with idempotency + sagas + the outbox."

## Deep-Dive 2 — Design a payment system (consistency-critical, tougher)
Here consistency > availability for the money movement.
- **Idempotency keys** on every charge (client-supplied) → no double charge on retries.
- **Ledger** as append-only double-entry (debit+credit rows) → auditable, never mutate balances.
- **Exactly-once effect** via idempotency + dedup, not by trusting the network.
- **Reconciliation** jobs against the payment provider; **DLQ** for failed webhooks.
- **State machine** for payment status (PENDING→AUTHORIZED→CAPTURED→SETTLED/REFUNDED).
- **Strong consistency** DB (Postgres) with row locks / optimistic versioning for balance-affecting ops.
- **PCI scope minimization** — tokenize cards, never store PAN. Encrypt + audit everything.

## Deep-Dive 3 — Design a news feed / timeline (fan-out problem, classic hard one)
- **Fan-out on write (push):** precompute each follower's feed on post → fast reads, expensive writes; bad for celebrities (millions of followers).
- **Fan-out on read (pull):** build feed at read time from followees → cheap writes, slow reads.
- **Hybrid (real answer):** push for normal users, **pull for celebrities** (merge at read). Cache feeds in Redis, store posts in a wide-column store, rank with a scoring service. State the trade-off explicitly — this is what they're testing.

## Deep-Dive 4 — Design a distributed rate limiter (correctness under concurrency)
- **Algorithm:** token bucket (allows bursts) implemented in **Redis** with an atomic **Lua script** (read tokens, refill by elapsed time, decrement) → avoids race conditions across many app servers.
- **Where:** at the API gateway; keys per user/API-key/IP.
- **Distributed correctness:** single Redis (or Redis cluster with hash-tagged keys) as the source of truth; handle Redis outage with a **fail-open vs fail-closed** decision (state the trade-off).
- Return `429 + Retry-After`. For global multi-region, consider approximate local counters + periodic sync.

## Deep-Dive 5 — Design a URL shortener at scale (the follow-ups)
- **Key generation without collisions/coordination:** base62 over a globally unique id — use a **counter/ticket server** (or Snowflake-style ID: timestamp+machine+seq) instead of random+check (which needs a read per write).
- **Read scaling (100:1):** Redis cache + CDN in front of redirects; DB is mostly for writes + cache misses.
- **Custom aliases:** unique constraint check.
- **Analytics:** don't block the redirect — emit a click event to **Kafka**, process async.
- **301 vs 302:** 301 is cached by browsers (fewer hits, faster, but you lose click analytics); 302 counts every click.

## Deep-Dive 6 — Design a real-time observability platform (YOUR wheelhouse — go deep)
- **Ingest** at high volume → buffer in **Kafka/Event Hubs** (absorb spikes, decouple).
- **Metrics** → Prometheus/Mimir (downsampling + retention tiers); **logs** → Loki; **traces** → Tempo (all via **OpenTelemetry**).
- **Cardinality control** — the hidden killer: limit label cardinality, sample high-volume traces (tail-based).
- **Query/serving** → Grafana dashboards; **WebSocket/SSE** to a React UI for live tiles + virtualized log views.
- **Alerting** → Alertmanager; **RAG summarization** of alerts for root-cause context (your innovation → 25% MTTR cut).
- **Scale** — shard scraping, federate Prometheus, object storage for long-term.
Narrate this as your MGM project — it's a huge credibility win.

## Deep-Dive 7 — Add an enterprise AI assistant (matches the JD's Agentic AI)
- Docs → chunk → embed → **pgvector**; query → **hybrid retrieve + re-rank** → grounded LLM answer with citations.
- **Agent layer** with tools via **MCP** (search internal APIs, run reports), orchestrated with **LangGraph**.
- **Security:** OAuth2 + **RBAC on tools**, only retrieve docs the user may see, audit logs, PII redaction, prompt-injection defenses, **human-in-the-loop** for actions.
- **Reliability/cost:** structured outputs + schema validation (AgentPulse-style self-healing), semantic cache, model routing, token/cost/trace observability.

## 🧠 Deep component knowledge to drop in any design
- **Consistent hashing** — distribute keys across nodes with minimal reshuffling when nodes change (used in sharding, caches, Cassandra). Virtual nodes for even distribution.
- **Bloom filter** — probabilistic "definitely not present / maybe present" → avoid expensive lookups (e.g., "is this URL taken?", DB read avoidance).
- **CDC (Debezium)** — stream DB changes to Kafka → sync search indexes/read models/outbox.
- **CQRS + materialized views** — separate optimized read models from the write model.
- **CAP/PACELC** — under partition choose C or A; else (normally) choose latency or consistency.
- **Idempotency + Outbox + Saga** — the trio for reliable event-driven systems.
- **Caching layers** — client → CDN → API cache → app (local) → distributed (Redis) → DB. Know invalidation + stampede protection.
- **WebSocket vs SSE vs long-poll** — bidirectional vs server-push one-way vs fallback.

## 🗣️ Two power phrases to repeat in every design
1. "Let me state my assumptions and do a rough capacity estimate first."
2. "The trade-off here is X vs Y; given the requirements I'd choose ___ because ___."

## ⚠️ Senior-level differentiators (what gets you the offer)
- You **quantify** (QPS, storage, latency), not just draw boxes.
- You **name failure modes** and handle them (retries, DLQ, idempotency, circuit breakers).
- You discuss **data consistency** explicitly (strong vs eventual, and why).
- You **don't over-engineer** — "I'd start with a modular monolith + Postgres, and extract services + Kafka when scale/teams demand it."
- You bring **observability + security** into the design unprompted.

---
---

# PART 3 — More Real Interview Questions (Easy Language, No Repeats)

## Q1. What is scalability, in plain words?
The ability of a system to **handle more load** (more users, requests, data) by adding resources — without slowing down or breaking. A scalable design lets you grow from 100 users to 1 million by adding servers, not by rewriting everything.

## Q2. What is the difference between latency and throughput?
- **Latency** — how long **one** request takes (e.g., 200ms). "How fast?"
- **Throughput** — how many requests you handle **per second** (e.g., 5,000 req/s). "How many?"
You often optimize both, and sometimes trade one for the other (batching improves throughput but adds latency).

## Q3. What is high availability (HA)?
Designing so the system **keeps working even when parts fail** — usually expressed as "nines" (99.9% = ~8.7 hours downtime/year; 99.99% = ~52 min/year). Achieved with redundancy (multiple servers), load balancing, health checks, failover, and no single point of failure.

## Q4. What is a single point of failure (SPOF) and how do you remove it?
Any one component whose failure takes down the whole system (e.g., a single database or server). Remove it with **redundancy** — multiple instances behind a load balancer, database replicas with failover, multi-zone deployment. If any one dies, another takes over.

## Q5. What is caching and where can you add it?
Storing frequently-used data in a fast location so you don't recompute/re-fetch it. Layers: **browser cache**, **CDN** (static files near users), **API/application cache** (Redis), and **database query cache**. Caching is the #1 cheapest way to improve performance and reduce load — but you must handle **invalidation** (keeping it fresh).

## Q6. What is a CDN and when do you use it?
A **Content Delivery Network** is a network of servers spread across the world that cache your static content (images, CSS, JS, videos) close to users. So a user in India gets files from a nearby server instead of your origin in the US — much faster. Use it for any static/global content.

## Q7. What is a load balancer's role in a scalable design?
It sits in front of multiple server instances and **distributes incoming traffic** among them (round-robin, least-connections, etc.), checks their health, and stops sending traffic to unhealthy ones. This enables horizontal scaling and high availability.

## Q8. How do you design a system to handle a sudden traffic spike (e.g., a sale)?
- **Autoscaling** — add instances automatically as load rises.
- **Caching + CDN** — serve most reads without hitting the backend.
- **Queues** (Kafka/SQS) — absorb bursts of writes and process them steadily (buffer).
- **Rate limiting** — protect the system from overload.
- **Load testing** beforehand to know your limits.

## Q9. What is database read/write splitting?
Send **writes** to the primary database and **reads** to one or more **read replicas**. Since most apps read far more than they write, this spreads the load and scales reads. Trade-off: replicas can lag slightly behind (eventual consistency for reads).

## Q10. What is sharding, explained simply?
Splitting your data across **multiple databases** so no single one holds everything. Example: users A–M on DB1, N–Z on DB2 (by a "shard key"). It lets you scale beyond one machine's limits. Downside: queries across shards and rebalancing get complex — use it only when a single DB truly can't cope.

## Q11. How would you design a simple notification system (email/SMS/push)?
- An app publishes a "notify" **event** to a queue (Kafka/Service Bus).
- A **Notification service** consumes it, picks the channel (email/SMS/push), and calls the provider (SendGrid/Twilio).
- Use **retries + DLQ** for failures, **templates** for content, and **idempotency** so users don't get duplicate messages.
- Track delivery status. Decoupling via a queue means the main app isn't slowed by sending notifications.

## Q12. How would you design a URL shortener (beginner-friendly walkthrough)?
1. User submits a long URL → generate a short unique code (e.g., base62 of an ID).
2. Store `code → long_url` in a database.
3. When someone visits the short URL, look up the code and **redirect** to the long URL.
4. Add a **cache** (Redis) since reads vastly outnumber writes, and a **CDN**. Optionally track click analytics asynchronously.

## Q13. What does "stateless vs stateful" mean for scaling?
- **Stateless** — the server keeps no memory between requests; any server can handle any request. Easy to scale (just add more).
- **Stateful** — the server remembers session/data in memory, so requests must go to the same server (sticky sessions), which is harder to scale.
Best practice: keep services **stateless** and store state in a shared DB/Redis.

## Q14. What is eventual consistency, with a relatable example?
When you post on social media, your friend might see it a second or two later, not instantly — because the data spreads across many servers. That short delay is **eventual consistency**: everyone agrees eventually, not immediately. It's a trade-off for scalability and availability.

## Q15. What is the difference between SQL and NoSQL in a system-design context?
Use **SQL** when you need strong consistency, relationships, and transactions (orders, payments). Use **NoSQL** when you need massive scale, flexible schemas, or a specific access pattern (product catalog, sessions, feeds, IoT). Big systems often use **both** — the right tool for each part ("polyglot persistence").

## Q16. How do you approach a system design question step by step (interview method)?
1. **Ask clarifying questions** (scale, features, read/write ratio).
2. **Estimate** rough numbers (users, requests/sec, storage).
3. **Draw the high-level design** (client → load balancer → services → DB/cache/queue).
4. **Detail the data model + APIs.**
5. **Address scaling** (caching, replicas, sharding, queues).
6. **Handle failures** (redundancy, retries, monitoring).
7. **State trade-offs.** Talk out loud throughout.

## Q17. Why do we use message queues in a system design (one clear reason)?
To **decouple** and **buffer**. The producer drops work in the queue and moves on; the consumer processes at its own pace. This absorbs traffic spikes, prevents one slow component from blocking others, and lets you scale producers and consumers independently.

## Q18. What is an API Gateway's role in a big system (recap simply)?
It's the **single front door** for all client requests. It routes them to the right microservice, and handles cross-cutting concerns once — authentication, rate limiting, logging, and SSL — so each service doesn't have to. Simplifies clients and centralizes security.

## Q19. How do you make a system observable (design perspective)?
Build in from the start: **structured logs** with a correlation ID, **metrics** (request rate, errors, latency) exposed for Prometheus/Grafana, and **distributed tracing** (OpenTelemetry) to follow a request across services. Add **alerts** on key metrics. You can't operate what you can't see. (Your MGM specialty.)

## Q20. What's a good answer to "how would you improve the performance of a slow web app"?
Work outside-in: 1) **CDN + browser caching** for static assets, 2) **cache** expensive API/DB results (Redis), 3) **optimize slow database queries** (indexes, avoid N+1), 4) **add read replicas / scale horizontally**, 5) **async** heavy work via queues, 6) **compress + paginate** responses, 7) measure with profiling/APM to find the real bottleneck first (don't guess).

## Q21. What is a "back-of-the-envelope" estimate and why do interviewers want it?
A quick rough calculation of scale — e.g., "1 million requests/day ≈ ~12 per second average, maybe ~30–50 at peak." It shows you can reason about whether you need one server or a hundred, and it guides your design choices. Always state your assumptions out loud.

## Q22. What common mistakes should you avoid in a system design interview?
- Jumping into details before **clarifying requirements**.
- Not mentioning **trade-offs** (there's rarely one perfect answer).
- **Over-engineering** (adding Kafka/microservices/sharding when a simple app would do) — say "start simple, scale when needed."
- Forgetting **failure handling, security, and monitoring**.
- Going silent — **think out loud** so the interviewer follows your reasoning.



