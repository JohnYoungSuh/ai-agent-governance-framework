# Control Validation Template (MVP)

## Control ID
- Example: SEC-001

## Policy Reference
- Link to mitigation-catalog.md entry

## Implementation
- Code/config snippet or script path
- Mock/test harness if AWS/3rd party not available

## Governance Record (Static JSON)
- Location of JSON registry entry
- Required fields: control_id, mapped_risks, evidence, owner

## Audit Trail (Dynamic JSON)
- Example audit entry schema
- Evidence hash location

## Auditor Agent Checks
- [ ] Governance record exists and is valid
- [ ] Audit trail entries generated for each transaction
- [ ] Gaps flagged as "MISSING"

## MVP Test
- Step 1: Run thin-slice workflow
- Step 2: Verify check-in/out or enforcement
- Step 3: Confirm audit trail JSON created
- Step 4: Reviewer signs off
