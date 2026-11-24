# 14 — Mock Exam 2 (50 questions, harder, ~45 minutes)

> More scenarios, more "NOT/least/minimise" wording, more Yes/No series. Target **≥ 43/50**.
> Cloud concepts Q1–14 · Architecture & services Q15–33 · Management & governance Q34–50.

---

## Section 1 — Cloud concepts

### M2.01
A company says: "After moving to Azure, we no longer need to worry about any aspect of security." Which concept shows this is wrong?
- A. Consumption-based model
- B. Shared responsibility model
- C. Elasticity
- D. Hybrid cloud

### M2.02
Which TWO are benefits of the consumption-based model? (Each is a complete solution.)
- A. No upfront infrastructure costs
- B. Guaranteed lower total cost in all scenarios
- C. Ability to stop paying for resources you no longer need
- D. Fixed monthly cost regardless of usage

### M2.03
Yes/No:
1. A private cloud can be hosted by a third-party provider and dedicated to one organisation.
2. Multi-cloud means combining on-premises and one public cloud.
3. Azure Arc can help manage a multi-cloud environment.

### M2.04
Which workload is the WORST fit for Spot VMs?
- A. Image rendering
- B. CI build agents
- C. A customer-facing payment database
- D. Large-scale data analysis jobs with checkpoints

### M2.05
A team needs to install a custom antivirus agent and kernel-level driver on its servers. Which service type is required?
- A. SaaS
- B. PaaS
- C. IaaS
- D. Serverless

### M2.06
Which statement describes "management OF the cloud"?
- A. Using the Azure CLI to create resources
- B. Automatically scaling resources and deploying from templates
- C. Using the portal
- D. Calling the REST API

### M2.07
An SLA of 99.99% allows approximately how much downtime per month?
- A. 4.4 minutes
- B. 22 minutes
- C. 44 minutes
- D. 8.8 hours

### M2.08
A company has a steady compute budget and plans to switch VM families and regions during the next 3 years. Which option gives a discount while keeping flexibility?
- A. Reserved instances for one VM size
- B. Azure savings plan for compute
- C. Spot VMs
- D. Dev/Test pricing for production

### M2.09
Which is NOT a characteristic of serverless?
- A. Event-driven execution
- B. Automatic scaling
- C. Full control over the underlying OS
- D. Pay per execution

### M2.10
In PaaS, which responsibility is SHARED between customer and Microsoft?
- A. Physical network
- B. Identity and directory infrastructure
- C. Physical hosts
- D. Datacentre

### M2.11
A newspaper's website suddenly gets 30× traffic after breaking news and stays online because instances are added automatically. Which TWO benefits are demonstrated?
- A. Elasticity and high availability
- B. Governance and compliance
- C. CapEx and depreciation
- D. Sovereignty and isolation

### M2.12
Which statement about reserved instances is TRUE?
- A. They are a CapEx purchase
- B. They provide discounts in exchange for a 1- or 3-year commitment
- C. They can be evicted at any time
- D. They are only for Linux

### M2.13
A company must keep using an on-premises mainframe for its ledger due to regulation, but wants a new mobile app to scale globally. Which model best fits?
- A. Private
- B. Public
- C. Hybrid
- D. On-premises only

### M2.14
Which of these is an example of SaaS?
- A. Azure Virtual Machines
- B. Azure SQL Database
- C. Microsoft 365 / Dynamics 365
- D. Azure Kubernetes Service

## Section 2 — Azure architecture and services

### M2.15
Yes/No:
1. Most region pairs are located in the same geography.
2. During planned updates, Azure updates both regions in a pair at the same time.
3. Some Azure regions do not have a pair.

### M2.16
A company needs to deploy to a region that guarantees data is managed by screened US personnel for a federal contract. Which should it choose?
- A. East US
- B. Azure Government
- C. Azure China
- D. Central US with ZRS

### M2.17
A management group hierarchy can be how many levels deep, excluding the root and subscription levels?
- A. 3
- B. 6
- C. 8
- D. 12

