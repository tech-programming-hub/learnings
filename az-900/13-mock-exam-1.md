# 13 — Mock Exam 1 (50 questions, ~45 minutes)

> **Rules:** answer all 50 on paper first, without notes, in 45 minutes. Then check the answer key at the bottom.
> **Weighting matches the real exam:** Cloud concepts Q1–14 · Architecture & services Q15–33 · Management & governance Q34–50.
> **Target:** ≥ 43/50 (86%). Every miss → re-read the file named in the key.

---

## Section 1 — Cloud concepts

### M1.01
Which of the following is a characteristic of the consumption-based model?
- A. Paying a fixed fee for reserved hardware
- B. Paying only for the resources you use
- C. Buying servers before you need them
- D. Paying annually in advance for all services

### M1.02
Which cloud model gives an organisation the most control over physical hardware?
- A. Public
- B. Private
- C. Hybrid
- D. SaaS

### M1.03
Yes/No:
1. In IaaS, the customer manages the operating system.
2. In SaaS, the customer manages the application code.
3. In every model, the customer is responsible for their data.

### M1.04
A company wants to deploy a custom web app without managing servers but needs to write its own code. Which service type fits?
- A. IaaS
- B. PaaS
- C. SaaS
- D. On-premises

### M1.05
Your app automatically adds compute instances when traffic increases and removes them when it decreases. This is:
- A. Fault tolerance
- B. Elasticity
- C. Agility
- D. Disaster recovery

### M1.06
Which statement about serverless computing is TRUE?
- A. You choose and patch the operating system
- B. Billing is based on execution and resources consumed
- C. It cannot scale automatically
- D. It requires reserved instances

### M1.07
An application uses a web tier with a 99.95% SLA and a database with a 99.99% SLA. Both are required. The composite SLA is approximately:
- A. 99.99%
- B. 99.95%
- C. 99.94%
- D. 99.97%

### M1.08
Which expenditure type allows costs to be deducted in the same year they occur?
- A. CapEx
- B. OpEx
- C. Depreciation
- D. Fixed assets

### M1.09
A company uses its on-premises datacentre for regular workloads and Azure for peak demand. Which model is this?
- A. Public cloud
- B. Private cloud
- C. Hybrid cloud
- D. Multi-cloud

### M1.10
Which is ALWAYS Microsoft's responsibility?
- A. Accounts and identities
- B. Physical datacentre
- C. Devices
- D. Data classification

### M1.11
Which pricing option is best for a non-critical batch job that can be interrupted, at the lowest cost?
- A. Reserved instance
- B. Spot VM
- C. Pay-as-you-go
- D. Dedicated host

### M1.12
Using Azure Policy and templates to ensure deployments meet corporate standards demonstrates which cloud benefit?
- A. Governance
- B. Elasticity
- C. Scalability
- D. Predictability of performance

### M1.13
Increasing a VM from 4 GB RAM to 16 GB RAM is an example of:
- A. Scaling out
- B. Scaling up
- C. Elasticity
- D. Horizontal scaling

### M1.14
Which service type would a company choose to migrate existing servers to the cloud with no application changes?
- A. SaaS
- B. PaaS
- C. IaaS
- D. Serverless

## Section 2 — Azure architecture and services

### M1.15
What is the minimum number of availability zones in a zone-enabled region?
- A. 1
- B. 2
- C. 3
- D. 4

### M1.16
Which statement about resource groups is TRUE?
- A. A resource can belong to multiple resource groups
- B. Resource groups can be nested
- C. Deleting a resource group deletes its resources
- D. All resources in a group must be in the same region

### M1.17
What is the correct order from broadest to narrowest scope?
- A. Subscription, management group, resource group, resource
- B. Management group, subscription, resource group, resource
- C. Resource group, subscription, resource, management group
- D. Management group, resource group, subscription, resource

### M1.18
Which feature protects VMs from a failure of an entire datacentre within a region?
- A. Availability sets
- B. Availability zones
- C. Resource locks
- D. Update domains

### M1.19
Which service should you use to host a website and REST API in Python without managing the OS?
- A. Azure Virtual Machines
- B. Azure App Service
- C. Azure Virtual Desktop
- D. Azure Dedicated Host

### M1.20
Which connectivity option provides a private connection between on-premises and Azure that does NOT use the public internet?
- A. Site-to-site VPN
- B. Point-to-site VPN
- C. ExpressRoute
- D. VNet peering

### M1.21
Yes/No:
1. VNet peering traffic travels over the Microsoft backbone.
2. VNet peering is transitive.
3. Peered VNets can be in different regions.

### M1.22
Which storage service should you use to provide SMB file shares that can be mounted by on-premises and cloud servers?
- A. Blob storage
- B. Azure Files
- C. Queue storage
- D. Table storage

