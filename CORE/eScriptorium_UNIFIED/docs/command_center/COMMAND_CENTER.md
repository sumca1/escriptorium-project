# ���� Command Center (�������� ����������) - Overview

Purpose: provide a single, actionable place that maps active work stages to the exact documentation and artifacts that matter (session entries, design docs, patterns, solutions, archive locations). The Command Center is the authoritative navigation hub for manager + chatbots during work and during maintenance.

Goals
- Give the manager a fast surface of "where the work lives" for every active stage.
- Give chatbots a single pointer for where to append session notes, where to link significant changes, and where to read solutions.
- Provide an event feed and links to artifacts (sessions, design files, _META/ catalogs, archive entries) so the manager can jump to the right place in one click.

Data sources
- `SESSION_LOG.md` - chronological session entries (append only)
- `CURRENT_STATE.md` - current project state, active tasks, `significant_change_pending` flag
- `_META/INDEX.md` - (planned) central index of documents and their status (ACTIVE/ARCHIVED)
- `_META/PATTERNS_CATALOG.md` - known recurring issues
- `_META/SOLUTIONS_CATALOG.md` - proven fixes and snippets
- `/design-active/` - active design documents
- `/archive/` - historical artifacts and reasons

Command Center Views (minimum viable)
1. Dashboard Summary (one-pager)
   - Latest 5 sessions (with links)
   - Current State snapshot (last updated + next steps)
   - Significant-change pending (flag)
   - Quick actions: "Request Maintenance", "Open Significant Template", "Create Issue"

2. Stage Map (work-stage ��� artifact)
   For each active stage show:
   - Stage name (e.g., "Phase 1 - Infrastructure")
   - Owner / assignee
   - Key docs: link to design doc(s) in `/design-active/`
   - Recent sessions that touched this stage (links)
   - Patterns related to stage (links to `_META/PATTERNS_CATALOG.md`)
   - Solutions related to stage (links)

3. Event Feed
   - Live stream of `SESSION_LOG.md` appended entries (most recent first)
   - Highlights: entries with `SIGNIFICANT_CHANGE: yes` or `significant_change_pending: true`
   - Quick actions inline: open template, link session ��� pattern, flag for maintenance

4. Patterns & Solutions Explorer
   - Searchable table of patterns, frequency, severity and direct link to solutions
   - When you click solution: show code snippet and link to sessions and archives

5. Archive Locator
   - For any artifact, show where its archived copy lives and the `REASON.md` for archival

Quick actions & workflows (one-click ideas)
- "Flag significant change" ��� opens `SIGNIFICANT_CHANGE_TEMPLATE.md` and sets `significant_change_pending: true` in `CURRENT_STATE.md` (manual or scripted)
- "Request Maintenance" ��� creates a maintenance TODO / issue or notifies the maintenance actor
- "Open session" ��� opens the relevant `SESSION_LOG.md` fragment
- "Link to pattern" ��� append a link from session to the pattern entry

UI and Implementation notes
- Minimal first: a markdown-based Command Center (`COMMAND_CENTER.md`) plus the existing `BUILD_MANAGER_DASHBOARD.html` that reads these files and renders widgets.
- Dashboard should NOT require chatbots to change behaviour ��� it only reads `SESSION_LOG.md`, `CURRENT_STATE.md`, and `_META/` files.
- Later: optional small script (Python/PowerShell) to produce JSON summaries for the dashboard to consume.

Naming & linking conventions
- Always link to files by path (relative) and include session line anchors (e.g. `SESSION_LOG.md#session-2025-10-27-16-45`) when possible.
- Use tags in session entries: `SIGNIFICANT_CHANGE: yes` and `PATTERN: <short-key>` and `STAGE: <phase-name>` so the feed can filter.

Minimal API for scripts (suggested)
- `scripts/command_center_export.py --out=data/command_center.json`  (reads markdown files and builds a small JSON used by dashboard)
- `scripts/flag_significant_change.py --title "..." --owner "..."` (creates `SIGNIFICANT_CHANGE_TEMPLATE.md` from CLI and sets `significant_change_pending: true`)

Next steps (practical)
1. Approve the Command Center concept.
2. Add lightweight tags to session entries (example below) and start using them.
3. Create the `scripts/command_center_export.py` (optional) so the HTML dashboard can render dynamic widgets.

Recommended short session entry tags (example use)
```
### Session - 27/10/2025 16:45 - Claude
**Task:** Fixed batch_ocr.py UTF-8 encoding issue
**Changes:**
- `external_tools/surya/batch_ocr.py` - Added UTF-8 wrapper on lines 21-22
**PATTERN:** encoding-unicode
**STAGE:** phase-1-infra
**SIGNIFICANT_CHANGE:** no
**Time:** 5 ��������
---
```

If you approve, I can (A) convert `COMMAND_CENTER.md` into a simple `command_center_export.py` script that generates `data/command_center.json` for the existing `BUILD_MANAGER_DASHBOARD.html` to consume, or (B) produce a minimal HTML snippet for the dashboard to include. Which do you prefer?