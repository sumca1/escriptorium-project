# 📋 Maintenance Playbook - תהליך זה שבוע (Day 7)

**מתי:** כל 7 ימים (ביום חמישי או ביום ראשון)  
**משך:** 1-2 שעות  
**מי:** Maintenance chatbot או manager  
**מטרה:** Keep project organized without burdening daily chatbots

## ⚡ Event-driven Triggers (הפעלת תחזוקה בעת שינוי משמעותי)

בנוסף לתזמון השבועי, יש מצבים שבהם יש להפעיל מיידית (או לתזמן מוקדם יותר) את תהליך ה-Maintenance:

- New architecture decision affecting multiple components (e.g., adding a new OCR engine, new model format)
- Major model additions or conversions (more than 1 substantial model)
- Database schema changes or migrations
- Major release / cut-over that impacts production or many files
- Large refactor affecting >5 modules
- Security/compliance changes
- Repeated incidents: >3 similar failures in a rolling 7-day window

כאשר אחד מהטריגרים מתרחש, בצע את ה-Maintenance flow באופן מלא (ראה למטה). השתמש בקובץ `SIGNIFICANT_CHANGE_TEMPLATE.md` כדי לתעד את השינוי ולהנחות את העבודה.

---

## ✅ Checklist למתן-חשבון (Copy-Paste)

### **Step 1: Review Sessions (15 דקות)**

```
[ ] Open SESSION_LOG.md
[ ] Read entries from past 7 days
[ ] Identify common issues/patterns
[ ] Identify successful solutions
[ ] Note interesting findings
```

**זכרו:** תעדו את הדפוסים! אלו הם בעיות חוזרות שצריך לפתור once and for all.

---

### **Step 2: Identify Patterns (15 דקות)**

```
[ ] Pattern 1: [Issue type]
    Frequency: X times this week
    Sessions: [links to sessions]
    Root cause: [analysis]
    
[ ] Pattern 2: [Issue type]
    Frequency: X times
    Sessions: [links]
    Root cause: [analysis]

[ ] Pattern 3: [Issue type]
    ...
```

**שאלות לשאול:**
- האם הבעיה הזו מופיעה קודם?
- אם כן - למה היא חוזרת?
- מה חסר - documentation? automated solution? awareness?

---

### **Step 3: Identify Solutions (15 דקות)**

```
[ ] Solution 1: [For Pattern 1]
    How: [תיאור]
    Code: [קישור לקוד או snippet]
    Sessions where used: [links]
    
[ ] Solution 2: [For Pattern 2]
    How: [תיאור]
    Code: [קישור]
    Sessions: [links]
```

---

### **Step 4: Archive Old Files (20 דקות)**

```
[ ] Check design files
    - Completed designs? → move to /archive/
    - Old solutions? → move to /archive/
    - Deprecated approaches? → move to /archive/

[ ] For each archived file, create REASON.md:
    ---
    **Why Archived:** [תיאור]
    **Date:** [תאריך]
    **Related Sessions:** [links]
    **Lessons Learned:** [מה למדנו]
    **When to reference:** [מתי לחזור אליו]
    ---

[ ] Keep:
    - ACTIVE design files in /design-active/
    - Recent sessions in SESSION_LOG
    - Active patterns in PATTERNS_CATALOG
```

---

### **Step 5: Update/Create _META/ Files (30 דקות)**

#### **File 1: _META/INDEX.md**

```markdown
# Central Index - כל הקבצים

**Updated:** [תאריך]
**Total Files:** X
**Last Maintenance:** [תאריך]

## Active Files (In Use)

| File | Created | Updated | Status | Purpose | Links |
|------|---------|---------|--------|---------|-------|
| INTEGRATION_DESIGN_PLAN.md | 27-Oct | 27-Oct | ACTIVE | System architecture | [Sessions], [Related] |
| batch_ocr.py | 15-Oct | 27-Oct | ACTIVE | OCR processing | [Pattern: Encoding], [Solution] |

## Archived Files (History)

| File | Created | Archived | Reason | Related Sessions |
|------|---------|----------|--------|------------------|
| OLD_SURYA_PLAN_v1.md | 20-Oct | 27-Oct | Replaced by v2 | [Session 1], [Session 2] |

## Meta Files (Organization)

| File | Purpose | Updated |
|------|---------|---------|
| PATTERNS_CATALOG.md | Identify recurring issues | [date] |
| SOLUTIONS_CATALOG.md | Track what works | [date] |
| WARNINGS_CATALOG.md | What NOT to do | [date] |
```

