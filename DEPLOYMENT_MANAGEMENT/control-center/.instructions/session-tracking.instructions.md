---
description: CRITICAL - Session tracking and state management rules for all AI chatbots
applyTo: '**'
---

# 🚨 SESSION TRACKING ENFORCEMENT RULES
**CRITICAL: These rules MUST be followed by ALL AI assistants in this workspace**

---

## 🚨 **MANDATORY FIRST READ!**

**Before reading this document:**
- ✅ **Read first:** `eScriptorium_CLEAN/.github/instructions/MANDATORY_FIRST_ACTION.md`
- 🔧 **Critical topics:** SSL/pip issues, MCP tools availability
- ⚡ **Priority:** HIGHEST - Required for every new session!

---

## ⚠️ IMMEDIATE ACTION REQUIRED

**AFTER completing ANY task, you MUST:**

1. ✅ **UPDATE `SESSION_LOG.md`** - Append your session details
2. ✅ **UPDATE `CURRENT_STATE.md`** - Overwrite with latest state
3. ✅ **DOCUMENT everything** - Files changed, issues, solutions, time spent

**Failure to update these files is a CRITICAL violation!**

---

## 📚 REQUIRED READING

**Before making ANY changes, you should be aware of:**

1. **Session Log**: `SESSION_LOG.md`
   - Complete history of all chatbot sessions
   - What was done, by whom, when
   - Issues encountered + solutions
   - **This is your collective memory!**

2. **Current State**: `CURRENT_STATE.md`
   - Snapshot of current project state
   - What's working, what's broken
   - Next steps and pending tasks
   - **Read this FIRST before starting work!**

3. **Automation Rules**: `.github/instructions/automation-scripts.instructions.md`
   - Never run manual docker/npm commands
   - Use automation scripts instead

---

## 🔴 RULE #1: Read Before You Act

**BEFORE starting ANY task:**

### Step 1: Read CURRENT_STATE.md
```markdown
✅ Check: What's working?
✅ Check: Known issues?
✅ Check: Recently modified files?
✅ Check: Next steps?
```

### Step 2: Read SESSION_LOG.md
```markdown
✅ Check: What did the last chatbot do?
✅ Check: Were there any issues?
✅ Check: Any recommendations for me?
✅ Check: Has someone already done this task?
```

### Step 3: Avoid Duplicate Work
- If the task was **already done** → Don't repeat it!
- If the task **failed before** → Learn from the failure
- If there's a **known workaround** → Use it!

---

## 🔴 RULE #2: Update After Every Task

**AFTER completing ANY task, you MUST update both files:**

### Update SESSION_LOG.md (Append)

**Required Template:**
```markdown
### Session - [DATE] [TIME] - Chatbot [YOUR-ID]

**Files Modified:**
- `path/to/file1.py` - [specific change description]
- `path/to/file2.js` - [specific change description]

**Actions Taken:**
- ✅ [What you accomplished]
- ✅ [What you built/fixed/deployed]

**Issues Encountered:**
- Problem: [describe the issue]
- Solution: [how you solved it]
- Workaround: [if you found one]

**Time Spent:** [X minutes]

**Next Chatbot Should Know:**
- [Critical info]
- [Recommendations]
- [Warnings]

---
```

### Update CURRENT_STATE.md (Overwrite)

**You MUST update these sections:**

1. **Last Updated** - Current timestamp + your ID
2. **What's Working Right Now** - Add your completed items
3. **Known Issues** - Remove fixed issues, add new ones
4. **Recently Modified Files** - Update the table
5. **Next Steps** - Update pending tasks
6. **System Health** - Update component status

---

## 🔴 RULE #3: Be Specific and Detailed

### ❌ BAD Example:
```markdown
Files Modified:
- editor.js - updated

Actions:
- Fixed stuff
```

### ✅ GOOD Example:
```markdown
Files Modified:
- `eScriptorium_CLEAN/front/dist/editor.js` - Added Hebrew RTL support for text selection (lines 245-267)
- `eScriptorium_CLEAN/scripts/build-and-deploy.ps1` - Used -Quick mode to avoid npm reinstall

Actions Taken:
- ✅ Built frontend using .\scripts\build-and-deploy.ps1 -Quick
- ✅ Deployed editor.js to Docker container at /usr/src/app/static/
- ✅ Verified Hebrew text renders correctly in editor
- ✅ Restarted web service using .\scripts\restart-services.ps1

Issues Encountered:
- Problem: npm install was deleting 45,263 files (324.8 MB), taking 5 minutes
- Solution: Used -Quick mode which skips node_modules cleanup
- Result: Build completed in 45 seconds instead of 5 minutes

Time Spent: 8 minutes total

Next Chatbot Should Know:
- ALWAYS use -Quick mode for fast builds unless you need full cleanup
- Hebrew RTL is now working in editor - no need to fix again
- Template caching might still be an issue - check if changes appear
```