### M2.18
You place two VMs in an availability set. What does this protect against?
- A. Region outage
- B. Zone outage
- C. A rack-level hardware failure
- D. Accidental deletion

### M2.19
A VM-based app needs the highest availability within one region. Which deployment provides a 99.99% SLA?
- A. One VM with Premium SSD
- B. Two VMs in an availability set
- C. Two or more VMs across two or more availability zones
- D. One VM in a scale set

### M2.20
A startup has containerised microservices and wants serverless scaling to zero, built-in ingress and no Kubernetes cluster management. What should it choose?
- A. AKS
- B. Azure Container Apps
- C. Azure Virtual Machines
- D. Azure Container Instances

### M2.21
You need to resolve names for VMs inside your VNets using custom names like `db01.internal.contoso.com`, not visible on the internet. What should you use?
- A. Azure DNS public zone
- B. Azure DNS private zone
- C. A domain registrar
- D. Azure Front Door

### M2.22
Your VNet must connect to on-premises. Traffic must be encrypted and you have a limited budget. What should you deploy?
- A. ExpressRoute Direct
- B. Site-to-site VPN Gateway
- C. VNet peering
- D. A private endpoint only

### M2.23
Which is TRUE about ExpressRoute?
- A. It is encrypted by default
- B. It routes through the public internet
- C. It is provided through a connectivity provider and offers predictable performance
- D. Only one Azure VNet can ever use it

### M2.24
A company wants its Azure Storage account accessible only via a private IP address in its VNet. What should it create?
- A. A public endpoint
- B. A private endpoint
- C. A resource lock
- D. An NSG on the storage account

### M2.25
Which storage redundancy is the CHEAPEST option that survives a regional outage?
- A. ZRS
- B. GRS
- C. RA-GZRS
- D. LRS

### M2.26
You delete a Cold-tier blob 30 days after uploading it. What happens?
- A. Nothing extra is charged
- B. You pay an early-deletion fee for the remaining 60 days
- C. You pay for 180 days
- D. The deletion is blocked

### M2.27
Which statement about Azure File Sync is TRUE?
- A. It syncs Linux servers with Blob storage
- B. It can cache an Azure file share on Windows Servers and tier cold files to the cloud
- C. It ships disks to Microsoft
- D. It's a command-line copy tool

### M2.28
Which storage account type should you choose for most scenarios needing Blob, Files, Queue and Table with geo-redundancy options?
- A. Premium block blobs
- B. Premium file shares
- C. Standard general-purpose v2
- D. Premium page blobs

### M2.29
A partner company's staff need access to your SharePoint site using their own work credentials. What should you use?
- A. B2B collaboration
- B. Entra Domain Services
- C. RBAC Owner
- D. Entra Connect

### M2.30
A user has Reader on a subscription and Contributor on resource group RG1. What can they do?
- A. Only read everything
- B. Read everything, and manage resources in RG1
- C. Manage all resources in the subscription
- D. Nothing, because the roles conflict

### M2.31
Arrange the layers of defense in depth from outermost to innermost (choose correct order):
- A. Physical → Identity & access → Perimeter → Network → Compute → Application → Data
- B. Perimeter → Physical → Network → Identity → Data → Compute → Application
- C. Data → Application → Compute → Network → Perimeter → Identity → Physical
- D. Identity → Network → Physical → Perimeter → Compute → Data → Application

### M2.32
Which passwordless method suits a user who has their own Windows 11 laptop with a fingerprint reader?
- A. Windows Hello for Business
- B. SMS one-time code
- C. Security questions
- D. Shared password

### M2.33
Yes/No:
1. Conditional Access requires Microsoft Entra ID P1 or higher.
2. Conditional Access can block sign-ins from specific countries.
3. Conditional Access controls which Azure VM sizes can be deployed.

## Section 3 — Management and governance

### M2.34
Which factor does NOT affect the cost of Azure resources?
- A. Region
- B. Outbound data transfer
- C. Resource type and size
- D. The resource group's name

