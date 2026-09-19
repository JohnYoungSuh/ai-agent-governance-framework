# Product & Compliance Manager Review: Production-Scale Implementation Plan

**Reviewer:** Product & Compliance Manager Persona  
**Date:** September 19, 2026  
**Document Under Review:** [docs/PRODUCTION-SCALE-PLAN.md](../PRODUCTION-SCALE-PLAN.md)  
**Baseline Evaluated:** `master` @ `4bcfc84` / `4fe483e`  
**Verdict:** **APPROVED WITH STRATEGIC GUIDANCE (High Commercial Viability)**

---

## 1. Executive Verdict & Strategic Alignment

This plan represents a crucial, mature pivot from **"governance theater"** (unmeasured claims of 152 ZTOM and theoretical 90.25% token savings) to a **hardened, enterprise-grade Policy Decision Point (PDP)** that can survive a commercial procurement audit or DoD IL5 / FedRAMP Moderate assessment.

### Why This Wins the Enterprise Buyer
The enterprise customer (CISO, VP of Platform Engineering, Head of AI/ML) is currently blocking agent deployments because of one existential fear:
> *"What if an autonomous agent executes an unreviewed destructive action in production, leaks credentials, or bypasses human controls?"*

The plan solves this exact problem by transforming the PDP from a demo-ware script writing to `/tmp` into a durable, multi-replica, fail-closed gate where:
1. **No side effect occurs without a cryptographically verified token.**
2. **Every authorization decision produces immutable, audit-ready evidence.**
3. **Operations maintains an instantaneous kill-switch that survives container lifecycles.**

---

## 2. NIST 800-53 Rev 5 & FedRAMP Moderate Compliance Assessment

The phased breakdown maps directly to required federal and commercial control families:

| Control Family | Specific Controls | Plan Implementation | Compliance Impact |
| :--- | :--- | :--- | :--- |
| **AC (Access Control)** | AC-2, AC-3, AC-6 | **1.1 Caller Auth & 1.6 Rate Limits**: Moving from open network access to mTLS / authenticated caller identity via CMDB. | **Critical:** Resolves the finding that any pod on the cluster network could mint JWTs. |
| **IA (Identification & Auth)** | IA-2, IA-5 | **1.2 Asymmetric JWT (RS256/ES256)**: ExternalSecret key rotation; agents verify with public keys. | **High:** Prevents token forgery and eliminates the architectural flaw of distributing signing keys to all agents. |
| **AU (Audit & Accountability)** | AU-2, AU-3, AU-6, AU-12 | **1.4 Durable Audit**: Streaming `audit-trail.json` to S3/MinIO and OCSF SIEM emitter; fail-closed on emission failure. | **Definitive:** Provides non-repudiable audit spans required for ATO (Authority to Operate). |
| **CM (Config Mgmt)** | CM-3, CM-5 | **1.5 Jira PKI Verification**: Replacing substring matching (`"denied"`) with real cryptographic signatures on CRs. | **Required:** Auditors immediately fail heuristic substring checks for change control. |
| **SC (System Protection)** | SC-7, SC-28, SC-39 | **2.3 Default-Deny NetworkPolicy & 2.4 PSS Restricted**: Egress isolation forcing traffic through GPIS proxy. | **Foundational:** Makes policy bypass an L4/L7 network failure rather than an optional application convention. |
| **IR (Incident Response)** | IR-4, IR-5 | **1.3 Redis Suspensions & 3.5 Runbooks**: Kill switch that survives pod restarts and is operable via runbooks. | **Mandatory:** Fulfills the "human-in-the-loop panic button" requirement. |

---

## 3. Product Roadmap & Phasing Critique

### What the Plan Gets Exactly Right
1. **Phase 0 Gate (Prove the Kernel First):**
   * *PM Endorsement:* Rejecting feature work until CI is green, tests pass reliably, and secret scanning prevents regressions is the hallmark of professional platform engineering.
2. **Prioritizing Kernel Integrity over Token Routing (Phases 1–2 before Phase 4):**
   * *PM Endorsement:* In the real market, saving $0.002 per prompt via token routing means nothing if an untrusted agent can delete an RDS database. Solving security and durability first establishes our core value proposition.
3. **The "What Not to Do in the Next 90 Days" Section:**
   * *PM Endorsement:* This is the most commercially valuable section in the document. It defends engineering focus against speculative features (e.g., auto-applying natural language policies, complex multi-model escalation) while core plumbing is hardened.

---

## 4. PM Blind Spots & Risk Mitigations (Areas to Watch)

As Product Manager, I flag the following three risks that must be proactively managed:

### ⚠️ Risk 1: Downstream PEP Adoption Friction (Phase 2.6)
* **Problem:** GPIS is a **Policy Decision Point (PDP)**, not an automatic **Policy Enforcement Point (PEP)**. If an agent receives a JWT but downstream APIs (K8s API, cloud provider endpoints, internal microservices) do not validate `Authorization: Bearer <JWT>`, the governance model breaks down.
* **PM Requirement:** We must provide a turn-key PEP integration pattern:
  * An Envoy/Traefik sidecar or Istio `RequestAuthentication` filter that validates the GPIS public key at ingress.
  * A lightweight client SDK (`agents/shared/gpis_client.py`) that handles automatic token acquisition, header injection, and retry logic.

### ⚠️ Risk 2: High Availability & Blast Radius of "Fail-Closed"
* **Problem:** If GPIS goes down or Redis becomes unreachable, fail-closed means all AI agent operations stop.
* **PM Requirement:** Enterprise buyers will accept fail-closed for Tier 3/4 write operations, but will demand high resilience for Tier 1 read operations. 
  * Ensure the dedicated Helm chart (Phase 2.1) has **3 replicas with PodDisruptionBudgets (PDB) and topology spread constraints**.
  * Add a health probe contract so load balancers pull degraded pods out of service without blackholing agent traffic.

### ⚠️ Risk 3: Developer Experience (DevX) & Local Testing
* **Problem:** If running an agent locally requires mTLS, cert-manager, ExternalSecrets, and live Jira PKI, developer velocity will grind to a halt, prompting developers to seek bypasses.
* **PM Requirement:** Maintain a clear, zero-friction local development mode:
  * Provide a single `make dev-up` (or docker-compose) with self-signed certs and seeded mock PKI keys so developers can test agents locally in seconds.

---

## 5. Definition of Done for First Milestone

The plan's proposed immediate first step is endorsed:
> **First PR: Phase 1.1 (Caller auth on `/api/v1/authorize`) + Phase 1.3 (Persist suspensions in Redis).**

### PM Acceptance Criteria for Milestone 1:
- [ ] Any call to `/api/v1/authorize` without a registered caller identity (mTLS SAN or CMDB-mapped API key) returns `401 Unauthorized`.
- [ ] A kill-switch suspension issued via `/admin/v1/suspend/{agent_id}` is written to Redis with TTL/persistence.
- [ ] When the GPIS pod is deleted (`kubectl delete pod`) and restarted, previously suspended agents remain suspended (DENIED) on restart.
- [ ] End-to-end integration test passes in CI without manual environment intervention.
