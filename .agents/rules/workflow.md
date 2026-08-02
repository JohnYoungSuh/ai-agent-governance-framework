---
trigger: always_on
---

# Project Workflow Rules

## Standard Development Loop
Every code change must follow this sequence — no exceptions:
1. **Edit** source in the appropriate layer (`app/`, `agents/`, `scripts/`, `deploy/`)
2. **Test**: `pytest tests/ -v` → confirm all tests pass
3. **Schema validate** (if policy or schema changed): `python3 scripts/validate-manifest.py`
4. **Lint**: `ruff check . && mypy app/` → confirm 0 errors
5. **Commit** using conventional commits (`fix:`, `feat:`, `sec:`, `compliance:`, etc.)
6. **Push** → let GitHub Actions CI be the final validation signal
7. **Verify CI**: green pipeline = the authoritative "done" signal

## 3-Tier Hardware Testing Strategy
- **Tier 1: Inner-Loop Dev (HP Dragonfly G4)** — Local development, unit/compliance tests (`pytest`), fast `k3d` (K3s in Docker) iterations.
- **Tier 2: Local GPU Inference Lab (Dell XPS 9500)** — NVIDIA GPU running Ollama / vLLM (`qwen2.5-coder:7b`) for zero-cost offline intent routing validation.
- **Tier 3: Bare-Metal Staging Lab (4x Dell OptiPlex 7040 Cluster)** — Proxmox VE 8.x running 4-node K3s cluster for multi-node NetworkPolicy/PPSM testing and eMASS package verification.

## Bug Fix Workflow
1. Open `NEXT_RELEASE_TODO.md` — pick the topmost unchecked item by priority (🔴 → 🏛️ → 🟡 → 🟢 → 🔵)
2. Check `LESSONS_LEARNED.md` — does this match a known root cause pattern?
3. Fix the **root cause**, not the symptom (see LL-004 checklist)
4. Run tests, validate schemas, confirm SIEM events emit correctly
5. Mark the item `[x]` with the fix date
6. Log under `## 📍 Session Log`
7. If it's a new root cause type, add to `LESSONS_LEARNED.md` before committing
8. Commit: `fix: <short description>` or `sec: <short description>` for security

## Release Checklist (Version Bump)
When bumping the version, update ALL of these atomically in a single commit:
1. `README.md` — version badge and "What's New" section
2. `app/main.py` — FastAPI `app = FastAPI(..., version="X.Y.Z")`
3. `agents/*/docker/Dockerfile` — base image pinning + label `VERSION`
4. `deploy/helm/ai-agent/Chart.yaml` — `appVersion: X.Y.Z`
5. `CHANGELOG.md` — add release section

Commit message: `chore: bump version to X.Y.Z across all configs`

## Build Commands Reference
| Task | Command |
|------|---------|
| Run unit tests | `pytest tests/ -v --cov=app` |
| Run integration tests | `pytest tests/integration/ -v` |
| Lint + type check | `ruff check . && mypy app/` |
| Validate agent manifests | `python3 scripts/validate-manifest.py` |
| Run compliance checks | `./scripts/compliance-check-enhanced.sh` |
| Benchmark token savings | `python3 scripts/benchmark_token_savings.py --format json` |
| Build Docker image | `docker build -t security-agent:dev -f agents/security/docker/Dockerfile .` |
| Deploy to local K8s | `helm upgrade --install security-agent deploy/helm/ai-agent -f deploy/helm/ai-agent/values-security.yaml` |
| Generate SBOM | `syft . -o cyclonedx-json > sbom.json` |

## CI/CD Pipeline (2-Stage)
- **Stage 1** — TruffleHog secret scan + `pip-audit` + Trivy container scan + Bandit SAST
- **Stage 2** — pytest (unit + integration) + mypy + manifest validation + Helm lint
- Both stages run on `push` and `pull_request` to `master`
- **Green pipeline = authoritative done signal**. Do not consider a change "done" until CI passes.

## The 3-Strikes Rule
If any task (build, test, push, validate) fails or loops **3 consecutive times**, STOP immediately and ask the user. Do not retry endlessly or find workarounds independently.

## Git & GitHub Preferences
- Use `gh` CLI for all GitHub repository management
- Prefer explicit `-m` messages — never leave the editor open
- Push to `master` branch
- PRs must reference an issue or backlog item

## Lockfile & Dependency Policy
- **Do NOT delete `requirements.txt`** entries without running `pip-audit` first
- Pin all production dependencies to exact versions
- Run `pip-audit` after any dependency change; block commit if critical CVEs found

## Git-Note Hybrid Tracking Rules (from AWS-DFD lessons)
- **Backlog Scope**: Use `NEXT_RELEASE_TODO.md` strictly as a future backlog and task planning board. Not as a detailed transaction journal.
- **Terse Session Logs**: When resolving backlog items, check off `[x]` and log a brief one-line summary under `## 📍 Session Log`.
- **Commit Rationale Authority**: Rely on Conventional Commits to convey detailed engineering decisions. Git is the authoritative technical source of truth.
- **Lessons First**: Root causes belong in `LESSONS_LEARNED.md`, not in commit messages or session logs.