---

#### **File 2: _META/PATTERNS_CATALOG.md**

```markdown
# Patterns Catalog - דפוסים שגילינו

**Updated:** [תאריך]
**Total Patterns:** X

## Pattern 1: Unicode/Encoding in Surya

**Category:** Technical Issue  
**Severity:** Medium  
**Frequency:** 3 times (27-Oct)

**Description:**
Hebrew terminal + emoji in output → UnicodeEncodeError

**Occurrences:**
- Session: [link to session 1] (batch_ocr.py line 21)
- Session: [link to session 2] (output handling)
- Session: [link to session 3] (print statements)

**Root Cause Analysis:**
Windows terminal default: cp1255 (Hebrew)
Surya output includes emoji (⭐, ✅, etc)
Python tries to encode emoji to cp1255 → fails

**Solution:**
See: SOLUTIONS_CATALOG.md#utf8-wrapper

**Prevention:**
Add UTF-8 wrapper at startup for all Python scripts
Document in: WARNINGS_CATALOG.md#always-set-utf8

**Related Issues:**
- [Other encoding issues if any]

---

## Pattern 2: [Another pattern]

**Category:** [Type]  
**Frequency:** X times  
**Severity:** [High/Medium/Low]
...
```

---

#### **File 3: _META/SOLUTIONS_CATALOG.md**

```markdown
# Solutions Catalog - פתרונות שעבדו

**Updated:** [תאריך]
**Total Solutions:** X

## Solution 1: UTF-8 Output Wrapper

**For Pattern:** Unicode/Encoding (see PATTERNS_CATALOG.md#unicode)

**Problem It Solves:**
UnicodeEncodeError when printing emoji to Hebrew terminal

**How It Works:**
```python
import sys
import io

# At start of script:
sys.stdout = io.TextIOWrapper(
    sys.stdout.buffer,
    encoding='utf-8',
    errors='replace'
)

# Now you can print emoji safely:
print("✅ Success!")  # Works!
```

**Implementation:**
- Where: batch_ocr.py (line 21)
- Add: 2 import lines + 4 lines of code
- Time: < 1 minute

**Effectiveness:**
✅ Tested in: 3 sessions (all worked)
✅ No side effects
✅ Works with Hebrew + emoji

**Test Cases:**
- Hebrew text: ✅ Works
- English text: ✅ Works
- Emoji: ✅ Works
- Mixed: ✅ Works

**Related Solutions:**
- If issue persists: check terminal encoding (cmd vs powershell)

**Code Example Link:**
[Link to batch_ocr.py implementation]

**Used In:**
- batch_ocr.py
- [other files if any]

---

## Solution 2: [Another solution]

**For Pattern:** [Pattern name]  
**How:** [תיאור]  
**Code:** [snippet or link]  
**Tested:** [כמה בדיקות]
```

---

#### **File 4: _META/WARNINGS_CATALOG.md**

```markdown
# Warnings Catalog - מה שלא לעשות

**Updated:** [תאריך]

## Warning 1: Don't Ignore Terminal Encoding

**Issue:** Unicode errors on Windows Hebrew terminals

**What NOT to do:**
❌ Ignore the error and try again
❌ Use English-only workarounds
❌ Add `# -*- coding: utf-8 -*-` (doesn't fix stdout)
❌ Use `print()` with no wrapper

**What TO do:**
✅ Add UTF-8 wrapper at script start (see SOLUTIONS_CATALOG)
✅ Test with emoji/Hebrew
✅ Document requirement
✅ Pass solution to next developer

**Cost of Ignoring:**
- Time: Hours of debugging
- Frustration: High
- Prevention: 1 minute setup

---

## Warning 2: [Another warning]

**Issue:** [תיאור הבעיה]  
**NOT:** [מה לא לעשות]  
**DO:** [מה לעשות]
```

---

### **Step 6: Cross-Link Everything (20 דקות)**

```
[ ] Update CURRENT_STATE.md
    [ ] Link to: _META/INDEX.md
    [ ] Link to: PATTERNS_CATALOG.md
    [ ] Link to: SOLUTIONS_CATALOG.md
    [ ] Add: "Patterns identified this week: X"
    [ ] Add: "Solutions documented: X"

[ ] Add cross-references in SESSION_LOG.md
    Example: "Pattern identified: see PATTERNS_CATALOG.md#unicode"
    
[ ] Update PATTERNS_CATALOG
    [ ] Each pattern links to: SOLUTIONS_CATALOG
    [ ] Each pattern links to: related SESSIONS
    [ ] Each pattern links to: WARNINGS_CATALOG (if applicable)

