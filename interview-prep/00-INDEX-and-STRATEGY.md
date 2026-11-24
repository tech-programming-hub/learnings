# Genpact Full Stack Engineer Interview — Master Prep Guide

**Interview Date:** 8th Aug | **Mode:** In-office (Genpact)
**Role:** Full Stack Engineer (~7 yrs) — Python/FastAPI + Java/Spring Boot backends, React.js frontend, AWS/Azure, Kafka/RabbitMQ/Azure Service Bus/Event Hub, Microservices, Agentic AI.

---

## 📚 How to Use This Pack

| File | Topic | Priority |
|------|-------|----------|
| `01-java-core.md` | Java 8–21, Collections, Concurrency, JVM | ⭐⭐⭐ |
| `02-spring-boot.md` | Spring Boot, Spring MVC, JPA, Security | ⭐⭐⭐ |
| `03-microservices.md` | Microservices patterns, API design, resilience | ⭐⭐⭐ |
| `04-kafka.md` | Kafka deep dive | ⭐⭐⭐ |
| `05-rabbitmq-azure-servicebus-eventhub.md` | Messaging systems & comparisons | ⭐⭐⭐ |
| `06-python-fastapi.md` | Python + FastAPI | ⭐⭐ |
| `07-react-typescript-frontend.md` | React, TypeScript, frontend | ⭐⭐ |
| `08-databases-sql-nosql.md` | PostgreSQL, MySQL, SQL Server, MongoDB | ⭐⭐ |
| `09-cloud-docker-k8s-cicd-observability.md` | AWS/Azure, Docker, K8s, CI/CD, OpenTelemetry | ⭐⭐ |
| `10-security-auth.md` | OAuth2, OIDC, JWT, SAML, RBAC | ⭐⭐ |
| `11-agentic-ai.md` | Agentic AI, orchestration, MCP, RAG | ⭐⭐ |
| `12-system-design-scenarios.md` | End-to-end design questions | ⭐⭐⭐ |
| `13-hr-behavioral.md` | Behavioral, STAR stories, questions to ask | ⭐⭐ |
| `14-coding-questions-most-asked.md` | Most-asked coding problems + solutions | ⭐⭐⭐ |
| `15-situational-scenario-questions.md` | "What would you do if…" behavioral + technical | ⭐⭐⭐ |
| `16-angular-frontend.md` | Angular (components, DI, RxJS, change detection, forms, routing) | ⭐⭐ |
| `17-real-interview-questions-asked.md` | **Real questions from a live interview** + same-type follow-ups (resilience, Java concurrency, Spring DI, Kafka semantics, Azure Managed Identity, K8s ConfigMap, cloud migration) | ⭐⭐⭐ |

> **Note:** Each topic file (01–13) has **3 layers**: **Part 1** (foundational Q&A), **Part 2** (advanced/tough questions with code), and **Part 3** (extra concepts in plain, easy language — read this first if a topic feels new). Files **14** (coding) and **15** (situational) are dedicated practice sets built from the most frequently asked questions.


---

## 🎯 Interview Strategy

### The night before / morning of
- Skim every file's **bold headers** and code snippets.
- Re-read `12-system-design-scenarios.md` and `13-hr-behavioral.md` fully.
- Prepare 3 project stories mapped to STAR (MGM observability, BMW PQM, AgentPulse).

### During the interview
1. **Anchor answers in your experience.** You have real Kafka + Azure + microservices + AI experience. Say "In my project at BMW we used Kafka + Elasticsearch to…".
2. **Structure = clarity.** For design questions: Requirements → High-level → Data model → APIs → Scaling → Trade-offs.
3. **Say the trade-off.** Senior engineers are judged on *judgement*. Always mention "the trade-off here is…".
4. **When unsure**, reason out loud instead of guessing silently.
5. **Numbers impress.** "Reduced MTTR by 25%", "200+ microservices", "sub-second self-healing".

### Genpact-specific notes
- Genpact is a large IT/BPM services firm — expect **breadth over niche depth**, plus **domain/enterprise integration** flavor.
- They value **delivery ownership, Agile/SAFe, and client communication** — highlight your Technical Lead experience.
- Expect a mix of: 1 coding/DSA round, 1–2 technical (Java + system design), 1 managerial/HR.

---

## ⚡ 60-Second Elevator Pitch (memorize)

> "I'm a Technical Lead with 11+ years building high-concurrency Java/Spring Boot systems and modern full-stack apps. I've designed 100+ microservices with Kafka-based event-driven integration, deployed cloud-native on Azure (AKS, Web Apps, Function Apps) with GitHub Actions CI/CD, and built React/Angular frontends. Recently I've gone deep on AI-native systems — RAG pipelines, MCP integration, and an open-source LLM middleware proxy called AgentPulse on PyPI. I've delivered for MGM, BMW, Air Canada, and Maersk. I own what I build, end to end."

---

## ✅ Quick Self-Check Checklist
- [ ] Can explain Kafka consumer groups, partitions, offsets, rebalancing
- [ ] Can compare Kafka vs RabbitMQ vs Azure Service Bus vs Event Hub
- [ ] Can design an event-driven order system live
- [ ] Can explain Saga, CQRS, Outbox, Circuit Breaker
- [ ] Can write Java streams + concurrency code on whiteboard
- [ ] Can explain Spring Boot auto-config, bean lifecycle, transactions
- [ ] Can explain OAuth2 flows + JWT validation
- [ ] Can compare SQL vs NoSQL and index/partition strategies
- [ ] Can explain K8s pods/deployments/HPA and Docker multi-stage builds
- [ ] Have 3 STAR stories ready
