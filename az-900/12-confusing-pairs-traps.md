# 12 — Confusing Pairs & Exam Traps

> **Prerequisites:** files 01–11. Read this twice — these look-alikes cause most failed attempts.

## 1. The 60 look-alikes

| # | This… | …vs this | The difference in one line |
|---|---|---|---|
| 1 | CapEx | OpEx | Upfront asset (depreciated) vs pay-as-you-use (expensed now) |
| 2 | Scalability | Elasticity | *Can* scale vs scales *automatically* with demand |
| 3 | Scale up / down | Scale out / in | Bigger/smaller machine (vertical) vs more/fewer machines (horizontal) |
| 4 | High availability | Reliability | Staying up (SLA %) vs recovering from failure (often multi-region) |
| 5 | Hybrid cloud | Multi-cloud | On-prem + public vs two or more public providers |
| 6 | IaaS | PaaS | You manage the OS vs Microsoft manages the OS |
| 7 | PaaS | SaaS | You deploy your code vs you just use the finished app |
| 8 | Serverless | PaaS | Event-driven, scale-to-zero, pay-per-execution vs always-allocated plan (e.g. App Service plan) |
| 9 | Availability set | Availability zone | Racks in one datacentre (99.95%) vs separate datacentres in a region (99.99%) |
| 10 | Availability zone | Region pair | Survives datacentre loss vs survives region loss |
| 11 | Fault domain | Update domain | Shared power/network (rack) vs rebooted together for maintenance |
| 12 | Resource group | Management group | Container for resources vs container for subscriptions |
| 13 | Subscription | Management group | Billing + access boundary vs governance across subscriptions (no bill) |
| 14 | Resource group location | Resource location | RG metadata location vs each resource can be anywhere |
| 15 | VM Scale Sets | Availability sets | Autoscaling identical VMs vs placing VMs on different racks (no autoscale) |
| 16 | Container Instances | Kubernetes Service | Single container, no orchestration vs full orchestration of many |
| 17 | Container Apps | AKS | Serverless containers, no cluster management vs you manage Kubernetes node pools |
| 18 | VPN Gateway | ExpressRoute | Encrypted over internet vs private circuit, not internet (not encrypted by default) |
| 19 | Site-to-site | Point-to-site | Whole office vs single device |
| 20 | VNet peering | VPN Gateway (VNet-to-VNet) | Backbone, no gateway, non-transitive vs encrypted tunnel via gateways |
| 21 | Private endpoint | Public endpoint | Private IP inside your VNet vs internet-reachable address |
| 22 | Private endpoint | Service endpoint | Service gets a private IP in your VNet vs service keeps public IP but only accepts your VNet |
| 23 | Azure DNS | Domain registrar | Hosts DNS records vs sells domain names (Azure DNS can't sell domains) |
| 24 | LRS | ZRS | 3 copies in one datacentre vs 3 copies across zones |
| 25 | GRS | RA-GRS | Secondary readable only after failover vs readable anytime |
| 26 | GRS | GZRS | LRS in primary vs ZRS in primary (both copy to secondary region) |
| 27 | Cool | Cold | 30-day minimum vs 90-day minimum (both online) |
| 28 | Cold | Archive | Online (ms) vs offline (rehydrate up to 15 h), 180-day minimum |
| 29 | Blob storage | Azure Files | Object storage via HTTP vs mountable SMB/NFS file shares |
| 30 | Queue storage | Table storage | Messages between components vs NoSQL key-attribute data |
| 31 | AzCopy | Storage Explorer | Command line vs GUI (uses AzCopy inside) |
| 32 | Azure File Sync | AzCopy sync | Continuous sync + local cache for Windows Server ↔ Azure Files vs on-demand one-way copy |
| 33 | Azure Migrate | Azure Arc | Move workloads into Azure vs manage workloads where they are |
| 34 | Azure Migrate | Azure Data Box | Hub for discovery/assessment/migration vs physical device for offline data |
| 35 | Entra ID | Entra Domain Services | Modern cloud identity (OAuth/SAML) vs managed legacy domain (LDAP, Kerberos, GPO) |
| 36 | Authentication | Authorisation | Who you are (Entra ID) vs what you can do (RBAC) |
| 37 | RBAC | Azure Policy | Who can act vs what configurations are allowed (applies even to Owners) |
| 38 | Azure Policy | Resource lock | Rules about properties vs block delete/modify of specific resources |
| 39 | Delete lock | ReadOnly lock | Can modify, can't delete vs can't modify or delete |
| 40 | Owner | Contributor | Both manage everything; only Owner can grant access |
| 41 | Azure RBAC roles | Entra roles | Manage Azure resources vs manage directory (users, licences) |
| 42 | B2B collaboration | External ID (customers) / B2C | Partner staff as guests vs consumers of your public app |
| 43 | Conditional Access | MFA | Decides *when* to require controls vs the control itself |
| 44 | Zero Trust | Defense in depth | Security strategy "never trust, always verify" vs layered controls model |
| 45 | Defender for Cloud | Azure Advisor | Security posture + threat protection vs recommendations across 5 pillars |
| 46 | Defender for Cloud | Microsoft Purview | Protect workloads/resources vs govern and protect data |
| 47 | Pricing calculator | Cost Management | Estimate future cost vs analyse actual cost, budgets |
| 48 | Cost Management | Azure Advisor | Track/budget spend vs recommend savings |
| 49 | Tags | Resource groups | Labels (many per resource, cross-cutting) vs one container per resource |
| 50 | Azure Monitor | Service Health | Your resources' behaviour vs Microsoft platform issues |
| 51 | Service Health | Azure status | Personalised to your services/regions vs global public page |
| 52 | Service Health | Resource Health | Your services & regions vs one specific resource |
| 53 | Application Insights | Log Analytics | App performance monitoring vs querying logs with KQL |
| 54 | Activity log | Application logs | Who changed Azure resources vs what your app did |
| 55 | ARM | ARM template | The management service vs the JSON file deployed through it |
| 56 | ARM template | Bicep | JSON vs simpler DSL that compiles to JSON |
| 57 | Declarative IaC | Imperative scripts | Desired end state vs step-by-step commands |
| 58 | Cloud Shell | Azure CLI | Browser-based place to run tools vs the tool itself |
| 59 | Reserved instance | Savings plan | Specific VM size/region vs flexible hourly spend commitment |
| 60 | Spot VM | Reserved instance | Cheapest but evictable vs discounted with commitment, not evictable |

---

## 2. "Absolute word" traps — all of these are FALSE

1. Moving to the cloud **always** reduces costs.
2. Microsoft is responsible for **all** security in the cloud.
3. **Every** region supports availability zones.
4. **Every** region has a region pair.
5. Availability sets protect against datacentre failure.
6. Peering is transitive.
7. ExpressRoute traffic is encrypted by default.
8. Azure DNS can register (sell) domain names.
9. A subscription can belong to two management groups.
10. Resource groups can be nested.
11. Tags are inherited from resource groups automatically.
12. Owners can delete resources that have a Delete lock (without removing the lock first).
13. Azure Policy deletes existing non-compliant resources.
14. Contributors can assign roles.
15. Archive tier can be the account default.
16. GRS lets you read from the secondary at any time.
17. Premium storage accounts support GRS.
18. Budgets automatically shut down resources (without action groups).
19. Azure Arc migrates servers to Azure.
20. Free and preview services have financially backed SLAs.
21. Serverless means there are no servers.
22. Azure PowerShell runs only on Windows.
23. ARM templates are written in YAML.
24. A deallocated VM bills for compute.
25. A stopped (from inside the OS, not deallocated) VM doesn't bill for compute.

## 3. "Sounds wrong but is TRUE"

1. Resources in one resource group can be in **different regions**.
2. Deleting a resource group **deletes everything** inside (unless locked).
3. Inbound data transfer is **free**.
4. A **Delete lock** still allows **modification**.
5. Locks apply to **Owners** too.
6. Disks **keep billing** when a VM is deallocated.
7. Composite SLA of dependent services is **lower** than each individual SLA.
8. **SSO** usually **improves** security.
9. Defender for Cloud protects **AWS and Google Cloud** resources.
10. Application Insights can monitor apps **on-premises**.
11. Azure Policy applies even to **Owners**.
12. Reserved instances are still **OpEx**.
13. A ReadOnly lock can stop you **listing storage keys**.
14. Brazil South's pair is **outside** Brazil.
15. Entra Domain Services sync is **one-way** (Entra ID → managed domain).

---
➡️ Next: [13 — Mock exam 1](13-mock-exam-1.md)