[ ] Update SOLUTIONS_CATALOG
    [ ] Each solution links to: PATTERNS_CATALOG
    [ ] Each solution links to: code examples
    [ ] Each solution links to: test results

[ ] Update WARNINGS_CATALOG
    [ ] Each warning links to: SOLUTIONS_CATALOG
    [ ] Each warning links to: PATTERNS_CATALOG
```

---

### **Step 7: Generate Reports (15 דקות)**

```
[ ] Create: project_health_report.md
    - Files: X total (Y active, Z archived)
    - Patterns: X identified
    - Solutions: X documented
    - Sessions: X this week
    - Average chatbot overhead: X דקות
    - System health: [EXCELLENT/GOOD/FAIR]

[ ] Create: patterns_and_solutions_summary.md
    - Quick reference for new chatbots
    - "If you encounter X, see SOLUTIONS_CATALOG#Y"
    - Code snippets ready to copy-paste

[ ] Create: maintenance_log.md entry
    ```
    ## Maintenance - 27-Oct-2025
    
    **Duration:** 1.5 hours
    **Patterns Found:** 3
    **Solutions Documented:** 3
    **Files Archived:** 2
    **Index Updated:** ✅
    **System Health:** EXCELLENT
    
    **Actions Taken:**
    1. Reviewed 7 sessions
    2. Created PATTERNS_CATALOG.md
    3. Created SOLUTIONS_CATALOG.md
    4. Archived old_api_plan_v1.md
    5. Cross-linked everything
    
    **Next Week Focus:**
    - Test solutions with new chatbots
    - Monitor for pattern repetition
    - Consider automation for recurring fixes
    ```
```

---

### **Step 8: Final Verification (10 דקות)**

```
[ ] Verify all links work
    [ ] SESSION_LOG → PATTERNS_CATALOG
    [ ] PATTERNS_CATALOG → SOLUTIONS_CATALOG
    [ ] SOLUTIONS_CATALOG → code examples
    [ ] Everything → CURRENT_STATE.md

[ ] Verify structure
    [ ] /archive/ has all old files
    [ ] /design-active/ has all active files
    [ ] _META/ has all catalogs updated

[ ] Verify CURRENT_STATE.md
    [ ] Points to active files
    [ ] Links to _META/ for deep dives
    [ ] Shows latest patterns found
    [ ] Ready for next week

[ ] Verify BUILD_MANAGER_DASHBOARD.html
    [ ] Loads without errors
    [ ] Shows updated counts
    [ ] Displays latest sessions
```

---

## ⏱️ Timeline Example:

```
Monday (After Maintenance):
- System is clean ✅
- Catalogs are updated ✅
- All links work ✅
- New chatbot onboarding: 5 דקות

Days 1-7:
- Chatbots work without burden ✅
- SESSION_LOG accumulates entries ✅
- No organization overhead ✅

Sunday Evening:
- 1-2 hour maintenance session ✅
- Review, archive, organize, link ✅
- Generate reports ✅
- System ready for next week ✅
```

---

## 💡 Key Principles:

### **For Maintenance Person:**
- ✅ Be thorough (this is one-time investment)
- ✅ Link everything (so chatbots can navigate)
- ✅ Document patterns (so they can be solved)
- ✅ Archive smartly (keep history but don't clutter)

### **For Next Week:**
- ✅ New chatbots see organized system
- ✅ They know where to find solutions
- ✅ Patterns are documented
- ✅ Knowledge is preserved

---

## 📝 Template: Use This Every Week

```markdown
## Maintenance - [DATE]

**Duration:** X hours
**Sessions Reviewed:** X
**Patterns Found:** X
**Solutions Documented:** X
**Files Archived:** X

**Key Findings:**
- Pattern 1: [description]
- Pattern 2: [description]
- Solution 1: [description]

**Actions:**
- [ ] Review SESSION_LOG
- [ ] Create/Update PATTERNS_CATALOG
- [ ] Create/Update SOLUTIONS_CATALOG
- [ ] Archive old files
- [ ] Cross-link everything
- [ ] Generate reports
- [ ] Verify links
- [ ] Update CURRENT_STATE

**System Health:** [EXCELLENT/GOOD/FAIR]

**Next Week Focus:** [What to watch for]
```

---

## ✅ You're Done!

System is organized, documented, linked, and ready for next week! 🎉

**Next Monday:** Chatbots come back to clean, organized project with clear solutions!
