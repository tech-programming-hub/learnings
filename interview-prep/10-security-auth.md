# 10 — Security: OAuth 2.0, OIDC, JWT, SAML, RBAC

> Anchor: JD explicitly requires OAuth2, OIDC, JWT, SAML, RBAC. Know the flows cold.

---

## A. Authentication vs Authorization

### Q1. Authentication vs Authorization?
These are the two foundational security concepts, and they answer two different questions in sequence:
- **Authentication (AuthN)** — **"Who are you?"** It's the process of **verifying identity** — proving you are who you claim to be, via credentials (username/password), tokens, biometrics, or certificates. Like showing your ID at the airport.
- **Authorization (AuthZ)** — **"What are you allowed to do?"** Once your identity is established, this determines **which resources/actions you're permitted** — enforced via roles, scopes, and permissions. Like your boarding pass granting access to a specific gate/seat.
The order matters: you **authenticate first**, then the system **authorizes** each action. A common interview point: they're distinct concerns and are often handled by different components (an identity provider does AuthN; the application/gateway enforces AuthZ).

---

## B. OAuth 2.0

### Q2. What is OAuth 2.0?
OAuth 2.0 is an **authorization framework** that lets a third-party app obtain **limited, delegated access** to a user's resources **without ever seeing the user's credentials**. The classic example: letting a photo-printing app access your Google Photos — you grant access without giving the app your Google password. It works by having the user authorize the app, after which an **authorization server** issues the app an **access token** carrying specific **scopes** (permissions). The app then presents that token to the resource server (API) to act on the user's behalf. The critical clarification interviewers look for: **OAuth 2.0 is about *authorization* (delegated access), not authentication** — it doesn't, by itself, tell the app *who the user is* (that's what OIDC adds on top). The whole point is avoiding credential-sharing and enforcing scoped, revocable, least-privilege access.

### Q3. OAuth 2.0 roles?
OAuth defines four roles, and understanding them makes every flow clearer:
- **Resource Owner** — the **user** who owns the data and grants access to it.
- **Client** — the **application** requesting access on the user's behalf (the SPA, mobile app, or backend service).
- **Authorization Server (AS)** — the server that **authenticates the user and issues tokens** (e.g., Keycloak, Auth0, Azure Entra ID, Okta).
- **Resource Server (RS)** — the **API hosting the protected resources**, which validates the access token and serves (or denies) the request.
The flow is essentially: the Client asks the Authorization Server for permission to access the Resource Server on behalf of the Resource Owner.

### Q4. OAuth 2.0 grant types (flows)?
"Grant types" are the different ways a client can obtain a token, each suited to a different scenario:
- **Authorization Code + PKCE** — for **user-facing apps** (web, mobile, SPA). This is the **most secure and recommended** flow. **PKCE** (Proof Key for Code Exchange) protects **public clients** that can't safely store a secret, by tying the code exchange to a one-time secret the client generates.
- **Client Credentials** — for **machine-to-machine** (no user involved); one service authenticates as itself to call another.
- **Refresh Token** — used to obtain a **new access token** without forcing the user to log in again.
- **Device Code** — for **input-constrained devices** (smart TVs, CLIs) where you authorize on a separate device.
- **Deprecated flows:** the **Implicit** flow (returned tokens in the URL — insecure) and **Resource Owner Password** (app handles the password — defeats OAuth's purpose) are no longer recommended.

### Q5. Explain the Authorization Code flow (with PKCE).
This is the gold-standard flow for user-facing apps. Step by step:
1. The client generates a secret `code_verifier` and its hash `code_challenge`, then **redirects the user to the Authorization Server** (passing the `code_challenge`).
2. The user **authenticates and consents** at the Authorization Server (so the client never sees their password).
3. The AS **redirects back to the client's redirect URI with a one-time authorization code**.
4. The client **exchanges that code plus the original `code_verifier`** at the token endpoint for an **access token** (and usually a refresh token + ID token).
5. The client calls the Resource Server with `Authorization: Bearer <access_token>`.
6. The Resource Server **validates the token** and serves the request.
The two-step design (code → token) means the sensitive tokens are never exposed in the browser URL, and **PKCE** ensures that even if the authorization code is intercepted, an attacker can't exchange it without the matching `code_verifier`.

### Q6. What are scopes?
Scopes are **named permissions attached to an access token** that define exactly *what* the token is allowed to do — e.g., `read:orders`, `write:orders`, `profile`, `email`. When the client requests authorization, it asks for specific scopes, the user consents to them, and the issued token is limited to those scopes. The resource server then checks the token's scopes before allowing an operation. Scopes are how OAuth enforces the **principle of least privilege** on tokens: a token minted for read-only access can't be used to modify data, so even if it leaks, the damage is bounded. They keep delegated access **narrow and explicit** rather than all-or-nothing.

### Q7. Access token vs refresh token?
These two tokens have deliberately different lifespans and purposes, and the split is a core security design:
- **Access token** — **short-lived** (minutes to an hour) and sent with **every API call** (`Authorization: Bearer`). Because it's used constantly and could leak, keeping it short-lived **limits the damage** of theft — it expires quickly.
- **Refresh token** — **long-lived** and used **only** to obtain new access tokens when they expire, so the user doesn't have to log in repeatedly. Because it's powerful, it must be **stored securely**, **rotated** on each use, and **revoked on logout**.
The pattern — short access token + refresh token — gives you both good security (small exposure window for the frequently-used token) and good UX (no constant re-logins). It's also how you partly work around JWTs being hard to revoke.


---

## C. OpenID Connect (OIDC)

### Q8. What is OIDC and how does it relate to OAuth2?
OIDC (OpenID Connect) is a thin **authentication layer built on top of OAuth 2.0**. The key insight: OAuth2 alone handles **authorization** (getting an access token to call APIs) but says nothing standardized about **who the user is** — apps used to hack around this. OIDC fixes that by adding a standardized **identity layer**: after the user logs in, the authorization server also issues an **ID token** — a **JWT containing identity claims** like `sub` (unique user ID), `email`, and `name`. So OIDC lets the client actually *know and verify the user's identity*, which is why it powers **Single Sign-On** and **"Login with Google/Microsoft"** buttons. The clean mental model: **OAuth2 = authorization (access), OIDC = authentication (identity) added on top of the same flow.**

### Q9. ID token vs access token?
They look similar (both often JWTs) but have **different audiences and purposes** — a common source of confusion:
- **ID token** (from OIDC) — proves **who the user is**, and is intended **for the client application**. It contains identity claims (`sub`, `name`, `email`) so the app can establish the user's identity and personalize the session. It should **not** be sent to APIs as an access credential.
- **Access token** (from OAuth2) — grants **access to APIs/resources**, and is intended **for the resource server**. It carries scopes/permissions and is what you put in the `Authorization: Bearer` header when calling an API.
Rule of thumb: **ID token = "who you are" (for the app); access token = "what you can access" (for the API).** Using one in place of the other is a security mistake.

### Q10. What is the UserInfo endpoint?
The UserInfo endpoint is a standard **OIDC endpoint that returns the authenticated user's profile claims** (name, email, picture, etc.) when called with a **valid access token**. It exists so the client can fetch up-to-date user profile information **without stuffing all of it into the ID token** (keeping tokens smaller) — or to retrieve additional claims on demand. The client calls it with `Authorization: Bearer <access_token>` and gets back a JSON object of user claims. It's part of how OIDC standardizes obtaining identity information.

---

## D. JWT

### Q11. What is a JWT?
A **JSON Web Token** is a compact, **self-contained, digitally signed** token used to securely transmit claims between parties. "Self-contained" is the key property: the token **carries its own data**, so a receiver can validate and use it **without a database lookup**. It has three base64url-encoded parts separated by dots — `header.payload.signature`:
- **Header** — metadata: the signing algorithm (`alg`, e.g., RS256) and token type.
- **Payload** — the **claims**: standard ones like `sub` (subject/user), `iss` (issuer), `aud` (audience), `exp` (expiry), `iat` (issued-at), plus custom claims like roles/scopes.
- **Signature** — a cryptographic signature over the header+payload, created with either an **HMAC secret** or an **RSA/EC private key**, used to **verify integrity** (that the token wasn't tampered with and came from a trusted issuer).
Crucially, a JWT is **signed, not encrypted** — the payload is only base64-encoded, so anyone can read it. Never put secrets in it.

### Q12. How do you validate a JWT?
Validation is a multi-step check, and skipping any step is a security hole:
1. **Verify the signature** — recompute/verify it using the HMAC secret (symmetric) or the issuer's **public key fetched from its JWKS endpoint** (asymmetric). This proves the token is authentic and untampered.
2. **Check the standard claims:** `exp` (not expired), `nbf` (not used before its valid time), `iss` (issued by a **trusted issuer**), and `aud` (the token's **intended audience is this API** — prevents a token minted for another service being replayed against yours).
3. **Check authorization claims** — the required **scopes/roles** for the requested operation.
In Spring, `oauth2ResourceServer().jwt()` wires this up automatically, fetching keys via JWKS and validating signature/claims on every request. The theme: authenticity (signature) + validity (time/issuer/audience) + permission (scopes).

### Q13. JWT signing: symmetric vs asymmetric?
The choice is about **who needs to hold which key**:
- **HS256 (symmetric)** — uses a **single shared secret** for both signing and verifying. It's simpler and fast, but the secret must be **shared with every party that verifies**, which is risky in distributed systems (any holder can also *forge* tokens). Fine for a single app/monolith.
- **RS256 (asymmetric)** — uses a **key pair**: the authorization server signs with its **private key**, and resource servers verify with the **public key** (published via a **JWKS endpoint**). The private key never leaves the AS, and verifiers only need the public key (which can't forge tokens). This is the **preferred choice for microservices/distributed systems**, because you can safely distribute the public key to many services without risk, and rotate keys via the `kid` header.

### Q14. Stateless JWT vs stateful sessions?
This is a fundamental architecture trade-off between **scalability and revocability**:
- **JWT (stateless)** — the token is self-contained, so the server just verifies the signature with **no server-side session store** and **no lookup**. This **scales beautifully** (any instance can validate; great for microservices). The downside: it's **hard to revoke before expiry** — once issued, a valid token works until it expires, even if you "log the user out."
- **Sessions (stateful)** — the server stores session state (often in **Redis**) and the client holds only a session ID. **Easy to revoke instantly** (delete the session), but requires a **shared session store** and a lookup on each request, adding a scaling dependency.
To get the best of both, the common approach with JWTs is: **short access-token expiry + refresh tokens + a denylist/blacklist for high-value revocations + refresh-token rotation** — mitigating the revocation weakness while keeping statelessness.

### Q15. Where should you store JWTs on the frontend?
This is a security trade-off with no perfect answer, but a clear best practice. Prefer **httpOnly, Secure, SameSite cookies**: because httpOnly cookies **cannot be read by JavaScript**, they **mitigate XSS token theft** (a malicious script can't exfiltrate the token), `Secure` ensures they're only sent over HTTPS, and `SameSite` limits cross-site sending. The catch is that cookie-based auth is susceptible to **CSRF**, so you must add CSRF protection (SameSite=Lax/Strict + CSRF tokens for state-changing requests). The tempting alternative, **`localStorage`**, is convenient but **vulnerable to XSS** — any injected script can read it and steal the token — so it's discouraged for sensitive tokens. A common robust pattern: keep the **refresh token in an httpOnly cookie** and the **short-lived access token in memory**.

### Q16. Common JWT security pitfalls?
The recurring JWT vulnerabilities to know:
- **`alg: none` attack** — an attacker changes the header algorithm to `none` (unsigned) hoping the server accepts it without verifying; always **reject unsigned tokens and pin the expected algorithm**.
- **Weak secrets** — a guessable HMAC secret lets attackers forge tokens; use strong secrets or asymmetric keys.
- **Not validating `aud`/`iss`** — accepting tokens meant for another service or from an untrusted issuer (token substitution).
- **Too-long expiry** — a long-lived token that leaks is dangerous because you can't easily revoke it; keep access tokens short.
- **Storing sensitive data in the payload** — remember the payload is only **base64, not encrypted** — anyone can decode it, so never put passwords/PII/secrets in it.
- **No key/token rotation** — failing to rotate signing keys or refresh tokens increases exposure over time.


---

## E. SAML

### Q17. What is SAML? SAML vs OIDC?
**SAML (Security Assertion Markup Language)** is an older, **XML-based standard for Single Sign-On**, widely used in **enterprise** environments. It works by exchanging **assertions** (signed XML statements about a user's identity and attributes) between two parties: the **IdP (Identity Provider)** — which authenticates the user (e.g., corporate Okta/AD FS) — and the **SP (Service Provider)** — the application the user wants to access. Compared with OIDC:
- **SAML** — **XML**-based, mature/enterprise/legacy, designed primarily for **browser-based web SSO**, and comparatively **heavyweight**.
- **OIDC** — **JSON/JWT**-based, modern, **mobile/SPA/API-friendly**, and **lightweight**.
Both achieve SSO, so the guidance is: choose **OIDC for new applications**, and use **SAML when you must integrate with an existing enterprise IdP** that only speaks SAML. Many enterprises support both.

### Q18. SAML flow (SP-initiated, brief)?
In the SP-initiated flow (the user starts at the application):
1. The user tries to access the **SP** (the application).
2. The SP sees they're not authenticated and **redirects the browser to the IdP** with a **SAML AuthnRequest**.
3. The user **authenticates at the IdP** (enters corporate credentials, does MFA).
4. The IdP **posts a digitally signed SAML assertion** back to the SP (via the browser).
5. The SP **validates the assertion's signature** and the claims, then **creates a local session** for the user.
The essence: the SP delegates authentication to the trusted IdP, and trust is established through the **signed XML assertion**. (There's also an IdP-initiated flow where the user starts from the IdP's portal.)

---

## F. RBAC & Access Control

### Q19. What is RBAC?
**Role-Based Access Control** is an authorization model where **permissions are grouped into roles, and roles are assigned to users** — rather than assigning individual permissions to each user directly. The chain is **User → Role → Permissions**: for example, an `ADMIN` role bundles many permissions, a `MANAGER` role fewer, and a `USER` role the least. Its big advantage is **manageability at scale**: to grant someone a set of capabilities you just assign them a role (and to change what a role can do, you edit the role once and everyone with it is updated). It maps naturally to how organizations think about job functions, making it the most common access-control model. The limitation is that it's **coarse-grained** — it can't easily express context-dependent rules (that's where ABAC comes in).

### Q20. RBAC vs ABAC?
Both are authorization models, differing in **how granular and context-aware** the decision is:
- **RBAC (Role-Based)** — grants access based on the user's **role**. Simple, easy to reason about and audit, but **coarse-grained** — the decision is essentially "does this user have this role?"
- **ABAC (Attribute-Based)** — grants access by evaluating **attributes and policies**: attributes of the *user* (department, clearance), the *resource* (owner, sensitivity), and the *environment* (time of day, location, IP). This is **fine-grained and flexible** — you can express rules like "managers can approve expenses only for their own department, under $10k, during business hours." The cost is **more complexity**, often implemented with a policy engine like **OPA/Rego** or Cedar.
Rule of thumb: **RBAC for straightforward role-based access; ABAC when you need context-sensitive, fine-grained policies.**

### Q21. How do you implement RBAC in Spring / APIs?
The standard pattern flows the user's roles from the token down to enforcement points:
- **Carry roles/scopes in the JWT** — when the user authenticates, the authorization server embeds their roles/scopes as claims in the access token.
- **Enforce declaratively** — in Spring Security, use method-level annotations like `@PreAuthorize("hasRole('ADMIN')")` or `@PreAuthorize("hasAuthority('SCOPE_write:orders')")` so an endpoint only runs if the caller has the required role/scope (Spring maps the JWT claims to authorities).
- **Enforce in layers** — check at the **API gateway** (coarse filtering at the edge) *and* at the **service** (defense in depth; never rely on the gateway alone), always applying the **principle of least privilege**.
The key idea: authentication establishes identity+roles (in the token), and authorization consistently enforces those roles at every protected operation.

---

## G. General API/App Security

### Q22. OWASP Top 10 (know a few)?
The **OWASP Top 10** is the industry-standard list of the **most critical web application security risks**, maintained by the Open Web Application Security Project — it's the checklist developers use to ensure they've addressed the common, dangerous vulnerabilities. Key ones to know: **Injection** (e.g., SQL injection), **Broken Authentication**, **Sensitive Data Exposure**, **XXE** (XML external entities), **Broken Access Control** (often #1 — users accessing things they shouldn't, like IDOR), **Security Misconfiguration**, **XSS** (Cross-Site Scripting), **Insecure Deserialization**, **Using Components with Known Vulnerabilities**, and **Insufficient Logging & Monitoring**. In an interview, it's good to mention you "follow OWASP guidelines" and can speak to preventing at least a few (injection → parameterized queries; broken access control → server-side authorization checks; XSS → output encoding).

### Q23. How do you prevent SQL injection?
SQL injection happens when untrusted input is **concatenated directly into a SQL query**, letting an attacker alter the query (e.g., inputting `' OR '1'='1` to bypass a login). The primary, near-total defense is **parameterized queries / prepared statements**: you send the SQL structure and the user data **separately**, so the database treats input strictly as **data, never as executable SQL** (`WHERE email = ?` with the value bound separately). Using an **ORM** (JPA/Hibernate, SQLAlchemy) gives this by default. Add **input validation** (reject clearly malformed input) as defense in depth, and run the app with a **least-privilege database user** (so even a successful injection can't, say, drop tables). The golden rule: **never build SQL by string concatenation with user input.**

### Q24. XSS and CSRF — what and how to prevent?
These are two distinct, commonly-confused browser attacks:
- **XSS (Cross-Site Scripting)** — the attacker **injects malicious JavaScript** that runs in *other users'* browsers (e.g., via an unsanitized comment field), letting them steal tokens/data or act as the user. **Prevent** with **output encoding/escaping** of any user-supplied data you render, a **Content Security Policy (CSP)**, **input sanitization** for rich content, **httpOnly cookies** (so scripts can't read tokens), and using frameworks (React) that auto-escape.
- **CSRF (Cross-Site Request Forgery)** — the attacker **tricks an authenticated user's browser into sending an unwanted request** to your site, riding on their existing session cookie. **Prevent** with **CSRF tokens** (a secret the attacker can't know), **SameSite cookies** (so cookies aren't sent on cross-site requests), and verifying the `Origin`/`Referer`. Note: pure **bearer-token APIs** (no cookies) are largely immune to CSRF but still exposed to XSS token theft — which is exactly why token storage is a debated topic.

### Q25. How do you secure microservices end-to-end?
Microservice security is layered ("defense in depth") and follows a **zero-trust** philosophy — never trust the network, verify every request:
- **Edge (API Gateway)** — the gateway handles **authentication** (validating the JWT), **rate limiting**, and a **WAF** to block malicious traffic before it reaches services.
- **Service-to-service** — internal calls are authenticated too, via **mTLS** (mutual TLS, usually auto-managed by a service mesh like Istio) and/or **OAuth2 client-credentials tokens** — so a compromised service can't freely call others.
- **Data** — encrypt **in transit** (TLS everywhere) and **at rest** (KMS/Key Vault-managed keys).
- **Secrets** — stored in **Vault/Key Vault**, rotated, accessed via **least-privilege IAM/managed identities**.
- **Zero-trust** — every request is authenticated and authorized regardless of where it originates; the network perimeter is not a security boundary.

### Q26. HTTPS/TLS — what does it provide?
HTTPS is HTTP running over **TLS (Transport Layer Security)**, and it provides three guarantees for data in transit:
1. **Confidentiality (encryption)** — the data is encrypted, so eavesdroppers on the network can't read it (passwords, tokens, personal data).
2. **Integrity** — it detects tampering, so an attacker can't silently modify the data in flight.
3. **Server authentication** — via **certificates** issued by trusted Certificate Authorities, the client verifies it's actually talking to the real server (not an impostor / man-in-the-middle).
The **TLS handshake** negotiates the encryption keys at the start of the connection. Best practices: use modern **TLS 1.2/1.3** (drop older versions), and enable **HSTS** (HTTP Strict Transport Security) to force browsers to always use HTTPS. Never send credentials or tokens over plain HTTP.

### Q27. How do you store passwords?
Passwords must **never** be stored in plaintext or with reversible encryption. Instead, store a **one-way hash** created with a **slow, salted, adaptive hashing algorithm** — **bcrypt, scrypt, or Argon2** (Argon2id is the current recommendation). Two properties matter:
- **Salting** — a unique random salt per user is combined with the password before hashing, so two users with the same password get **different** hashes, defeating precomputed **rainbow-table** attacks. (bcrypt/Argon2 handle salting for you.)
- **Slow/adaptive (work factor)** — these algorithms are deliberately **computationally expensive**, so brute-forcing is impractical, and you can increase the cost as hardware improves.
Critically, **do not use fast hashes like MD5, SHA-1, or even SHA-256** for passwords — their speed is exactly what makes them GPU-crackable. In Spring, use `BCryptPasswordEncoder` / `DelegatingPasswordEncoder`. To verify a login, hash the submitted password and compare against the stored hash.


---

## ⚡ Rapid-Fire soundbites
- "OAuth2 = authorization; OIDC = authentication on top; SAML = XML-based enterprise SSO."
- "Use **Authorization Code + PKCE** for user-facing apps, **Client Credentials** for service-to-service."
- "JWTs are signed, not encrypted — never put secrets in the payload."
- "Validate signature, `exp`, `iss`, `aud` on every JWT."
- "Short-lived access tokens + refresh tokens + rotation solve the JWT revocation problem."
- "RBAC for roles; ABAC/OPA when you need fine-grained, attribute-based policies."
- "Zero-trust + least privilege + secrets in a vault + mTLS between services."

---
---

# PART 2 — Advanced & Tough Questions (with detailed explanations + examples)

## T1. Walk me through the OAuth2 Authorization Code + PKCE flow step by step (and why PKCE exists).
1. The SPA/mobile app generates a random `code_verifier` and its hash `code_challenge`.
2. Redirects the user to the Authorization Server with `response_type=code`, `client_id`, `redirect_uri`, `scope`, `code_challenge`.
3. User authenticates + consents → AS redirects back with a one-time **authorization code**.
4. App exchanges `code` + the original `code_verifier` at the token endpoint → gets **access token** (+ refresh + ID token).
5. App calls the API with `Authorization: Bearer <access_token>`.
**Why PKCE:** public clients (SPA/mobile) can't keep a secret, so an attacker who intercepts the code can't exchange it without the `code_verifier` → prevents authorization-code interception attacks. (Implicit flow is deprecated precisely because it exposed tokens in the URL.)

## T2. A JWT is stolen — what can the attacker do, and how do you limit the blast radius?
Because JWTs are **stateless/self-contained**, a valid stolen token works until it **expires** — you can't easily revoke it. Mitigations: **short access-token TTL** (5–15 min) + refresh tokens, **refresh-token rotation** with reuse detection, a **denylist/jti** check at the gateway for high-value tokens, bind tokens to a client (DPoP/mTLS-bound tokens), store tokens in **httpOnly cookies** (not localStorage), and always serve over TLS. On breach: rotate signing keys (invalidates all tokens).

## T3. How exactly does a resource server validate a JWT (no call to the auth server)?
It fetches the AS's public keys from the **JWKS endpoint** (`/.well-known/jwks.json`), caches them, and for each request:
1. Verify the **signature** using the key matching the `kid` header (RS256).
2. Check `exp`/`nbf` (time), `iss` (trusted issuer), `aud` (this API), and required `scope`/roles.
3. No network round-trip per request → scalable. Key rotation is handled via JWKS `kid`.
This is why RS256 (asymmetric) is preferred in microservices — services only need the **public** key.

## T4. OAuth2 vs OIDC vs SAML — when do you pick each? (crisp)
- **OAuth2** — *authorization* (delegated API access via access tokens). Not for login by itself.
- **OIDC** — *authentication* built on OAuth2 (adds the **ID token**). Use for modern SSO/login in web/mobile/SPA.
- **SAML** — XML-based enterprise SSO (IdP↔SP assertions). Use when integrating with legacy enterprise IdPs that require it.
One-liner: "New app login → OIDC. API delegation → OAuth2. Enterprise/legacy SSO → SAML."

## T5. Service-to-service auth — how do services authenticate each other?
- **OAuth2 Client Credentials** grant: service A gets a token from the AS (its own identity + scopes) and calls service B, which validates it. No user involved.
- **mTLS** (mutual TLS) via a service mesh: both sides present certs → strong identity + encryption, often auto-managed by Istio/Linkerd.
- In cloud: **managed identities / workload identity** so services get short-lived tokens without stored secrets.
Zero-trust: authenticate + authorize **every** call, don't trust the network.

## T6. Where do you store the JWT on the frontend — and the trade-offs?
- **httpOnly + Secure + SameSite cookie** — not readable by JS → mitigates **XSS** token theft; but needs **CSRF** protection (SameSite=Lax/Strict + CSRF token for state-changing requests).
- **localStorage** — easy, works across tabs, but any XSS can steal it → avoid for sensitive tokens.
Best practice for web: httpOnly cookie for the refresh token, short-lived access token in memory.

## T7. RBAC vs ABAC — give a concrete scenario where RBAC isn't enough.
RBAC: "MANAGER can approve expenses." But "a manager can approve expenses **only for their own department and under $10k**" needs **ABAC** — attributes (user.dept == resource.dept, amount < 10000, time, location). Implement ABAC with a policy engine like **OPA/Rego** or Cedar, evaluated at the gateway/service. RBAC for coarse roles, ABAC for fine-grained, context-aware rules.

## T8. How do you prevent the top OWASP issues in a Spring/FastAPI app? (with examples)
- **SQL Injection:** parameterized queries / JPA (`WHERE email = :email`), never string concat.
- **Broken Access Control:** enforce authorization on the **server** for every request (`@PreAuthorize`), never trust client-side checks; check object ownership (IDOR).
- **XSS:** output-encode, CSP header, framework escaping, sanitize rich input.
- **Sensitive data exposure:** TLS everywhere, encrypt at rest, hash passwords (**bcrypt/Argon2**), don't log secrets/PII.
- **Vulnerable dependencies:** Snyk/Dependabot/Trivy scans in CI.
- **Security misconfig:** disable stack traces in prod, secure Actuator, least-privilege.

## T9. What is IDOR and how do you prevent it?
**Insecure Direct Object Reference:** `GET /orders/1234` returns someone else's order because the server only checks *authentication*, not *ownership/authorization*. Fix: always verify the authenticated principal is allowed to access **that specific resource** (`order.userId == currentUser.id`), use `@PostAuthorize`/policy checks, and avoid exposing guessable sequential IDs (use UUIDs + authz).

## T10. CSRF vs XSS — how are they different and which defenses apply?
- **XSS** — attacker injects scripts that run in the victim's browser (steals tokens, acts as user). Defense: output encoding, CSP, sanitize input, httpOnly cookies.
- **CSRF** — attacker tricks the victim's browser into sending an authenticated request (using their cookie) to your site. Defense: **CSRF tokens**, **SameSite** cookies, verify `Origin`/`Referer`. Note: pure bearer-token APIs (no cookies) are largely immune to CSRF but exposed to XSS token theft — hence the storage debate.

## T11. How do you securely store passwords, and why not SHA-256?
Use a **slow, salted, adaptive** hash: **bcrypt / scrypt / Argon2** (Argon2id preferred). A unique per-user salt defeats rainbow tables; the work factor makes brute force expensive. Fast hashes (MD5/SHA-1/SHA-256) are wrong for passwords precisely because they're fast → GPU-crackable. Spring: `BCryptPasswordEncoder`/`DelegatingPasswordEncoder`.

## T12. Token refresh with rotation + reuse detection — how does it work?
On each refresh, the AS issues a **new** refresh token and invalidates the old one. If an **old** (already-used) refresh token is presented again, that signals theft → the AS revokes the whole token family and forces re-login. This limits damage from a stolen refresh token. Combine with short access-token TTLs.

## T13. Encryption in transit vs at rest — and where do keys live?
- **In transit:** TLS 1.2/1.3 (HTTPS, mTLS between services), HSTS.
- **At rest:** disk/DB/blob encryption via **KMS/Key Vault**-managed keys; envelope encryption (data key encrypted by a master key).
- **Key management:** rotate keys, restrict access via IAM, audit usage, never hardcode. Managed identities to access Key Vault without secrets.

## T14. Tough rapid-fire
- **Access token vs ID token vs refresh token** — API access / user identity / get new access tokens.
- **`alg: none` attack** — reject unsigned tokens; pin expected algorithm.
- **Why validate `aud`?** a token minted for another API shouldn't be accepted by yours (token substitution).
- **Opaque token vs JWT** — opaque needs introspection (revocable, DB lookup) vs JWT self-validated (scalable, hard to revoke).
- **mTLS** — mutual cert auth; strong service identity + encryption.
- **Least privilege / zero trust** — minimal scopes/roles, verify every request, short-lived creds.
- **Secrets** — Vault/Key Vault, rotation, never in Git; scan for leaked secrets (gitleaks).
- **Rate limiting + WAF at the gateway** — mitigate brute force, DoS, injection.

---
---

# PART 3 — More Real Interview Questions (Easy Language, No Repeats)

## Q1. Authentication vs Authorization — the simplest way to remember?
- **Authentication** = "**Who are you?**" (proving your identity — like showing your ID at the airport).
- **Authorization** = "**What are you allowed to do?**" (like your boarding pass letting you into a specific seat/lounge).
First you authenticate, then you're authorized.

## Q2. What is a token, in plain words?
A token is like a **wristband at a concert**. After you show your ticket (login), you get a wristband (token). Now you flash the wristband to enter areas, instead of showing your ticket every time. The server checks the token on each request instead of asking for your password again.

## Q3. Why not just send username/password on every request?
It's insecure (password exposed repeatedly, easy to steal) and inefficient (the server would re-check credentials every time). Instead you log in once, get a **token**, and send that token — which is short-lived and limited in scope, so a leak is less damaging.

## Q4. What is HTTPS and why does it matter?
HTTPS = HTTP + encryption (TLS). It scrambles the data between browser and server so attackers on the network can't read or tamper with it (passwords, tokens, personal data). It also verifies you're talking to the real server (via a certificate). Always use HTTPS — never send credentials over plain HTTP.

## Q5. What is a session vs a token (JWT) approach?
- **Session-based** — server stores your login info and gives you a session ID (in a cookie); server looks it up each request. Easy to revoke, but needs server-side storage.
- **Token-based (JWT)** — the token itself carries your info and is signed; the server just verifies the signature, no lookup needed. Scales well, but harder to revoke before expiry.

## Q6. What is Single Sign-On (SSO), explained simply?
Log in **once** and access many applications without logging in again. Like a theme park wristband that gets you into all the rides. Behind the scenes, apps trust a central **Identity Provider** (Google, Okta, Azure Entra ID) to confirm who you are. Implemented with OIDC or SAML.

## Q7. What is Multi-Factor Authentication (MFA)?
Requiring **two or more** types of proof to log in: something you **know** (password), something you **have** (phone/OTP app), or something you **are** (fingerprint/face). Even if a password is stolen, the attacker still can't get in without the second factor. Greatly improves security.

## Q8. What is an API key and how is it different from a token?
An **API key** is a simple long string identifying an application (not a user), often used for partner/service access. It's static and doesn't expire on its own, so it's less secure than short-lived OAuth tokens. Good for basic rate-limiting/identification; use OAuth tokens for real user/security contexts.

## Q9. What is the principle of least privilege, with an example?
Give each user/service **only the minimum access they need** — nothing more. Example: a reporting service that only reads data should have a **read-only** database account, not admin. So if it's compromised, the damage is limited. This is a core security best practice.

## Q10. What is encryption "in transit" vs "at rest" (simple)?
- **In transit** — data is encrypted while moving over the network (HTTPS/TLS), so eavesdroppers can't read it.
- **At rest** — data is encrypted while stored on disk/database, so someone who steals the disk/backup can't read it.
You want both for sensitive data.

## Q11. What is hashing and how is it different from encryption?
- **Encryption** — two-way: you can encrypt and later **decrypt** back to the original (used for data you need to read later).
- **Hashing** — one-way: you can hash but **can't reverse** it (used for passwords). You verify by hashing the input and comparing hashes.
So passwords are hashed (never decryptable), while, say, stored credit-card tokens might be encrypted.

## Q12. What is "salting" a password?
Adding a unique random value (the **salt**) to each password before hashing. This ensures two users with the same password get **different** hashes, and defeats "rainbow table" attacks (precomputed hash lookups). Algorithms like bcrypt/Argon2 handle salting automatically.

## Q13. What is a security vulnerability scan and where does it fit in CI/CD?
Automated tools (Snyk, Trivy, OWASP Dependency-Check) that scan your code, dependencies, and Docker images for **known vulnerabilities**. You run them in the CI/CD pipeline so a build **fails** if it introduces a serious security flaw — catching issues before they reach production.

## Q14. What is a firewall / WAF in simple terms?
- A **firewall** controls which network traffic is allowed in/out (by IP/port).
- A **WAF (Web Application Firewall)** sits in front of your web app and blocks malicious HTTP requests (SQL injection attempts, XSS, bot attacks) based on rules. It's an extra shield at the edge.

## Q15. What is rate limiting and why is it a security feature?
Limiting how many requests a user/IP can make in a time window. It prevents **abuse**: brute-force password guessing, denial-of-service (DoS) attacks, and API scraping. Exceeding the limit returns HTTP **429 Too Many Requests**. Usually done at the API gateway.

## Q16. What are roles and permissions (RBAC), with a simple example?
- **Permission** — a specific action ("delete_user", "view_reports").
- **Role** — a bundle of permissions ("Admin", "Editor", "Viewer").
You assign roles to users, so managing access is simple: make someone an "Admin" instead of granting 20 individual permissions. This is **Role-Based Access Control (RBAC)**.

## Q17. What is a certificate (SSL/TLS certificate) in one line?
A digital ID card for a website, issued by a trusted authority (CA), that proves the site is who it claims to be and enables the encrypted HTTPS connection. Browsers show a padlock when the certificate is valid.

## Q18. What is the OWASP Top 10?
A well-known list of the **10 most critical web security risks** (like Injection, Broken Access Control, XSS). It's the industry checklist developers use to make sure they've addressed the most common and dangerous vulnerabilities. Good to mention you "follow OWASP guidelines."

## Q19. How do you handle a leaked secret/API key?
1. **Revoke/rotate** it immediately (invalidate the old one).
2. Issue a new secret and update the apps (ideally via a vault, not code).
3. Investigate what was accessed and check logs.
4. Prevent recurrence: use a secrets manager, add secret-scanning (gitleaks) in CI, and never commit secrets to Git.

## Q20. What is CSRF, explained with a simple scenario?
You're logged into your bank. You visit a malicious site, which secretly makes your browser send a "transfer money" request to the bank — using your logged-in cookie. The bank thinks it's you. That's **Cross-Site Request Forgery**. Defenses: **CSRF tokens** (a secret the attacker can't know) and **SameSite cookies** (so cookies aren't sent on cross-site requests).

## Q21. What is XSS, explained simply?
**Cross-Site Scripting** — an attacker sneaks malicious JavaScript into a page (e.g., via a comment field), and it runs in other users' browsers, stealing their data/tokens. Prevent by **escaping/sanitizing** any user input you display and using a Content Security Policy (CSP). Modern frameworks (React) auto-escape, which helps a lot.

## Q22. If you had to secure a new REST API from scratch, what's your checklist?
1. **HTTPS** everywhere.
2. **Authentication** (OAuth2/OIDC + JWT validation).
3. **Authorization** on every endpoint (RBAC, check ownership).
4. **Input validation** (reject bad/oversized input; prevent injection).
5. **Rate limiting** + WAF at the gateway.
6. **Secrets** in a vault, not code.
7. **Least-privilege** DB/service accounts.
8. **Logging/monitoring** (no secrets in logs) + dependency scanning.
9. **CORS** configured to only allow trusted origins.