### M1.23
Which redundancy option keeps three copies of data across three availability zones in one region?
- A. LRS
- B. ZRS
- C. GRS
- D. RA-GRS

### M1.24
You need to read your storage data from the secondary region at any time, even when the primary is healthy. Which option?
- A. GRS
- B. RA-GRS
- C. ZRS
- D. LRS

### M1.25
Which access tier has a minimum retention of 180 days and requires rehydration before reading?
- A. Hot
- B. Cool
- C. Cold
- D. Archive

### M1.26
You need to move 90 TB from a site with a slow internet connection. What should you use?
- A. AzCopy
- B. Azure Data Box
- C. Azure Storage Explorer
- D. Azure File Sync

### M1.27
Which service provides a central hub to discover, assess and migrate on-premises servers?
- A. Azure Arc
- B. Azure Migrate
- C. Azure Advisor
- D. Azure Monitor

### M1.28
Which identity service provides LDAP, Kerberos and Group Policy without deploying domain controllers?
- A. Microsoft Entra ID
- B. Microsoft Entra Domain Services
- C. Entra External ID
- D. Azure RBAC

### M1.29
Which feature evaluates signals such as location and device to decide whether to require MFA?
- A. Azure Policy
- B. Conditional Access
- C. RBAC
- D. Defender for Cloud

### M1.30
Which built-in role can manage all resources but cannot grant access to others?
- A. Owner
- B. Contributor
- C. Reader
- D. User Access Administrator

### M1.31
Which is NOT a principle of Zero Trust?
- A. Verify explicitly
- B. Use least privilege access
- C. Assume breach
- D. Trust the corporate network

### M1.32
Which service gives a secure score and recommendations for Azure, AWS and on-premises resources?
- A. Azure Advisor
- B. Microsoft Defender for Cloud
- C. Microsoft Purview
- D. Azure Service Health

### M1.33
Which resource is REQUIRED when creating an Azure VM?
- A. Public IP address
- B. Load balancer
- C. Virtual network
- D. Availability set

## Section 3 — Management and governance

### M1.34
Which tool estimates the monthly cost of Azure resources before you deploy them?
- A. Cost Management
- B. Pricing calculator
- C. Azure Advisor
- D. Azure Monitor

### M1.35
You want to see costs per department on a single subscription. What should you use?
- A. Resource locks
- B. Tags
- C. Availability sets
- D. Management groups

### M1.36
Yes/No:
1. Tags applied to a resource group are inherited by its resources automatically.
2. Azure Policy can require that resources have a specific tag.
3. A resource can have up to 50 tags.

### M1.37
What happens when a Cost Management budget reaches 100% by default?
- A. Resources are deleted
- B. An alert is sent to configured recipients
- C. The subscription is disabled
- D. VMs are deallocated

### M1.38
Which service enforces that VMs can be created only in specific regions?
- A. RBAC
- B. Azure Policy
- C. Resource locks
- D. Azure Advisor

### M1.39
A ReadOnly lock is applied to a resource group. What can an Owner do with a VM in that group?
- A. Delete it
- B. Resize it
- C. View it
- D. Change its tags

### M1.40
Which service helps discover and classify sensitive data across on-premises, multi-cloud and SaaS sources?
- A. Microsoft Purview
- B. Azure Policy
- C. Azure Arc
- D. Azure Monitor

### M1.41
Which tool provides a browser-based Bash or PowerShell experience with Azure tools preinstalled?
- A. Azure portal dashboards
- B. Azure Cloud Shell
- C. Azure Arc
- D. Azure Storage Explorer

### M1.42
Which service lets you manage and apply Azure Policy to servers running in AWS?
- A. Azure Arc
- B. Azure Migrate
- C. ExpressRoute
- D. Azure Data Box

### M1.43
ARM templates use which format and approach?
- A. YAML, imperative
- B. JSON, declarative
- C. XML, imperative
- D. Python, declarative

### M1.44
Which service do all Azure management tools (portal, CLI, PowerShell) send requests through?
- A. Azure Monitor
- B. Azure Resource Manager
- C. Azure Advisor
- D. Microsoft Entra Domain Services

### M1.45
Which service provides recommendations in the categories Reliability, Security, Performance, Cost and Operational excellence?
- A. Azure Monitor
- B. Azure Advisor
- C. Service Health
- D. Defender for Cloud

### M1.46
You want to be notified about planned Azure maintenance affecting the regions you use. What should you configure?
- A. Azure Monitor metric alert
- B. Service Health alert
- C. Azure Advisor
- D. Activity log export

### M1.47
Which Azure Monitor feature lets you run KQL queries over collected logs?
- A. Application Insights
- B. Log Analytics
- C. Azure Advisor
- D. Resource Health