---

## 🔴 RULE #4: Detection and Enforcement

**YOU MUST check for these scenarios:**

### Scenario A: Starting a New Task
```
1. Open CURRENT_STATE.md
2. Check "Recently Modified Files" - was this file just changed?
3. Check "Next Steps" - is this task already listed as done?
4. If YES → Don't duplicate work!
```

### Scenario B: Encountering an Issue
```
1. Open SESSION_LOG.md
2. Search for similar issue (Ctrl+F)
3. If found → Use the documented solution
4. If not found → Document your solution after fixing
```

### Scenario C: Completing a Task
```
1. Append your session to SESSION_LOG.md
2. Update CURRENT_STATE.md with new state
3. Mark tasks as complete in "Next Steps"
4. Update "System Health" if relevant
```

---

## 📋 FILE LOCATIONS

### Root Level (BiblIA_dataset/)
- `SESSION_LOG.md` - Main session log
- `CURRENT_STATE.md` - Main state file

### Subfolder Level (eScriptorium_CLEAN/)
- `SESSION_LOG.md` - Mirror for subfolder chatbots
- `CURRENT_STATE.md` - Mirror for subfolder chatbots

**Note:** Both copies should be kept in sync!

---

## 🎯 QUICK REFERENCE

### Before Starting Work:
```
✅ Read CURRENT_STATE.md (2 minutes)
✅ Scan SESSION_LOG.md for recent sessions (1 minute)
✅ Check .github/instructions/automation-scripts.instructions.md
```

### After Completing Task:
```
✅ Append session to SESSION_LOG.md (3 minutes)
✅ Overwrite CURRENT_STATE.md with new state (2 minutes)
✅ Be specific about files, issues, solutions
✅ Include time estimates
```

### When Stuck:
```
✅ Search SESSION_LOG.md for similar issues
✅ Check CURRENT_STATE.md "Known Issues" section
✅ Check automation-scripts.instructions.md for script solutions
```

---

## ⚠️ CRITICAL SCENARIOS

### Scenario 1: "I can't find the session files"
**Solution:**
- Root level: `G:\OCR_Arabic_Testing\BiblIA_dataset-project\BiblIA_dataset\SESSION_LOG.md`
- Subfolder: `G:\OCR_Arabic_Testing\BiblIA_dataset-project\BiblIA_dataset\eScriptorium_CLEAN\SESSION_LOG.md`

### Scenario 2: "Should I append or overwrite?"
**Answer:**
- `SESSION_LOG.md` → **ALWAYS append** (never delete history)
- `CURRENT_STATE.md` → **ALWAYS overwrite** (replace with latest state)

### Scenario 3: "I forgot to update the files"
**Solution:**
- Go back and update them NOW
- Better late than never
- Include timestamp of when task was actually completed

### Scenario 4: "Another chatbot is working simultaneously"
**Solution:**
- Check CURRENT_STATE.md for "Last Updated" timestamp
- If very recent (< 5 min) → Coordinate to avoid conflicts
- Update SESSION_LOG.md with your session anyway
- Note in your session that another chatbot was active

---

## 🔴 ENFORCEMENT

### This is NOT optional!

**Every AI chatbot MUST:**
- ✅ Read both files before starting work
- ✅ Update both files after completing work
- ✅ Document everything clearly and specifically
- ✅ Follow the templates provided

**Violation Examples:**
- ❌ Completing task without updating files
- ❌ Updating files with vague descriptions
- ❌ Deleting history from SESSION_LOG.md
- ❌ Not reading CURRENT_STATE.md before starting
- ❌ Duplicating work that was already done

---

## 📊 SUMMARY

| When | File | Action | Details |
|------|------|--------|---------|
| **Before starting** | `CURRENT_STATE.md` | READ | Check current state, known issues |
| **Before starting** | `SESSION_LOG.md` | READ | Check recent sessions, learn from others |
| **After completing** | `SESSION_LOG.md` | APPEND | Add your session details |
| **After completing** | `CURRENT_STATE.md` | OVERWRITE | Update with latest state |

---

## 🔗 Related Documentation

- **Automation Scripts:** `.github/instructions/automation-scripts.instructions.md`
- **Build System:** `README_ENFORCED_BUILD.md`
- **Chatbot Guide:** `scripts/CHATBOT_GUIDE.md`
- **Session Log:** `SESSION_LOG.md`
- **Current State:** `CURRENT_STATE.md`

---

**Version:** 1.0  
**Created:** October 26, 2025  
**Status:** 🔴 ENFORCED - ALL AI assistants must comply

---

**Remember:** These files are your shared memory across all chatbot sessions!  
**Use them wisely!** 🧠
