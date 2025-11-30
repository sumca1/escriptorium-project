# 🏗️ Build Management

## What's Here?
Everything related to building, testing, and quality assurance of 
the eScriptorium project.

## Quick Start:
```bash
# Setup CI/CD
./ci-cd/setup-github-actions.sh

# Run tests
./testing/run-all-tests.sh

# Check quality
./quality/run-linters.sh
```

## Domains:
- **ci-cd/** - GitHub Actions, automated pipelines
- **testing/** - Unit, integration, E2E tests
- **quality/** - Linting, formatting, coverage
- **versioning/** - Releases, changelogs, git workflows
- **documentation/** - Dev guides, API docs, ADRs
- **tools/** - Build utilities and helpers

## For ChatBots:
When working in this domain, focus ONLY on:
✅ Build processes and automation
✅ Testing frameworks and test cases
✅ Code quality tools and standards
✅ CI/CD pipeline configuration
✅ Version management and releases

Do NOT touch:
❌ Core application code → See CORE/
❌ Docker/deployment → See DEPLOYMENT_MANAGEMENT/

---

**Note:** This domain is extracted from best practices in escriptorium_V2/
