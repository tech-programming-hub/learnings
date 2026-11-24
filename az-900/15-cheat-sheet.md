# 15 — Last-Day Cheat Sheet

> Read this the night before and the morning of the exam. Everything here is explained in files 01–12.

## Numbers to memorise

| Topic | Number |
|---|---|
| Pass mark | **700 / 1000** |
| Zones per zone-enabled region | **≥ 3** |
| Region pair distance | usually **≥ 300 miles** |
| Management group depth | **6 levels** (excl. root & subscription) |
| Management groups per directory | **10,000** |
| Tags per resource | **50** |
| Availability set | **3** fault domains, **5** update domains default (max **20**) |
| VM SLA | single Premium SSD **99.9%** · availability set **99.95%** · zones **99.99%** |
| SLA downtime/month | 99.9% ≈ **44 min** · 99.95% ≈ **22 min** · 99.99% ≈ **4.4 min** |
| Storage durability | LRS **11 nines** · ZRS **12** · GRS/GZRS **16** |
| Copies | LRS 3 · ZRS 3 (across zones) · GRS/GZRS 6 (2 regions) |
| Tier minimums | Cool **30** · Cold **90** · Archive **180** days |
| Archive rehydration | up to **15 hours** |
| Data Box usable capacity | **80 TB** (exam/Learn figure; newer devices 120 / 525 TB) |
| Storage account name | **3–24** lowercase letters + numbers, globally unique |
| Queue message max | **64 KB** |
| Spot discount | up to **~90%** · Reserved up to **~72%** · Savings plan up to **~65%** |
| Free account | **USD 200** credit / 30 days + 20+ services free 12 months + 65+ always-free |
| Cloud Shell idle timeout | **~20 min** |

## One-line service map

| If you need to… | Use |
|---|---|
| Run code on an event, no servers | **Azure Functions** (code) / **Logic Apps** (workflow) |
| Full OS control | **Virtual Machines** |
| Auto-scale identical VMs | **VM Scale Sets** |
| Survive rack failure | **Availability set** |
| Survive datacentre failure | **Availability zones** / ZRS |
| Survive region failure | **Region pair** / GRS / GZRS |
| Virtual desktops, multi-session | **Azure Virtual Desktop** |
| Host web app/API, no OS | **App Service** |
| One container, quick | **Container Instances** |
| Serverless microservices containers | **Container Apps** |
| Full Kubernetes | **AKS** |
| Private network in Azure | **Virtual network** (+ subnets, NSGs) |
| Connect two VNets | **VNet peering** (global for regions) |
| Office ↔ Azure, encrypted over internet | **Site-to-site VPN** |
| One laptop ↔ Azure | **Point-to-site VPN** |
| Private dedicated line, no internet | **ExpressRoute** |
| Host DNS records | **Azure DNS** (can't buy domains) |
| PaaS service on private IP | **Private endpoint** |
| Unstructured objects | **Blob** |
| SMB file shares | **Azure Files** |
| Messages between apps | **Queue** |
| NoSQL key-value | **Table** |
| VM disks | **Managed Disks** |
| Copy via script | **AzCopy** |
| Copy via GUI | **Storage Explorer** |
| Sync Windows file server ↔ cloud | **Azure File Sync** |
| Discover/assess/migrate | **Azure Migrate** |
| Offline bulk data | **Azure Data Box** |
| Cloud identity, SSO, MFA | **Microsoft Entra ID** |
| Legacy LDAP/Kerberos/GPO, no DCs | **Entra Domain Services** |
| Sync on-prem AD → Entra ID | **Entra Connect** |
| Partners with own accounts | **B2B collaboration** |
| Customers sign up | **Entra External ID** (formerly Azure AD B2C) |
| "If risky then MFA/block" | **Conditional Access** (needs P1) |
| Who can do what on resources | **RBAC** |
| Secure score, threat protection, multi-cloud | **Defender for Cloud** |
| Estimate cost before | **Pricing calculator** |
| Actual spend, budgets, alerts | **Cost Management** |
| Labels for cost/ops | **Tags** |
| Data discovery, classification, DLP | **Microsoft Purview** |
| Enforce configuration rules | **Azure Policy** |
| Prevent delete / change | **Resource locks** |
| Web GUI | **Azure portal** |
| Browser shell, pre-authenticated | **Cloud Shell** |
| `az ...` commands | **Azure CLI** |
| `Verb-AzNoun` cmdlets | **Azure PowerShell** |
| Manage non-Azure servers/K8s | **Azure Arc** |
| Declarative IaC | **ARM templates (JSON)** / **Bicep** |
| The management layer under every tool | **Azure Resource Manager** |
| Recommendations (5 pillars) | **Azure Advisor** |
| Azure outages/maintenance for you | **Service Health** |
| Your one resource's health | **Resource Health** |
| Global public status | **Azure status** |
| Metrics, logs, alerts | **Azure Monitor** |
| KQL queries | **Log Analytics** |
| App performance | **Application Insights** |
| Who changed a resource | **Activity log** |

## Mnemonics

- **Hierarchy:** *My Students Read Regularly* → Management group · Subscription · Resource group · Resource.
- **Always-customer responsibilities:** *DDA* → Data, Devices, Accounts.
- **Defense in depth (out→in):** *Please Inspect Perimeter Networks Carefully And Data* → Physical, Identity, Perimeter, Network, Compute, Application, Data.
- **Zero Trust:** *Verify, Least, Assume* → Verify explicitly · Least privilege · Assume breach.
- **Advisor pillars:** *Real Security Pros Cut Ops* → Reliability, Security, Performance, Cost, Operational excellence.
- **Redundancy cheapest→dearest:** LRS < ZRS < GRS < RA-GRS < GZRS < RA-GZRS.
- **Tiers cheapest storage→dearest:** Archive < Cold < Cool < Hot (access cost is the reverse).

## Ten final reminders

1. "Always / never / only / guaranteed" → usually **No**.
2. Policy = **what**; RBAC = **who**; Lock = **don't delete/change**.
3. Advisor = **recommend**; Monitor = **observe & alert**; Service Health = **Microsoft's problems**.
4. Calculator = **before**; Cost Management = **after**.
5. Arc = **manage where it is**; Migrate = **move it**.
6. VPN = **encrypted internet**; ExpressRoute = **private, not encrypted by default**.
7. Sets = rack; Zones = datacentre; Pairs = region.
8. Archive = offline, rehydrate, 180 days, can't be account default.
9. Tags **not inherited**; RGs **not nested**; resources can be in **other regions** than their RG.
10. No negative marking — **answer everything**; Yes/No sets can't be revisited.

Good luck! 🎯
