# 00 — Exam Strategy & Question Types

> **Prerequisite:** none. Read this first so the question formats in every later file feel familiar.

## 1. The six question formats you will see

### 1.1 Multiple choice (one answer)
Pick the single best answer. Two options are usually clearly wrong; the other two are "close". The deciding word is almost always in the question: *minimise cost*, *least administrative effort*, *without managing servers*, *highest availability*.

### 1.2 Multiple select ("Each correct answer presents a complete solution. Choose two.")
- "**Complete solution**" = each picked option works **on its own**.
- "**Part of the solution**" = the picked options work **together**.
Read which wording is used — it changes the answer.

### 1.3 Yes / No statement series (the most important format)
Three statements about one topic; answer Yes or No to each. **You cannot go back** after you leave the set. Treat each statement independently and look for the one word that breaks it (*always, only, must, all, automatically, guaranteed*).

### 1.4 Hot area / drop-down sentence completion
A sentence with a blank: *"\_\_\_\_\_ provides recommendations to reduce cost."* Pick from a drop-down. These test exact service names — know the name ↔ purpose mapping cold (file 15).

### 1.5 Drag-and-drop matching
Match services to descriptions. Some services may be used once, more than once, or not at all.

### 1.6 Case-style scenario (rare on AZ-900)
A short company description followed by 2–4 questions. Same skills, more reading.

## 2. Time plan

| Phase | Minutes | What to do |
|---|---|---|
| Pass 1 | 0–35 | Answer everything (~50 s per question), flag doubts |
| Pass 2 | 35–43 | Revisit flagged questions |
| Buffer | 43–45 | Make sure nothing is blank |

## 3. The 7 decoding rules (they settle most "close" options)

| If the question says… | Lean towards… | Example |
|---|---|---|
| "without managing servers / infrastructure" | PaaS or serverless (Functions, App Service, Logic Apps) | Run code when a file is uploaded → **Azure Functions** |
| "full control of the OS" | IaaS (Virtual Machines) | Install a custom driver → **VM** |
| "users just use the app" | SaaS | Email for staff → **Microsoft 365** |
| "enforce / prevent / deny a configuration" | **Azure Policy** | Only allow VMs in India regions |
| "who can do what" | **RBAC** | Give helpdesk read-only access |
| "prevent accidental deletion" | **Resource lock (Delete / CanNotDelete)** | Protect production database |
| "recommendations" | **Azure Advisor** | How do I cut cost? |
| "is Azure having an outage affecting me?" | **Azure Service Health** | Region incident notice |
| "collect metrics and logs, alert" | **Azure Monitor** | CPU > 80% alert |
| "private, dedicated connection, not over internet" | **ExpressRoute** | Bank linking datacentre to Azure |
| "encrypted over the internet" | **VPN Gateway** | Branch office to Azure |
| "manage on-prem / other cloud servers from Azure" | **Azure Arc** | Govern AWS VMs with Azure Policy |
| "estimate cost before deploying" | **Pricing calculator** | Price a VM before buying |
| "analyse / budget actual spending" | **Cost Management** | Alert at 80% of monthly budget |

## 4. Words that usually make a statement FALSE

- **"Always"**, **"never"**, **"only"**, **"guaranteed"**, **"automatically"**, **"all"**.
  *"Moving to the cloud always reduces cost"* → **No**.
  *"Microsoft is responsible for all security in the cloud"* → **No** (shared responsibility).
- Absolute claims about SLAs: *"Deploying two VMs guarantees 100% uptime"* → **No**.

## 5. Words that change the answer

| Word | Effect |
|---|---|
| **Minimise cost** | Cheapest option that still works (e.g. LRS instead of GRS, Archive instead of Hot, Reserved instance for steady 24×7 load) |
| **Minimise administrative effort** | Most managed option (PaaS/SaaS over IaaS) |
| **Highest availability** | Availability zones, zone-redundant or geo-redundant |
| **Survive a region outage** | Something **geo**-something (GRS/GZRS, region pairs, second region) — zones are not enough |
| **Survive a datacentre outage** | Availability **zones** / ZRS |
| **Survive a rack/hardware failure** | Availability **set** / LRS is enough |

## 6. Exam-day checklist

1. Online exam: clean desk, ID ready, close all apps, stable internet; check-in opens 30 minutes before.
2. Test centre: arrive 15 minutes early with government ID.
3. Answer every question — no negative marking.
4. For Yes/No series, decide carefully **before** clicking Next.
5. Unscored "beta" questions may appear — you won't know which, so treat every question seriously.
6. Your result appears immediately on screen.

---

## Practice questions about the exam itself

### Q0.01 · L1 · Passing score
What score is required to pass AZ-900?

- A. 70% of questions correct
- B. 700 on a scale of 1–1000
- C. 800 on a scale of 1–1000
- D. 600 on a scale of 1–1000

<details><summary><b>Answer</b></summary>

**Answer: B**

The score is **scaled** from 1–1000 and 700 passes. It is *not* the same as 70% correct — questions carry different weights, and some unscored items may appear.
- **Not covered:** Microsoft doesn't publish per-question weights.
</details>

### Q0.02 · L2 · Multiple select wording
A question says *"Each correct answer presents part of the solution. Choose two."* What does this mean?

- A. Either option alone solves the problem
- B. Both options together solve the problem
- C. Only one option is right; the other is a distractor
- D. You get half marks for one correct option, and the answer is optional

<details><summary><b>Answer</b></summary>

**Answer: B**

"Part of the solution" = they work **together**. "Complete solution" = each one works **on its own**. Partial credit may be given on some multi-part items, but you should aim to pick both correctly.
</details>

### Q0.03 · L2 · Yes/No series behaviour
Which statement about Yes/No statement series is true?

- A. You can return to them at the end of the exam
- B. You cannot return to them once you move to the next screen
- C. They are never scored
- D. They always have exactly one "Yes"

<details><summary><b>Answer</b></summary>

**Answer: B**

Once you leave the set, you can't come back. Any combination of Yes/No is possible — including all Yes or all No.
</details>