### M2.35
A manager asks: "How much did each project spend last quarter, and are we on track this month?" Which tool?
- A. Pricing calculator
- B. Cost Management (cost analysis + forecast)
- C. Azure Monitor metrics
- D. Azure Service Health

### M2.36
You must ensure that every new resource inherits the `CostCenter` tag of its resource group. What should you use?
- A. Resource lock
- B. Azure Policy (inherit tag from resource group)
- C. RBAC
- D. Management group

### M2.37
Which statement about Azure Policy is FALSE?
- A. It can deny creation of non-compliant resources
- B. It can audit existing resources
- C. It deletes existing non-compliant resources automatically
- D. It can be assigned at management group level

### M2.38
Which combination ensures that (i) nobody can create resources outside India and (ii) a critical VNet cannot be deleted?
- A. (i) RBAC, (ii) Policy
- B. (i) Policy, (ii) Delete lock
- C. (i) Delete lock, (ii) Policy
- D. (i) Tags, (ii) RBAC

### M2.39
You applied a Delete lock to a storage account. A user with Storage Blob Data Contributor deletes blobs inside it. What happens?
- A. Blob deletion is blocked by the lock
- B. Blob deletion succeeds, because locks protect the management plane, not data operations
- C. The storage account is deleted
- D. The lock converts to ReadOnly

### M2.40
Which solution helps prevent employees from sharing documents containing credit-card numbers outside the organisation?
- A. Microsoft Purview data loss prevention
- B. Azure Policy
- C. Azure Advisor
- D. Network security group

### M2.41
Which Bicep statement is TRUE?
- A. It is imperative
- B. It compiles to ARM template JSON
- C. It is only for AWS
- D. It requires a state file like Terraform

### M2.42
Your team must redeploy an identical environment in a new region with the least effort and risk of mistakes. What should you use?
- A. Azure portal manual deployment
- B. Infrastructure as code (Bicep/ARM templates)
- C. Azure Advisor
- D. Azure Storage Explorer

### M2.43
Yes/No:
1. Azure Arc can bring Kubernetes clusters in other clouds under Azure management.
2. Azure Arc is required to use Azure CLI on Linux.
3. Defender for Cloud can protect Arc-enabled on-premises servers.

### M2.44
Which TWO tools can be used to manage Azure from a macOS terminal? (Each is a complete solution.)
- A. Azure CLI
- B. Azure PowerShell
- C. Azure Data Box
- D. Azure Service Health

### M2.45
You need to know who deleted a resource group yesterday. Where do you look?
- A. Azure Advisor
- B. Activity log
- C. Application Insights
- D. Azure status

### M2.46
Which is the best tool to be alerted when your web app's failed-request rate exceeds 5%?
- A. Azure Advisor
- B. Azure Monitor alert (Application Insights metric) with an action group
- C. Service Health
- D. Azure Policy

### M2.47
A CTO wants a single score reflecting how well resources follow best practices for cost, reliability, performance, security and operations. Which feature?
- A. Advisor Score
- B. Secure score
- C. Composite SLA
- D. Resource Health

### M2.48
Which provides a public, global page of Azure service health across all regions, without signing in?
- A. Service Health
- B. Resource Health
- C. Azure status
- D. Log Analytics

### M2.49
Yes/No:
1. Azure Monitor can collect data from on-premises servers.
2. Application Insights can only monitor apps hosted in Azure App Service.
3. Azure Monitor alerts can run an automation runbook.

### M2.50
Drag-drop: match each requirement to the best service: (i) Estimate cost of a planned solution · (ii) Get alerted at 80% of monthly spend · (iii) Get recommendations to cut cost.
- A. (i) Pricing calculator · (ii) Cost Management budget · (iii) Azure Advisor
- B. (i) Advisor · (ii) Pricing calculator · (iii) Cost Management
- C. (i) Cost Management · (ii) Advisor · (iii) Pricing calculator
- D. (i) Pricing calculator · (ii) Service Health · (iii) Azure Monitor

---
---

## Answer key with explanations

<details><summary><b>Show answer key</b></summary>