### M1.48
Developers want to find which external API call is making their web app slow. What should they use?
- A. Application Insights
- B. Azure Advisor
- C. Service Health
- D. Cost Management

### M1.49
Yes/No:
1. Resource locks apply to all users, including Owners.
2. A Delete lock prevents modification of a resource.
3. Locks can be applied at the subscription level.

### M1.50
Sentence completion: "To find out whether your individual VM was affected by an Azure platform problem last night, use \_\_\_\_\_."
- A. Azure status
- B. Resource Health
- C. Azure Advisor
- D. Pricing calculator

---
---

## Answer key with explanations

<details><summary><b>Show answer key</b></summary>

| Q | Ans | Why (and the trap) | Revise |
|---|---|---|---|
| M1.01 | **B** | Consumption = pay for what you use | 01 |
| M1.02 | **B** | Private = full control, highest CapEx | 01 |
| M1.03 | **Yes / No / Yes** | SaaS app code is the provider's; data is always yours | 01 |
| M1.04 | **B** | PaaS — your code, no servers | 01 |
| M1.05 | **B** | Automatic = elasticity | 01 |
| M1.06 | **B** | Pay per execution; servers hidden | 01 |
| M1.07 | **C** | 0.9995 × 0.9999 ≈ 99.94% — lower than both | 01 |
| M1.08 | **B** | OpEx deducted in the same period | 01, 10 |
| M1.09 | **C** | On-prem + public = hybrid (cloud bursting) | 01 |
| M1.10 | **B** | Physical = always Microsoft | 01 |
| M1.11 | **B** | Spot — up to ~90% off, evictable | 01 |
| M1.12 | **A** | Governance | 01 |
| M1.13 | **B** | Bigger VM = scale up (vertical) | 01 |
| M1.14 | **C** | Lift-and-shift = IaaS | 01 |
| M1.15 | **C** | Minimum three zones | 02 |
| M1.16 | **C** | Deleting RG deletes contents (unless locked); RGs can't nest; resources can be in other regions | 02 |
| M1.17 | **B** | MG → Sub → RG → Resource | 02 |
| M1.18 | **B** | Zones = separate datacentres; sets = racks only | 02, 03 |
| M1.19 | **B** | App Service supports Python, no OS management | 03 |
| M1.20 | **C** | ExpressRoute = private circuit | 03 |
| M1.21 | **Yes / No / Yes** | Global peering exists; non-transitive | 03 |
| M1.22 | **B** | Azure Files = SMB shares | 04 |
| M1.23 | **B** | ZRS | 04 |
| M1.24 | **B** | RA- = read access to secondary anytime | 04 |
| M1.25 | **D** | Archive: 180 days, offline | 04 |
| M1.26 | **B** | Large data + slow link = Data Box | 04 |
| M1.27 | **B** | Azure Migrate hub; Arc manages, doesn't migrate | 04, 08 |
| M1.28 | **B** | Entra Domain Services | 05 |
| M1.29 | **B** | Conditional Access | 05 |
| M1.30 | **B** | Contributor can't grant access | 05 |
| M1.31 | **D** | Zero Trust removes implicit network trust | 05 |
| M1.32 | **B** | Defender for Cloud — secure score, multi-cloud | 05 |
| M1.33 | **C** | VNet (+ subnet, NIC) required; public IP optional | 03 |
| M1.34 | **B** | Pricing calculator = estimate before | 06 |
| M1.35 | **B** | Tags + cost analysis grouped by tag | 06 |
| M1.36 | **No / Yes / Yes** | Tags aren't inherited by default | 06 |
| M1.37 | **B** | Budgets alert; automation needs action groups | 06 |
| M1.38 | **B** | Policy "Allowed locations" | 07 |
| M1.39 | **C** | ReadOnly: read only — even Owner (until lock removed) | 07 |
| M1.40 | **A** | Purview | 07 |
| M1.41 | **B** | Cloud Shell | 08 |
| M1.42 | **A** | Arc extends Azure management to AWS | 08 |
| M1.43 | **B** | JSON, declarative | 08 |
| M1.44 | **B** | ARM | 08 |
| M1.45 | **B** | Advisor's five categories | 09 |
| M1.46 | **B** | Service Health alert | 09 |
| M1.47 | **B** | Log Analytics (KQL) | 09 |
| M1.48 | **A** | Application Insights — dependency tracking | 09 |
| M1.49 | **Yes / No / Yes** | Delete lock still allows modification | 07 |
| M1.50 | **B** | Resource Health = individual resource | 09 |

**Scoring:** count each Yes/No set as 1 mark only if all three are right (strict practice). 43+ = ready for Mock 2.

</details>
