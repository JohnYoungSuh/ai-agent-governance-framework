## Purpose

This policy defines requirements for generating, protecting, storing, and integrating logs and audit records across AI/Dev/Sec/Ops.  

Compliance, security monitoring, and both internal and external audits rely on these logs to demonstrate policy enforcement and system integrity.

---

## Scope

This policy applies to all components of the AI/Dev/Sec/Ops framework, including:  
- AI OPS Agents generating audit-trail entries  
- AI Auditor Agent ingesting and verifying logs  
- JIRA change-management events  
- AWS Secrets Manager credential operations  
- SIEM ingestion pipelines  
- External audit interfaces  

---

## Logging Requirements

### Log Sources

- Audit-trail store entries (append-only JSON)  
- JIRA ticket events (structured metadata)  
- Credential checkout/checkin from AWS Secrets Manager  
- SIEM-normalized events (generic SIEM schema)  

### Log Format and Schema

- All entries must conform to approved JSON schemas:  
  - `policies/schemas/audit-trail.json`  
  - `policies/schemas/siem-event.json`  
- Each log record must include:  
  - A unique `siem_event_id`  
  - ISO-8601 `timestamp`  
  - `source` or `log_source` field specifying origin  
  - Payload matching the schema for that source  

### Protection and Retention

- Store logs in append-only, write-once storage (e.g., S3 Object Lock, WORM).  
- Enable object-level immutability and versioning to prevent deletion or modification.  
- Retain all logs for a minimum of 1 year and archive to cold storage for 3 additional years.  
- Periodically publish cryptographic hashes (Merkle root) for external integrity verification.  

### Access Control

- Grant **append-only** write permissions exclusively to the AI Auditor Agent.  
- Grant read-only access to:  
  - External auditors via MCP-style API  
  - Security operations and compliance teams  
- Restrict administrative deletion or modification rights; any permission change requires a multi-layer PKI-signed approval (see `frameworks/approval-workflows.yml`).  

### SIEM Integration

- Configure SIEM connectors to ingest logs from:  
  - Audit-trail append-only store  
  - JIRA event webhook endpoint  
  - AWS Secrets Manager audit logs  
- Map incoming fields to the generic SIEM schema (`policies/schemas/siem-event.json`).  
- Ensure SIEM retention and index settings meet policy retention requirements.  

### Audit Monitoring

- AI Auditor Agent must consume both raw audit-trail JSON and SIEM events for control validation.  
- Define SIEM alert rules for:  
  - Missing or out-of-order audit events  
  - Budget token over-use or missing JIRA approvals  
  - Attempts to modify protected logs without approvals  
  - Document all alert definitions under `frameworks/observability-config.yml`.  
