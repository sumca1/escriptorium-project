# 🛠 Significant Change Template

Use this template when a major design/plan/process change occurs and you want a full maintenance run.

When to use: any of the following triggers (not exhaustive):
- New architecture decision (e.g., add a new engine, model-format shift)
- Model conversion or major model addition (>1 model)
- Database schema change or migration
- Major release / cut-over that affects many files
- Large refactor (changes in >5 modules)
- Security/Compliance change
- Repeated incidents (>3 similar failures in a week)

---

## Quick summary (1-2 lines)

- Title: [Short descriptive title]
- Date: [YYYY-MM-DD]
- Owner: [who triggered this / contact]
- Scope: [short list of affected areas]

---

## Detailed description

[Explain rationale, what changes, what systems are affected, expected impact and rollback plan]

---

## Files / Artifacts changed (list with paths)

- `path/to/file1` - [what changed]
- `path/to/file2` - [what changed]

---

## Risk assessment

- Impact level: High / Medium / Low
- Users affected: [who]
- Rollback plan: [how to roll back]
- Required resources: [people, infra, time estimate]

---

## Actions required for Maintenance run

1. Update `_META/INDEX.md` entries for any new/renamed files
2. Add pattern entries (if new) to `_META/PATTERNS_CATALOG.md`
3. Add solution entries (if new) to `_META/SOLUTIONS_CATALOG.md`
4. Archive replaced/obsolete files to `/archive/` with `REASON.md`
5. Cross-link all session entries that led to this decision
6. Run tests / smoke tests specified below
7. Generate `project_health_report.md` with change note

---

## Smoke tests (minimal acceptance tests)

- Test 1: [describe; pass/fail criteria]
- Test 2: [describe; pass/fail criteria]

---

## Post-maintenance verification

- All links in `_META/INDEX.md` work
- `CURRENT_STATE.md` updated to reflect change
- `SESSION_LOG.md` contains link to this template and maintenance notes
- `project_health_report.md` updated with change summary

---

## Notes / References

[links to design docs, PRs, sessions, etc.]
