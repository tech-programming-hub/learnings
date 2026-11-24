# 09 — Cloud (AWS/Azure), Docker, Kubernetes, CI/CD, Observability

> Anchor: You deployed Spring Boot on Azure (Web Apps, Function Apps, AKS) with GitHub Actions, built Grafana/Prometheus/OpenTelemetry observability. This is a strong area — tell stories.

---

## A. Containers & Docker

### Q1. What is Docker? Container vs VM?
Docker is a platform that **packages an application together with all its dependencies** (libraries, runtime, config) into a single, portable unit called a **container** that runs identically anywhere. The key distinction from a VM is *what gets virtualized*:
- **Container** — **shares the host operating system's kernel** and isolates just the application's process and filesystem. This makes it **lightweight** (megabytes), **fast to start** (seconds or less), and dense (many per host).
- **VM (Virtual Machine)** — runs a **full guest operating system** on top of a hypervisor, which makes it **heavy** (gigabytes), **slow to boot**, and resource-hungry, but gives **stronger isolation** (its own kernel).
The benefits of containers: **consistency** (it solves "it works on my machine" because the container carries its environment with it), **isolation** (apps don't interfere), **density** (more apps per server), and **fast deployment**. The trade-off vs VMs is slightly weaker isolation since containers share the kernel.

### Q2. Image vs container?
This is the "class vs object" distinction of Docker:
- **Image** — an **immutable, read-only template** built from a Dockerfile. It's made of stacked **layers** (each instruction adds a layer) and contains everything needed to run the app. It's the blueprint you build once and store in a registry.
- **Container** — a **running (or stopped) instance of an image**. When you `docker run` an image, Docker adds a thin writable layer on top and starts the process. You can run **many containers from the same image**, each isolated.
Analogy: the image is the recipe (or class); the container is the cooked dish (or object instance).

### Q3. Key Dockerfile instructions?
A Dockerfile is the script that defines how to build an image, step by step. The key instructions:
- **`FROM`** — the base image to start from (e.g., `eclipse-temurin:21-jre`).
- **`WORKDIR`** — sets the working directory for subsequent commands.
- **`COPY`** — copies files from your build context into the image.
- **`RUN`** — executes a command at **build time** (e.g., install dependencies, compile) — each `RUN` creates a new layer.
- **`ENV`** — sets environment variables.
- **`EXPOSE`** — documents which port the container listens on.
- **`ENTRYPOINT`** — the fixed executable to run when the container starts.
- **`CMD`** — default arguments (overridable at run time).
The critical performance concept is **layer caching**: Docker caches each layer and reuses it if nothing changed, so **instruction order matters** — put rarely-changing things (like dependency installation) early and frequently-changing things (like your source code) **last**, so a code change doesn't invalidate the cached dependency layers and force a slow full rebuild.


### Q4. What is a multi-stage build and why?
A multi-stage build uses **multiple `FROM` stages in one Dockerfile**: an early "build" stage that contains all the heavy build tooling (JDK, Maven, compilers, dev dependencies), and a final "runtime" stage that starts from a **slim base** and **copies only the finished artifact** (the jar) from the build stage. The reason this matters: your build tools (JDK + Maven + the whole `.m2` cache) are huge and are **not needed at runtime** — shipping them would bloat the image and expand the attack surface. By copying just the compiled jar into a lean JRE image, you get a **much smaller, faster-to-pull, more secure** final image (fewer packages = fewer CVEs). The example below builds with `maven:...-temurin-21` and then ships only `app.jar` on a slim `jre-alpine` base.
```dockerfile
FROM maven:3.9-eclipse-temurin-21 AS build
WORKDIR /app
COPY . .
RUN mvn -q clean package -DskipTests


FROM eclipse-temurin:21-jre-alpine
WORKDIR /app
COPY --from=build /app/target/app.jar app.jar
EXPOSE 8080
ENTRYPOINT ["java","-jar","app.jar"]
```

### Q5. Docker image optimization best practices?
The goals are **smaller images** (faster pulls/deploys) and a **smaller attack surface** (fewer CVEs). The key practices:
- **Use small base images** — `alpine` or **distroless** (which contain only your app and its runtime, no shell/package manager) instead of full OS images.
- **Multi-stage builds** — ship only the runtime artifact, not the build tools (see Q4).
- **Minimize and order layers** — combine related `RUN` commands, and put frequently-changing content last so caching works.
- **Use a `.dockerignore`** — keep unneeded files (`.git`, `target`, `node_modules`) out of the build context so builds are faster and images leaner.
- **Don't run as root** — create and switch to a non-root user to limit blast radius if the container is compromised.
- **Pin versions** — pin base image and dependency versions for reproducible, predictable builds.
- **Cache dependencies separately** — copy the dependency manifest (`pom.xml`/`package.json`) and download deps *before* copying source, so a code change doesn't re-download everything.
- **Scan images** (Trivy/Snyk) for vulnerabilities as part of CI.

### Q6. ENTRYPOINT vs CMD?
Both define what runs when a container starts, but they play different roles and are often used **together**:
- **`ENTRYPOINT`** — defines the **fixed executable** — the thing the container is fundamentally meant to run (e.g., `java -jar app.jar`). It's not easily overridden by arguments at `docker run`.
- **`CMD`** — provides **default arguments** (or a default command) that are **easily overridden** when you run the container.
The common pattern is `ENTRYPOINT ["java","-jar","app.jar"]` with `CMD ["--spring.profiles.active=prod"]` — the entrypoint is the app, and CMD supplies default args you can override at runtime (`docker run image --spring.profiles.active=dev`). If you only use `CMD` alone, the whole thing is overridable; if you only use `ENTRYPOINT`, there are no default args.

### Q7. Docker networking & volumes?
These cover **how containers communicate** and **how they persist data**:
- **Networks** — Docker gives containers virtual networks. **Bridge** (the default) isolates containers on the host but lets them talk to each other; on a **user-defined bridge network** containers can reach each other **by name** (built-in DNS), which is how an app container finds its DB container. **Host** networking shares the host's network stack (no isolation, faster). **Overlay** networking spans **multiple hosts** (used in Swarm/Kubernetes-style clusters).
- **Volumes** — because a container's writable layer is **ephemeral** (deleted when the container is removed), you use volumes to **persist data outside the container lifecycle**. **Named volumes** are managed by Docker (best for databases), while **bind mounts** map a host directory into the container (handy for local dev to live-edit code). The key point: never store important data only in the container's own filesystem.

### Q8. What is Docker Compose?
Docker Compose is a tool for **defining and running multi-container applications** using a single declarative YAML file (`docker-compose.yml`). Instead of manually starting each container with long `docker run` commands, you describe all your services (e.g., app + PostgreSQL + Kafka + Redis), their images, ports, environment variables, volumes, and the network between them — then bring the whole stack up with `docker compose up` (and down with `docker compose down`). It's invaluable for **local development and testing**, letting a developer spin up an entire realistic environment with one command. Note: Compose is for a **single host**; for production orchestration across many machines you graduate to Kubernetes.


---

## B. Kubernetes

### Q9. What is Kubernetes? Why use it?
Kubernetes (K8s) is a **container orchestration platform** — it manages the deployment, scaling, and operation of containers **across a cluster of many machines** automatically. Running one container with Docker is easy; running hundreds across many servers reliably is not, and that's the problem K8s solves. Its core capabilities: **automated deployment** and rollouts, **self-healing** (restarts crashed containers, reschedules pods off dead nodes), **horizontal scaling** (add/remove replicas on demand), **service discovery and load balancing** (stable endpoints for dynamic pods), and **rolling updates/rollbacks** (zero-downtime deployments). You declare the **desired state** ("I want 5 replicas of this app"), and Kubernetes continuously works to make reality match that state. That declarative, self-healing model is why it's the standard for running microservices at scale (like your 200+ service AKS setup).

### Q10. Explain the K8s architecture.
A Kubernetes cluster has two kinds of machines — the **control plane** (the brain) and **worker nodes** (where your apps run):
- **Control plane** — makes global decisions:
  - **API Server** — the front door; everything (kubectl, controllers) talks to it; it validates and stores requests.
  - **etcd** — the distributed **key-value store** holding the entire cluster state (the single source of truth).
  - **Scheduler** — decides **which node** each new pod should run on (based on resources, affinity, constraints).
  - **Controller Manager** — runs control loops that drive actual state toward desired state (e.g., recreating failed pods).
  - **Cloud Controller** — integrates with the cloud provider (load balancers, volumes, nodes).
- **Worker nodes** — run the workloads:
  - **kubelet** — the agent on each node that starts/monitors the pods the control plane assigns.
  - **kube-proxy** — handles pod networking and Service routing on the node.
  - **container runtime** — actually runs the containers (e.g., containerd).
The recurring theme: the control plane holds desired state; the nodes execute it; controllers continuously reconcile the two.

### Q11. Explain core K8s objects.
Kubernetes gives you a set of declarative objects, each solving a specific need:
- **Pod** — the **smallest deployable unit**: one or more tightly-coupled containers that **share network and storage**. You rarely create pods directly.
- **ReplicaSet** — ensures a specified **number of pod replicas** are running (self-healing count).
- **Deployment** — the object you actually use for stateless apps: it manages ReplicaSets to provide **declarative updates, rolling deployments, and rollbacks**.
- **Service** — a **stable network endpoint** (IP/DNS) that load-balances across a changing set of pods.
- **Ingress** — **L7 HTTP(S) routing + TLS** into the cluster (path/host-based routing to Services).
- **ConfigMap / Secret** — externalize **configuration** (ConfigMap) and **sensitive data** (Secret) from the image.
- **Namespace** — **logical isolation/partitioning** of cluster resources (per team/env).
- **StatefulSet** — for stateful apps (databases) needing **stable identity and persistent storage** per pod.
- **DaemonSet** — runs **one pod per node** (log/metrics agents, the OTel collector).
- **Job / CronJob** — run **batch** work to completion or on a **schedule**.

### Q12. What is a Service and its types?
Pods are ephemeral and get new IPs when recreated, so you can't rely on a pod's IP directly. A **Service** provides a **stable virtual IP + DNS name** for a group of pods (selected by labels) and **load-balances** traffic across the healthy ones. The types differ by **how the Service is exposed**:
- **ClusterIP** (default) — reachable **only inside the cluster**; used for internal service-to-service communication.
- **NodePort** — opens a **static port on every node**, exposing the Service externally in a basic way (mostly for dev/testing).
- **LoadBalancer** — provisions a **cloud load balancer** (Azure/AWS) with an external IP for production external access.
- **Ingress** — technically not a Service type but the layer above: **L7 HTTP routing + TLS** that fronts multiple Services with host/path rules, so you expose many services through one entry point.

### Q13. How does autoscaling work? (you did pod autoscaling)
Kubernetes autoscaling operates at three levels:
- **HPA (Horizontal Pod Autoscaler)** — the most common: **adds/removes pod replicas** based on observed metrics (CPU, memory, or custom/external metrics like queue length). This handles fluctuating traffic.
- **VPA (Vertical Pod Autoscaler)** — **adjusts a pod's resource requests/limits** (sizing up/down) rather than the count — useful for right-sizing.
- **Cluster Autoscaler** — **adds/removes worker nodes** when pods can't be scheduled (no capacity) or nodes are underused.
A crucial prerequisite: you must **set resource requests/limits**, because HPA's CPU targets are relative to requests, and the scheduler needs requests to place pods. For event-driven workloads, **KEDA** extends HPA to scale on things like Kafka consumer lag or Service Bus queue depth.

### Q14. Rolling updates & rollbacks?
A **rolling update** is how a Deployment ships a new version with **zero downtime**: it replaces old pods with new ones **gradually**, governed by `maxSurge` (how many extra pods it can create above the desired count) and `maxUnavailable` (how many pods can be down at once). New pods only receive traffic once their **readiness probe** passes, and old pods are drained as new ones come up — so there's always capacity serving users. If the new version is broken, `kubectl rollout undo` **rolls back** to the previous ReplicaSet quickly. This combination of gradual replacement + readiness gating + easy rollback is what makes Kubernetes deployments safe.

### Q15. Liveness vs readiness vs startup probes?
These are three health checks that answer different questions, and mixing them up causes real outages:
- **Liveness probe** — "is the app **alive**, or stuck/deadlocked?" If it fails, Kubernetes **restarts** the container. Keep it cheap and don't check external dependencies (or a DB blip restarts all your pods).
- **Readiness probe** — "is the app **ready to serve traffic**?" If it fails, the pod is **removed from the Service's endpoints** (no traffic sent) but **not** restarted. Perfect for holding traffic until dependencies/caches are ready, and during graceful shutdown.
- **Startup probe** — "has the app **finished starting up**?" It's for **slow-starting apps** (e.g., a JVM that needs 40s to warm up): it **delays the liveness/readiness probes** until startup completes, preventing a too-aggressive liveness probe from killing an app that just needs time to boot.

### Q16. How do you manage config & secrets in K8s?
Kubernetes separates configuration from your image (12-factor style):
- **ConfigMaps** — hold **non-sensitive** configuration (feature flags, URLs, tuning values), injected into pods as **environment variables or mounted files**.
- **Secrets** — hold **sensitive data** (passwords, API keys, certs). Important caveat: Kubernetes Secrets are only **base64-encoded, not encrypted by default** — so you should **enable encryption at rest** on etcd and lock them down with **RBAC**.
- **External secret stores** — the more secure production approach: keep secrets in **Azure Key Vault / HashiCorp Vault / AWS Secrets Manager** and pull them into pods at runtime via the **CSI Secrets Store driver** or External Secrets Operator, authenticating with a **managed/workload identity** (no static credentials).
Either way, config/secrets are mounted as env vars or files so the same image runs in any environment.

### Q17. How do you deploy to K8s? (Helm)
There are a few approaches, increasing in sophistication:
- **`kubectl apply` of raw manifests** — directly apply YAML files. Simple, but hard to parameterize across environments and manage as versioned releases.
- **Helm** — the **package manager for Kubernetes**. A **Helm chart** is a templated, parameterized, versioned bundle of manifests, so you deploy the same chart to dev/staging/prod with different **values**, and Helm tracks it as a **release** you can upgrade/rollback. Best for packaging and reusable, configurable deployments.
- **Kustomize** — template-free customization using **overlays** that patch a common base per environment (built into `kubectl`).
- **GitOps (ArgoCD/Flux)** — the modern operational model: Git holds the desired manifests/charts, and an operator **continuously reconciles** the cluster to match Git (auditable, declarative, easy rollback).

### Q18. EKS vs AKS?
Both are **managed Kubernetes services** where the cloud provider runs and maintains the **control plane** (API server, etcd, upgrades, HA) for you, and you focus on your **workloads and worker nodes**. **EKS** is AWS's Elastic Kubernetes Service; **AKS** is Azure Kubernetes Service. Functionally they're the same Kubernetes underneath, differing mainly in **cloud integration** — IAM/identity (AWS IAM vs Entra ID/managed identity), load balancers, networking (VPC vs VNet), and registry (ECR vs ACR). The value of managed K8s is that you **don't operate the control plane yourself**, dramatically reducing ops burden. You've used **AKS** (with ACR + GitHub Actions).


---

## C. Cloud (Azure focus + AWS awareness)

### Q19. Azure compute options you used?
Azure offers a spectrum of compute options that trade **control vs convenience**, and the skill is picking the right one per workload:
- **Web Apps (App Service)** — **PaaS web hosting**: you deploy your app (jar/container) and Azure manages the servers, scaling, patching, TLS. Best for straightforward web apps/APIs where you don't need container orchestration.
- **Function Apps** — **serverless, event-driven** compute: code runs in response to triggers, scales automatically to zero, and you pay per execution. Best for glue logic, scheduled jobs, and event processing.
- **Container Apps / AKS** — for **containerized workloads**: Container Apps is a simpler managed container platform (serverless containers with scale-to-zero and KEDA built in), while **AKS** is full Kubernetes for complex, large-scale microservice systems needing fine-grained orchestration.
The talking point: I choose **PaaS (App Service)** for simple apps, **serverless (Functions)** for event-driven/spiky work, and **containers/AKS** when I need portability, complex orchestration, or scale — matching the workload to the right level of control.

### Q20. Serverless / Azure Functions — when to use?
Serverless functions are **event-driven, short-lived pieces of code** that Azure runs on demand — they **auto-scale** (including down to zero when idle) and you **pay only per execution**, so there's no idle server cost. They're invoked by **triggers**: HTTP requests, timers (scheduled jobs), queue/Service Bus messages, Event Hub events, or Blob storage changes. They're ideal for **event processing, lightweight APIs, scheduled tasks, and integration glue**. But you must design around their constraints: **cold starts** (latency when a new instance spins up after idle), **execution time limits** (not for long-running jobs), and **statelessness** (no in-memory state between invocations — use external storage). So use them for spiky, event-driven, short tasks — not for long-running or ultra-low-latency workloads.

### Q21. IaaS vs PaaS vs SaaS?
These are the three cloud service models, distinguished by **how much the provider manages vs you**:
- **IaaS (Infrastructure as a Service)** — you rent **raw compute/storage/network** (VMs) and manage everything from the **OS upward** (patching, runtime, app). Maximum control, maximum responsibility. Examples: **Azure VM, AWS EC2**.
- **PaaS (Platform as a Service)** — the provider manages the **servers and runtime**, and you just **deploy and run your app**. Less control, far less operational burden. Examples: **Azure App Service, AWS RDS**.
- **SaaS (Software as a Service)** — you just **use finished software** over the internet; the provider manages everything. Examples: **Office 365, Gmail, Salesforce**.
The pizza analogy: IaaS = you cook using a rented kitchen; PaaS = you order takeout; SaaS = you dine at the restaurant. Moving up the stack, you trade control for convenience.


### Q22. Key AWS services to know (JD lists AWS)?
- **Compute:** EC2, Lambda, ECS/EKS, Fargate.
- **Storage:** S3, EBS, EFS.
- **DB:** RDS, DynamoDB, Aurora, ElastiCache.
- **Messaging:** SQS, SNS, Kinesis (≈ Event Hubs), MSK (managed Kafka).
- **Networking:** VPC, ELB, Route53, CloudFront, API Gateway.
- **Security:** IAM, Secrets Manager, KMS.
- **Monitoring:** CloudWatch, X-Ray.

### Q23. Azure ↔ AWS service mapping (handy)
| Concept | Azure | AWS |
|--|--|--|
| VMs | Azure VM | EC2 |
| Serverless | Functions | Lambda |
| K8s | AKS | EKS |
| Object storage | Blob | S3 |
| Managed SQL | Azure SQL | RDS |
| NoSQL | Cosmos DB | DynamoDB |
| Streaming | Event Hubs | Kinesis |
| Messaging | Service Bus | SQS/SNS |
| Secrets | Key Vault | Secrets Manager |
| Identity | Entra ID (AAD) | IAM |
| Managed Kafka | HDInsight/Event Hubs (Kafka API) | MSK |

### Q24. What is Infrastructure as Code (IaC)?
IaC is the practice of **defining and provisioning your infrastructure** (servers, networks, databases, load balancers, Kubernetes clusters) **through code/config files rather than manual clicking** in a cloud console. You describe the *desired* infrastructure declaratively, and a tool creates/updates it to match. The main tools: **Terraform** (cloud-agnostic, works across AWS/Azure/GCP), **Bicep/ARM** (Azure-native), and **CloudFormation** (AWS-native). The benefits are significant: infrastructure becomes **version-controlled** (tracked in Git, with history and rollback), **repeatable** (spin up an identical staging/prod/DR environment reliably), **reviewable** (changes go through PRs like code), and it enables **drift detection** (spotting when reality has diverged from the defined config). It eliminates the slow, error-prone, undocumented "click-ops" approach and makes environments consistent and reproducible.

---

## D. CI/CD

### Q25. What is CI/CD? (you used GitHub Actions)
CI/CD is the automation backbone of modern delivery, made of two connected practices:
- **CI (Continuous Integration)** — **every commit is automatically built and tested**. The goal is **fast feedback** and catching bugs/integration issues early, before they pile up. It acts as a set of **quality gates** (tests, linting, security scans) that code must pass.
- **CD (Continuous Delivery/Deployment)** — the tested build is **automatically delivered/deployed** to environments. Continuous *Delivery* means it's always deployable (often with a manual approval to push to prod); continuous *Deployment* means it goes all the way to prod automatically.
A typical pipeline: **build → unit tests → static analysis/security scan → package (Docker) → push to registry → deploy (staging → prod) → smoke tests**. The overall value: releases become **fast, frequent, and reliable** instead of slow, risky, manual events.

### Q26. Describe a GitHub Actions pipeline you built.
A concrete flow from my Azure work: the workflow **triggers on push/PR to a branch**, then **sets up the JDK**, runs **`mvn verify`** (compile + unit/integration tests), and if that passes, **builds a Docker image** and **pushes it to Azure Container Registry (ACR)**. The deploy job then **rolls the new image out to AKS** using kubectl/Helm with a **rolling update** for zero downtime. For safety, I use **GitHub Environments with protection rules** — staging deploys automatically, but **production requires a manual approval**. Secrets (registry creds, kubeconfig) are stored in **GitHub Secrets / pulled from Azure Key Vault**, and I prefer **OIDC federation** to Azure over long-lived credentials. This gives an auditable, automated path from commit to production.

### Q27. Deployment strategies (recap)?
The main strategies, all aimed at **zero downtime + fast rollback**:
- **Rolling** (the default) — gradually replace old pods/instances with new ones; simple and resource-efficient, but rollback is a bit slower.
- **Blue-Green** — run **two full environments** (blue = current, green = new); deploy/test on green, then **switch all traffic at once**; gives **instant rollback** but doubles resources temporarily.
- **Canary** — route a **small percentage** of traffic to the new version, watch metrics, then gradually ramp up; best **risk control** for uncertain changes.
- **Feature flags** — deploy code "dark" and **toggle features on/off at runtime** independent of deployment, enabling gradual rollout and instant disable without redeploying.
You pick based on risk tolerance and infrastructure: rolling for routine changes, canary/blue-green for risky ones.

### Q28. How do you secure a CI/CD pipeline?
A CI/CD pipeline is a high-value attack target (it has access to prod), so you harden it at multiple points:
- **Secret management** — never hardcode credentials; use a secrets store / Key Vault, and prefer **OIDC federation** so the pipeline gets short-lived tokens instead of long-lived cloud keys.
- **Least-privilege service principals** — the deploy identity should have only the permissions it needs, scoped tightly.
- **Scanning** — **dependency scanning** and **container image scanning** (Trivy, Snyk) to catch known CVEs, plus generating an **SBOM** (software bill of materials) and **signing images** so you can verify provenance.
- **Source controls** — **branch protection** and **required reviews** so no unreviewed code reaches main, plus required status checks.
The theme: shift security **left** (into the pipeline) and never trust unverified code or long-lived credentials.

### Q29. What is GitOps?
GitOps is an operational model where **Git is the single source of truth** for both infrastructure and application deployments. Instead of manually running `kubectl apply` or pushing changes to the cluster, you commit the **desired state** (manifests/Helm charts) to a Git repo, and an in-cluster **operator (ArgoCD or Flux) continuously reconciles** the actual cluster state to match what's in Git — automatically applying changes and correcting drift. The benefits: everything is **declarative and auditable** (every change is a Git commit with history and review), **rollbacks are trivial** (revert the commit), and there's **no manual cluster access** needed for deployments. It essentially applies the "infrastructure as code + pull-based automation" philosophy to running Kubernetes.


---

## E. Observability (your specialty — MGM)

### Q30. Three pillars of observability?
Observability is the ability to understand a system's internal state from its outputs, and it rests on three complementary data types — you need all three because each answers a different question:
- **Metrics** — **numeric time-series** data (request rate, error count, CPU, latency percentiles). Cheap to store and query, great for **dashboards and alerting** — they tell you **"is something wrong?"**. Tools: **Prometheus + Grafana**.
- **Logs** — **discrete, timestamped event records** with detailed context. They tell you **"what exactly happened?"**. Best as **structured JSON** and centrally aggregated. Tools: **ELK (Elasticsearch/Logstash/Kibana) or Loki**.
- **Traces** — the **end-to-end path of a single request as it flows across multiple services**, with timing for each hop/span. They tell you **"where is it slow / where did it fail?"** in a distributed system. Tools: **OpenTelemetry → Jaeger/Tempo**.
The power comes from correlating them (a trace ID in your logs links the three), which is exactly what makes debugging distributed systems tractable.

### Q31. What is OpenTelemetry? (you used it)
OpenTelemetry (OTel) is a **vendor-neutral, open standard** — plus a set of SDKs and a collector — for **generating and collecting all three signals: traces, metrics, and logs**. Its big value is **decoupling instrumentation from the backend**: you instrument your code **once** against the OTel API, and can then export the data via the **OTLP protocol** to *any* compatible backend (Grafana Tempo, Jaeger, Prometheus, commercial APM tools) without changing your app — no vendor lock-in. It supports **auto-instrumentation** (agents that automatically capture HTTP/DB/messaging calls) and **manual instrumentation** (custom spans/metrics for business logic), plus **context propagation** (W3C `traceparent`) so a trace follows a request across service boundaries. (At MGM I built a reusable Java common module wrapping OTel so any team could adopt standardized tracing/metrics by adding one dependency.)

### Q32. Prometheus & Grafana?
These are the de facto open-source metrics stack, and they play distinct roles:
- **Prometheus** — a **pull-based metrics database**: it periodically **scrapes** metrics from your services' `/metrics` endpoints, stores them as time-series, and lets you query with **PromQL**. It also handles **alerting rules**, firing alerts to **Alertmanager** (which routes them to Slack/PagerDuty/email).
- **Grafana** — the **visualization layer**: it builds **dashboards and graphs** on top of data sources like Prometheus (metrics), Loki (logs), and Tempo (traces), giving a single pane of glass.
In a Spring Boot app, **Micrometer** (the metrics facade) exposes a `/actuator/prometheus` endpoint that Prometheus scrapes — so you get JVM, HTTP, and custom business metrics into Grafana with minimal effort. Prometheus gathers/queries/alerts; Grafana makes it visual.

### Q33. What metrics matter (RED/USE)?
Rather than tracking everything, two well-known frameworks tell you *which* metrics matter, depending on whether you're monitoring a **service** or a **resource**:
- **RED** (for **request-driven services**): **R**ate (requests/sec), **E**rrors (failed requests), **D**uration (latency, especially p95/p99). These directly reflect user-facing health.
- **USE** (for **resources** like CPU, memory, disk, queues): **U**tilization (how busy), **S**aturation (how much queued/overloaded), **E**rrors. These reveal resource bottlenecks.
On top of these you define **SLIs** (indicators you measure), **SLOs** (targets, e.g., 99.9% availability), and **SLAs** (contractual commitments), and track an **error budget** (how much unreliability you can "spend") to balance reliability vs feature velocity. The point: measure what reflects user experience and resource health, not vanity metrics.

### Q34. How do you reduce MTTR? (your 25% story)
MTTR (Mean Time To Resolution) drops when engineers can **find and understand problems faster**, so you attack every step of the incident-response path: **standardized structured logging + correlation/trace IDs** (so you can trace one request across all services), **distributed tracing** (to pinpoint the slow/failing span), **good dashboards and well-tuned alerts** (to detect issues fast and with context, not noise), and **runbooks** (so on-call knows the remediation steps). In my case, I added **RAG-driven alert summarization** that pulled the relevant root-cause context (logs, recent changes, similar past incidents) and surfaced it **directly to the on-call engineer** with the alert — so they started debugging with context instead of from scratch, cutting resolution time ~25%. The theme: reduce the time to *detect*, *diagnose*, and *decide*.

### Q35. Structured logging best practices?
Structured logging means emitting logs as **machine-parseable data (JSON)** with consistent fields rather than free-form text — this is what makes logs searchable and aggregatable at scale. Best practices:
- **JSON format** with **consistent field names** (timestamp, level, service, message, etc.) so tools can index and query them.
- Always include a **correlation/trace ID** so you can stitch together all logs for a single request across services (and link to traces).
- Use appropriate **log levels** (ERROR/WARN/INFO/DEBUG) so you can filter signal from noise.
- **Never log secrets or PII** (passwords, tokens, card numbers) — a common and serious mistake.
- **Centralize** logs (ELK/Loki) so you're not SSH-ing into pods, and apply **sampling** for very high-volume logs to control cost.
The goal: logs that a machine can search and correlate instantly, giving you the detailed "what happened" that complements metrics and traces.

---

## F. Security & Secrets (bridges to file 10)

### Q36. How do you manage secrets? (JD: Vault, Secrets Manager)
The cardinal rule is **never store secrets in code or repositories** (they leak, live forever in Git history, and can't be rotated cleanly). Instead, keep them in a dedicated **secrets manager**: **HashiCorp Vault**, **Azure Key Vault**, or **AWS Secrets Manager**. Then:
- **Inject at runtime** rather than baking into images — via environment variables, the **CSI Secrets Store driver** (mounts secrets as files), or better, a **managed/workload identity** so the app authenticates to the vault without any static credential at all.
- **Rotate secrets regularly** (and automatically where possible), so a leaked secret has a short useful life.
- **Audit access** — log who/what reads each secret.
- **Encrypt at rest** and control access with least-privilege policies.
The end goal: secrets are centralized, access-controlled, rotatable, and never sitting in plaintext in your codebase or images.

### Q37. What is least-privilege IAM?
Least-privilege is the security principle of granting each user, service, or component **only the minimum permissions it needs to do its job — and nothing more**. This **minimizes the blast radius**: if an account or service is compromised, the attacker can only do the limited things that identity was allowed to do. In practice: prefer **roles / managed identities over long-lived access keys** (no static credentials to steal), **scope policies tightly** (specific resources and actions, not wildcards), **review permissions regularly** (permissions tend to accumulate — "permission creep"), and favor **short-lived credentials via OIDC federation** over permanent keys. It's a foundational cloud-security practice that pairs with proper secret management.


---

## ⚡ Rapid-Fire
- **`kubectl get pods / describe pod / logs / exec -it`** — debugging basics.
- **CrashLoopBackOff** — pod repeatedly crashing (check logs/probes/resources).
- **ImagePullBackOff** — can't pull image (auth/tag).
- **Resource requests vs limits** — guaranteed vs max; drives scheduling + QoS + OOMKill.
- **Sidecar pattern** — helper container in same pod (e.g., OTel collector, Envoy).
- **Service mesh (Istio/Linkerd)** — mTLS, traffic mgmt, observability without app changes.
- **Blue-green = instant switch; canary = gradual.**
- **12-factor config** — env-based, not baked into image.

---
---

# PART 2 — Advanced & Tough Questions (with detailed explanations + examples)

## T1. A pod is in CrashLoopBackOff — walk me through debugging it.
1. `kubectl get pods` → see status/restarts.
2. `kubectl logs <pod> --previous` → the crash reason from the last run.
3. `kubectl describe pod <pod>` → events (OOMKilled? failed probe? image pull? mount error?).
4. Common causes: app throws on startup (bad config/secret), **liveness probe** too aggressive (killing a slow-starting app → add a **startup probe**), missing env/ConfigMap, **OOMKilled** (raise memory limit or fix leak), port mismatch.
5. `kubectl exec -it` into a running variant, or run the image locally to reproduce.

## T2. Liveness vs readiness vs startup — a subtle production bug.
A common outage: a **liveness probe** with a short `initialDelaySeconds` restarts a JVM app that just needs 40s to warm up → endless restarts. Fix: use a **startup probe** to gate liveness until the app is up, keep **readiness** to hold traffic until dependencies are ready, and make liveness cheap (don't check the DB in liveness or a DB blip restarts all pods).

## T3. Requests vs limits — how do they affect scheduling, QoS, and OOMKills?
- **Requests** — guaranteed, used by the scheduler to place pods (and by HPA).
- **Limits** — hard cap; exceeding **memory** limit → **OOMKilled**; exceeding **CPU** limit → throttled (not killed).
- **QoS classes:** *Guaranteed* (requests==limits), *Burstable*, *BestEffort* (no requests/limits — evicted first under pressure).
Pitfall: setting no memory limit risks a noisy-neighbor OOM on the node; setting CPU limits too low causes latency from throttling. Right-size from real metrics.

## T4. How does HPA actually decide to scale? What can go wrong?
HPA compares observed metric (e.g., CPU) to target: `desiredReplicas = ceil(current * currentMetric/targetMetric)`. Needs **resource requests** set (CPU% is relative to request) and the **metrics-server**. Gotchas: scaling on CPU when the bottleneck is I/O/latency (use **custom/KEDA** metrics like queue length or Kafka lag), flapping (tune stabilization windows), and startup lag. For event-driven scaling (your messaging work), **KEDA** scaling on Kafka/Service Bus lag is the modern answer.

## T5. Docker: why multi-stage builds and non-root, and how to shrink images?
Multi-stage = build with JDK/Maven, ship only the JRE + jar → smaller attack surface + faster pulls. Also: use **distroless/alpine** bases, `.dockerignore`, layer caching (copy `pom.xml` + download deps before copying source so dependency layers cache), run as **non-root** user, pin versions, scan with **Trivy**. A fat image = slower deploys + more CVEs.
```dockerfile
RUN addgroup -S app && adduser -S app -G app
USER app
```

## T6. Rolling update caused a brief outage — why, and how do you get true zero-downtime?
Causes: no **readiness probe** (traffic sent before app ready), no `preStop` hook/graceful shutdown (in-flight requests dropped), too-aggressive `maxUnavailable`. Fixes: readiness probe gating, `terminationGracePeriodSeconds` + app handling SIGTERM (drain), `preStop` sleep to let the LB deregister, `PodDisruptionBudget` to keep min replicas during node drains, and `maxSurge=1,maxUnavailable=0`.

## T7. Blue-green vs canary vs rolling — pick one for a risky release.
- **Rolling** (default) — gradual pod replacement; simple; harder instant rollback.
- **Blue-green** — full parallel env, switch traffic at once; instant rollback; double resources.
- **Canary** — route small % to the new version, watch metrics (error rate/latency), then ramp; best for risk control (needs good observability + traffic splitting via mesh/ingress). For a risky change I'd canary with automated metric gates and auto-rollback.

## T8. How do you manage secrets end-to-end (JD: Vault, Secrets Manager)?
K8s Secrets are only **base64** (not encrypted by default) → enable **encryption at rest** + RBAC, or better, use **external secrets**: Azure **Key Vault** / HashiCorp **Vault** via the **CSI Secrets Store driver** or External Secrets Operator, injected at runtime. Use **workload identity / managed identity** so pods authenticate without static creds. Rotate regularly, audit access, never bake secrets into images or Git. In CI/CD use OIDC federation instead of long-lived cloud keys.

## T9. Describe a robust CI/CD pipeline you'd build (with security gates).
`push/PR` → build → **unit + integration tests (Testcontainers)** → **static analysis** (SonarQube) → **dependency/image scan** (Trivy/Snyk) → build & sign Docker image (SBOM) → push to ACR → deploy to **staging** (auto) → smoke/contract tests → **manual approval** → **canary to prod** with metric gates → auto-rollback on failure. Secrets via OIDC + Key Vault; environments with protection rules. This maps to your GitHub Actions + AKS experience.

## T10. IaC: why Terraform, and how do you keep state safe in a team?
Terraform gives declarative, versioned, reviewable infra with a **plan/apply** workflow and drift detection. Team practices: **remote state** (Azure Storage/S3) with **state locking** (blob lease/DynamoDB), separate state per environment, modules for reuse, `plan` in PRs, least-privilege service principals, and never commit state (it can contain secrets). Bicep/ARM if Azure-only.

## T11. OpenTelemetry — how did you instrument 200+ services consistently? (your MGM story)
Build a **reusable common module/starter** that auto-configures the OTel SDK (traces/metrics/logs), standard resource attributes (service name, env, version), context propagation (W3C `traceparent`), and OTLP export — so any team onboards by adding one dependency (your 40% boilerplate reduction). Auto-instrument HTTP/JDBC/Kafka; add manual spans for business ops. Export to Tempo/Jaeger + Prometheus + Grafana. Sampling (tail-based) to control volume.

## T12. Metrics vs logs vs traces — which do you reach for when?
- **Metrics** (Prometheus) — "is something wrong?" cheap, alertable (RED/USE, SLOs).
- **Traces** (OTel) — "where is it slow?" per-request latency breakdown across services.
- **Logs** (Loki/ELK) — "what exactly happened?" detailed context (with trace id to correlate).
Debugging flow: alert (metric) → trace (find slow span) → logs (root cause). This layered approach is how you cut MTTR.

## T13. Serverless (Azure Functions/Lambda) — cold starts and when NOT to use it.
Cold start = latency when a new instance spins up (worse for JVM/.NET; better for Node/Python; mitigate with **premium/pre-warmed** plans, smaller packages, provisioned concurrency). Avoid serverless for: long-running/CPU-heavy jobs, ultra-low-latency needs, heavy stateful workloads, or chatty DB apps (connection exhaustion — use a proxy/pooling). Great for event-driven, spiky, glue workloads.

## T14. Docker container vs VM — and where does Kubernetes fit?
Containers share the host kernel (lightweight, fast, dense) vs VMs (full OS, stronger isolation, heavier). Kubernetes **orchestrates** containers across many nodes — scheduling, self-healing, scaling, service discovery, rolling updates. You don't need K8s for a couple of containers (Compose/App Service suffices); you need it at scale with many services (your 200+ microservice AKS setup).

## T15. Tough rapid-fire
- **ImagePullBackOff** — bad tag/registry auth; check `imagePullSecrets`.
- **Node NotReady** — kubelet/network/disk pressure; `kubectl describe node`.
- **Service has no endpoints** — selector doesn't match pod labels, or readiness failing.
- **ClusterIP vs NodePort vs LoadBalancer vs Ingress** — internal / node port / cloud LB / L7 routing+TLS.
- **StatefulSet vs Deployment** — stable identity + persistent volumes (DBs) vs stateless.
- **DaemonSet** — one pod per node (log/metrics agents, OTel collector).
- **Sidecar** — helper container in the pod (proxy/collector); the mesh pattern.
- **Helm vs Kustomize** — templated packages+releases vs overlay patches; GitOps with ArgoCD.
- **12-factor** — config in env, stateless processes, logs as streams → cloud-native readiness.
- **Multi-AZ / region** — spread nodes across zones + PodTopologySpread for HA; DR with backups + IaC to rebuild.

---
---

# PART 3 — More Real Interview Questions (Easy Language, No Repeats)

## Q1. What is "the cloud" in simple terms?
Instead of buying and running your own servers, you **rent** computing power, storage, and services from a provider (AWS, Azure, Google) over the internet, and pay only for what you use. You can scale up/down instantly and let them handle the hardware, power, and networking.

## Q2. What is Docker, using an analogy?
Docker is like a **shipping container** for software. Just as a physical container holds goods and can be moved onto any ship or truck unchanged, a Docker container packages your app + everything it needs (libraries, config) so it runs the same way on any machine — your laptop, a test server, or production. Solves "it works on my machine."

## Q3. What is the difference between a Docker image and a container (simple)?
- **Image** — the blueprint/template (like a class in code, or a recipe).
- **Container** — a running instance of that image (like an object, or the cooked dish).
You build an image once and run many containers from it.

## Q4. Why do we need Kubernetes if we already have Docker?
Docker runs a container on one machine. But in production you have **many containers across many machines**, and you need them to restart when they crash, scale up under load, get traffic routed to them, and update without downtime. **Kubernetes** automates all of that — it's the "manager" for lots of containers.

## Q5. What is a Pod in Kubernetes (beginner version)?
The smallest deployable unit — usually **one container** (sometimes a couple that must run together). Kubernetes doesn't run containers directly; it runs them inside pods. Pods are disposable — if one dies, Kubernetes creates a new one.

## Q6. What is a Deployment in Kubernetes?
A Deployment is your instruction to Kubernetes: "keep 3 copies of this app running, and here's how to update them." It handles creating pods, replacing crashed ones, scaling the number up/down, and doing rolling updates (and rollbacks). You mostly interact with Deployments, not raw pods.

## Q7. What is a Service in Kubernetes and why is it needed?
Pods come and go and get new IPs, so you can't rely on a pod's IP. A **Service** gives a stable name/IP that always points to the healthy pods behind it, and load-balances traffic across them. Other apps talk to the Service, not individual pods.

## Q8. What is CI/CD in one simple sentence each?
- **CI (Continuous Integration)** — every time someone pushes code, it's automatically built and tested, so bugs are caught early.
- **CD (Continuous Delivery/Deployment)** — that tested code is automatically packaged and deployed to environments, so releases are fast, frequent, and reliable.

## Q9. What is a CI/CD pipeline, described as steps?
A recipe that runs automatically: **build the code → run tests → scan for security issues → package into a Docker image → push to a registry → deploy to test → deploy to production**. Each step must pass before the next. This replaces slow, error-prone manual deployments.

## Q10. What is an artifact and an artifact registry?
An **artifact** is the built output you deploy — e.g., a JAR file or a Docker image. An **artifact/container registry** (Docker Hub, Azure ACR, AWS ECR) is a storage place for these images, so your deploy step can pull the exact version to run.

## Q11. What is Infrastructure as Code (IaC), simply?
Instead of clicking around in a cloud console to create servers/databases (manual, error-prone, not repeatable), you **write it as code** (e.g., Terraform files) and run it. This makes your infrastructure repeatable, reviewable, version-controlled, and easy to recreate in another environment.

## Q12. What is the difference between IaaS, PaaS, and SaaS (with examples)?
- **IaaS** — you rent raw servers and manage the OS/app yourself (Azure VM, AWS EC2).
- **PaaS** — you just deploy your app; the platform manages servers (Azure App Service, Heroku).
- **SaaS** — you just use finished software (Gmail, Office 365).
Analogy: pizza — IaaS = you cook with rented kitchen; PaaS = you order takeout; SaaS = you dine at the restaurant.

## Q13. What is autoscaling and how does it help?
Automatically adding more instances when traffic/load is high and removing them when it's low. Benefits: your app stays fast under spikes **and** you save money by not running extra servers when idle. In Kubernetes, the **HPA** scales pods based on CPU/memory or custom metrics.

## Q14. What is a rolling update and why is it "zero downtime"?
Instead of stopping all old versions and starting new ones (causing an outage), Kubernetes replaces pods **a few at a time** — starting new ones and only removing old ones once the new are healthy. Users always have working pods serving them, so there's no downtime. If something's wrong, you roll back.

## Q15. What is observability (the 3 pillars) in plain words?
Being able to understand what's happening inside your running system:
- **Logs** — detailed text records of events ("what happened").
- **Metrics** — numbers over time like CPU, request count, error rate ("is something wrong?").
- **Traces** — the path of a single request across services ("where is it slow?").
Together they let you find and fix problems fast.

## Q16. What is the difference between monitoring and observability?
**Monitoring** = watching known things (dashboards/alerts for CPU, errors) — "is it up?". **Observability** = the ability to ask **new questions** about your system's behavior from its data (logs/metrics/traces) — "why is this specific user's request slow?". Observability is broader and helps debug the unexpected.

## Q17. What is Prometheus and Grafana (simple roles)?
- **Prometheus** — collects and stores metrics (numbers over time) and can trigger alerts.
- **Grafana** — the dashboard/visualization tool that draws those metrics as graphs and charts.
Together: Prometheus gathers the data, Grafana makes it visual. (You used exactly this at MGM.)

## Q18. What is a container registry vs Kubernetes (people mix these up)?
- **Container registry** (ACR/ECR/Docker Hub) — where you **store** built images.
- **Kubernetes** — where you **run** containers from those images.
CI builds the image → pushes to the registry → Kubernetes pulls it and runs it.

## Q19. How do you keep secrets (passwords, API keys) safe in the cloud?
Never put them in code or Git. Store them in a **secrets manager / vault** (Azure Key Vault, AWS Secrets Manager, HashiCorp Vault). Apps fetch them at runtime, ideally using a **managed identity** so there's no master password to leak. Rotate them regularly and restrict who can read them.

## Q20. What is blue-green deployment, explained simply?
Run two identical environments: **Blue** (current live) and **Green** (new version). You deploy and test on Green while Blue serves users, then **switch all traffic to Green** at once. If something breaks, switch back to Blue instantly. Safe, with fast rollback — at the cost of running two environments.

## Q21. What is a canary release?
Release the new version to a **small percentage** of users first (say 5%), watch the metrics (errors, latency), and if all looks good, gradually increase to 100%. If something's wrong, only a few users were affected and you roll back. It's a cautious way to release risky changes.

## Q22. What happens (step by step) when you deploy a new version to Kubernetes?
1. CI builds a new Docker image and pushes it to the registry (e.g., ACR).
2. You update the Deployment to use the new image tag.
3. Kubernetes starts **new** pods with the new version.
4. It waits for their **readiness probe** to pass before sending them traffic.
5. It gradually terminates the **old** pods (rolling update).
6. If new pods fail health checks, it stops and you can `rollout undo`.
Result: a safe, zero-downtime update — exactly the flow you ran on AKS with GitHub Actions.