| Q | Ans | Why (and the trap) | Revise |
|---|---|---|---|
| M2.01 | **B** | Customer always keeps data, devices, identities | 01 |
| M2.02 | **A, C** | "Guaranteed lower cost" is the absolute-word trap | 01 |
| M2.03 | **Yes / No / Yes** | Hosted private cloud exists; multi-cloud = 2+ public providers | 01 |
| M2.04 | **C** | Evictable VMs are wrong for production databases | 01 |
| M2.05 | **C** | Kernel/driver control = IaaS | 01 |
| M2.06 | **B** | *Of* = what happens to resources; *in* = tools you use | 01 |
| M2.07 | **A** | 99.99% ≈ 4.38 min/month | 01 |
| M2.08 | **B** | Savings plan = spend commitment, flexible | 01 |
| M2.09 | **C** | No OS control in serverless | 01 |
| M2.10 | **B** | Identity infrastructure, apps, network controls are shared in PaaS | 01 |
| M2.11 | **A** | Automatic scaling + staying up | 01 |
| M2.12 | **B** | Still OpEx; not evictable | 01, 10 |
| M2.13 | **C** | Regulated on-prem + scalable cloud = hybrid | 01 |
| M2.14 | **C** | Finished apps = SaaS | 01 |
| M2.15 | **Yes / No / Yes** | Brazil South is the cross-geography exception (so "always" would be No). Updates go to one region of a pair at a time | 02 |
| M2.16 | **B** | Sovereign US region | 02 |
| M2.17 | **B** | 6 levels | 02 |
| M2.18 | **C** | Sets = racks (fault domains) | 03 |
| M2.19 | **C** | Zones → 99.99% | 03 |
| M2.20 | **B** | Container Apps = serverless containers, no cluster ops | 03 |
| M2.21 | **B** | Private DNS zones resolve inside VNets | 03 |
| M2.22 | **B** | Encrypted + budget = S2S VPN | 03 |
| M2.23 | **C** | Private ≠ encrypted; provider-based | 03 |
| M2.24 | **B** | Private endpoint = private IP | 03 |
| M2.25 | **B** | GRS is cheapest geo option | 04 |
| M2.26 | **B** | Cold minimum 90 days → 90 − 30 = 60 days charged | 04 |
| M2.27 | **B** | File Sync = Windows Server cache + cloud tiering | 04 |
| M2.28 | **C** | GPv2 = default, all services, all redundancy | 04 |
| M2.29 | **A** | B2B guests use own identities | 05 |
| M2.30 | **B** | RBAC is additive | 05 |
| M2.31 | **A** | Physical outermost, Data innermost | 05 |
| M2.32 | **A** | Windows Hello for Business = personal Windows device biometrics | 05 |
| M2.33 | **Yes / Yes / No** | VM sizes = Azure Policy | 05, 07 |
| M2.34 | **D** | Names don't affect price | 06 |
| M2.35 | **B** | Actual spend + forecast | 06 |
| M2.36 | **B** | Tags aren't inherited — Policy can do it | 06, 07 |
| M2.37 | **C** | Policy flags, doesn't delete | 07 |
| M2.38 | **B** | Policy for "what"; lock for "don't delete" | 07 |
| M2.39 | **B** | Locks = management plane only | 07 |
| M2.40 | **A** | DLP is part of Purview | 07 |
| M2.41 | **B** | Bicep transpiles to ARM JSON; no state file | 08 |
| M2.42 | **B** | IaC = repeatable | 08 |
| M2.43 | **Yes / No / Yes** | CLI needs no Arc | 08 |
| M2.44 | **A, B** | Both are cross-platform | 08 |
| M2.45 | **B** | Activity log = who did what | 09 |
| M2.46 | **B** | Monitor alert on App Insights metric | 09 |
| M2.47 | **A** | Advisor Score (secure score is security only) | 09 |
| M2.48 | **C** | Azure status = global/public | 09 |
| M2.49 | **Yes / No / Yes** | App Insights works anywhere | 09 |
| M2.50 | **A** | Estimate → calculator; alert → budget; recommend → Advisor | 06, 09 |

</details>
