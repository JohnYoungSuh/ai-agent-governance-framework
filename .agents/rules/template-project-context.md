# Project Context Template

## Instructions
Copy this template to `.claude/prompts/project-context.md` in any new project.
Customize the sections below to provide automatic framework context.

---

# [Project Name] - Project Context

## Project Overview
[Brief description: What does this project do? What's its purpose?]

## Tech Stack
- **Language**: [e.g., Python, TypeScript, Go]
- **Framework**: [e.g., FastAPI, React, Django]
- **Database**: [e.g., PostgreSQL, MongoDB]
- **Infrastructure**: [e.g., AWS Lambda, Kubernetes, Docker]
- **Key Libraries**: [List 3-5 most important dependencies]

## Project Structure
```
/src or /app - [Main application code]
/tests - [Test files]
/docs - [Documentation]
/scripts - [Automation scripts]
/config - [Configuration files]
[Add other important directories]
```

## Key File Paths
- Main entry point: `[path/to/main.py or index.ts]`
- Configuration: `[config/settings.py]`
- Tests: `[tests/]`
- Documentation: `[docs/]`

## Development Workflow
- Setup: `[e.g., npm install, pip install -r requirements.txt]`
- Run locally: `[e.g., npm start, python app.py]`
- Run tests: `[e.g., pytest, npm test]`
- Build: `[e.g., npm run build, docker build]`
- Deploy: `[e.g., kubectl apply, terraform apply]`

## Governance & Standards
- **Code Style**: [e.g., PEP 8, ESLint config]
- **Testing Requirements**: [e.g., 80% coverage, all tests pass]
- **Review Process**: [e.g., PR approval required, automated checks]
- **Security**: [e.g., secrets in vault, vulnerability scanning]
- **Compliance**: [e.g., SOC 2, HIPAA, internal policies]

## Common Tasks
- Add new feature: [Brief workflow]
- Fix bug: [Brief workflow]
- Deploy to staging: [Brief workflow]
- Deploy to production: [Brief workflow]

## Important Conventions
- [Naming conventions]
- [File organization patterns]
- [Testing patterns]
- [Documentation requirements]

## External Dependencies & Services
- [API services used]
- [Third-party integrations]
- [Cloud services]

## Git & CI/CD
- Branch: [main branch name]
- PR Requirements: [approvals, checks]
- CI/CD: [GitHub Actions, Jenkins, etc.]
- Deployment: [manual, automatic, approval-based]

## Team Contacts
- Owner: [name/email]
- Tech Lead: [name/email]
- [Other key contacts]

## Notes
[Any other context that would help an AI assistant understand this project]
