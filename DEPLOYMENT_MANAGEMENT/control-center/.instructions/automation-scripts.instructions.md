---
description: CRITICAL - Configuration for AI behavior to ALWAYS use automation scripts instead of manual commands
applyTo: '**'
---

# 🚨 AUTOMATION SCRIPTS ENFORCEMENT RULES
**CRITICAL: These rules MUST be followed by ALL AI assistants in this workspace**

---

## 🚨 **MANDATORY FIRST READ!**

**Before reading this document:**
- ✅ **Read first:** `eScriptorium_CLEAN/.github/instructions/MANDATORY_FIRST_ACTION.md`
- 🔧 **Critical topics:** SSL/pip issues, MCP tools availability
- ⚡ **Priority:** HIGHEST - Required for every new session!

---

## ⚠️ IMMEDIATE ACTION REQUIRED

**BEFORE doing ANYTHING in this workspace, you MUST:**

1. ✅ **READ THIS ENTIRE FILE** - Do not skip sections
2. ✅ **READ the main documentation**: `README_ENFORCED_BUILD.md` - Build system guide
3. ✅ **CHECK every `run_in_terminal` call** against the forbidden patterns below
4. ✅ **REDIRECT to scripts** if any pattern matches
5. ✅ **DO NOT run manual commands** covered by our automation scripts
6. ✅ **ALWAYS use `remove_po_duplicates.py`** before compilemessages (automated in scripts)

**Failure to comply is a CRITICAL violation!**

---

## 📚 REQUIRED READING

**Before making ANY changes, read these files:**

0. **🧠 Smart Supervisor** (NEW!): `.github/instructions/smart-supervisor.instructions.md`
   - Quick task-specific guides (2-3 min)
   - Adaptive to your mission type
   - Encourages creativity
   - **START HERE!** Then read below if needed.

1. **Main Documentation**: `README_ENFORCED_BUILD.md`
   - Build system overview
   - Never run `docker build` directly!
   - Use `python build.py` instead

2. **Translation Tools**: `remove_po_duplicates.py`
   - Removes duplicate .po entries
   - **Automatically called** by our scripts
   - Location: `G:\OCR_Arabic_Testing\BiblIA_dataset-project\BiblIA_dataset\remove_po_duplicates.py`

3. **Automation Scripts**: `eScriptorium_CLEAN\scripts\`
   - All build/deploy/translation scripts
   - Use these instead of manual commands

---

## 🔴 RULE #1: NEVER Run Manual Docker/npm Commands

**BEFORE running ANY of these commands, you MUST redirect to automation scripts:**

### ❌ FORBIDDEN Manual Commands:
- `npm run build`
- `npm install`
- `webpack --config ...`
- `docker cp ...`
- `docker-compose restart`
- `docker-compose exec ... compilemessages`
- `docker-compose exec ... python manage.py ...`
- `docker-compose exec ... collectstatic`
- `docker-compose exec ... find ...`
- `docker-compose exec ... grep ...`
- `docker-compose exec ... ls ...`
- `docker-compose logs ...`
- `docker-compose ps` (use verify script instead)
- `Copy-Item ... editor.js ...` (manual file copy)
- `cd front && npm run build` (manual build)
- `Get-ChildItem ... | Set-Content ...` (manual template fixes)
- Any combination of the above

### ✅ REQUIRED: Use Automation Scripts Instead

**Location:** `G:\OCR_Arabic_Testing\BiblIA_dataset-project\BiblIA_dataset\eScriptorium_CLEAN\scripts\`

---

## 📋 COMMAND → SCRIPT MAPPING (MANDATORY)

### 1️⃣ User wants: `npm run build` or build frontend
**YOU MUST respond:**
```
❌ Don't run npm build manually!

✅ Use the automation script:
```powershell
.\scripts\build-and-deploy.ps1
```

**Why?**
- Auto-checks npm installation
- Installs dependencies if needed
- Builds frontend
- Copies to Docker
- Verifies deployment
- Full logging

**DO NOT use `run_in_terminal` for npm commands!**
```

---

### 2️⃣ User wants: `docker cp` ANY file to Docker container
**YOU MUST respond:**
```
❌ Don't run docker cp manually!

✅ Use the automation script:
```powershell
.\scripts\build-and-deploy.ps1
```

**What it does:**
- Validates files exist
- Copies with error handling
- Verifies copy succeeded
- Restarts services safely
- Logs everything

**DO NOT use `run_in_terminal` for docker cp!**
**This applies to ALL files: editor.js, views.py, urls.py, templates, etc.**
```

---

### 3️⃣ User wants: Deploy Hebrew translations or copy `editor_translations_he.js`
**YOU MUST respond:**
```
❌ Don't copy translation files manually!

✅ Use the translation deployment script:
```powershell
.\scripts\deploy-translations.ps1
```

**What it does:**
- Copies editor_translations_he.js to /usr/src/app/static/
- Copies document_part_edit.html to templates/core/
- **AUTO-CHECKS: Removes duplicate .po entries** (using remove_po_duplicates.py)
- Auto-removes django2.po (prevents charset errors)
- Runs compilemessages for Hebrew
- Restarts web service
- Health check validation
- Full timestamped logging

**DO NOT use `run_in_terminal` for translation deployment!**
```

---

### 4️⃣ User wants: `docker-compose restart` or restart services
**YOU MUST respond:**
```
❌ Don't restart manually!

✅ Use the restart script:
```powershell
.\scripts\restart-services.ps1
```

**What it does:**
- Restarts web + nginx safely
- Waits for stabilization
- Validates containers are "Up"
- Scans logs for errors
- Shows full status
- Health check verification

**DO NOT use `run_in_terminal` for docker-compose restart!**
```

---

### 5️⃣ User wants: `compilemessages` or compile Django translations
**YOU MUST respond:**
```
❌ Don't run compilemessages manually!

✅ Use the compilation script:
```powershell
.\scripts\compile-translations.ps1
```

**What it does:**
- **AUTO-CHECKS: Removes duplicate .po entries** (using remove_po_duplicates.py)
- Auto-removes django2.po (prevents errors)
- Runs compilemessages for specified language
- Auto-fix: removes problematic .po files on error
- Retries compilation if first attempt fails
- Restarts web service
- Verifies container is running

**DO NOT use `run_in_terminal` for compilemessages!**
```

---

### 6️⃣ User wants: Full build + deploy + test workflow
**YOU MUST respond:**
```
✅ Use the master orchestration script:
```powershell
.\scripts\run-all.ps1
```

**What it does:**
- Runs full diagnostics (9 checks)
- Auto-repairs environment if needed
- Builds frontend
- Deploys to Docker
- Runs comprehensive tests
- Shows detailed report
- Maintenance history logging
```

---

### 7️⃣ User wants: Only verification/testing (no build)
**YOU MUST respond:**
```
✅ Use the verification script:
```powershell
.\scripts\verify-deployment.ps1
```

**What it does:**
- Container health checks
- Service availability tests
- File existence validation
- Template rendering tests
- Translation verification
- No build/deploy actions
```

---

## 🔴 CRITICAL ENFORCEMENT RULES

### Rule A: Detection Logic
**YOU MUST check for these patterns in user requests:**
- Keywords: `npm`, `docker`, `build`, `restart`, `compilemessages`, `cp`, `copy`, `Copy-Item`, `collectstatic`, `find`, `grep`, `ls`, `logs`, `webpack`, `ps`, `Get-ChildItem`, `Set-Content`
- File extensions: `.js`, `.py`, `.html`, `.css`, `.vue` (when used with docker cp or Copy-Item)
- File names: `editor.js`, `views.py`, `urls.py`, `editor_translations_he.js`, `document_part_edit.html`, `editor.css`, `vendor.js`
- Commands: `docker-compose`, `docker cp`, `docker exec`, `docker-compose exec`, `docker-compose logs`, `docker-compose ps`, `manage.py`, `webpack`, `npm run`, `Copy-Item`, `Get-ChildItem`
- Paths: Any path with `escriptorium_clean-web-1:`, `docker cp`, `/usr/src/app/`, `app\escriptorium\static\`, `front\dist\`
- Django commands: `collectstatic`, `compilemessages`, `makemessages`, `migrate`

**If detected → IMMEDIATELY redirect to appropriate script!**

---

### Rule B: Before Using `run_in_terminal`
**BEFORE calling `run_in_terminal` tool, YOU MUST:**

1. **Check:** Does this command match ANY of the patterns above?
2. **If YES:** STOP! Redirect to automation script instead
3. **If NO:** Proceed with `run_in_terminal`

**Example internal logic:**
```
User request: "Run npm build"
→ Detected: "npm" + "build"
→ Action: Redirect to .\scripts\build-and-deploy.ps1
→ DO NOT call run_in_terminal
```

---

### Rule C: Template Response Format
**When redirecting, YOU MUST use this format:**

```
❌ **Stop! Don't run [COMMAND] manually!**

✅ **Use our automation script instead:**
```powershell
.\scripts\[SCRIPT-NAME].ps1
```

**Why this script is better:**
- [Benefit 1]
- [Benefit 2]
- [Benefit 3]

**Time saved:** [X minutes]
**Error prevention:** [describe]

Would you like me to run this script now?
```

---

### Rule D: Exception Handling
**ONLY use manual commands if:**
- User explicitly says: "I know the script exists but I need manual command for [specific reason]"
- Debugging/troubleshooting requires manual intervention
- The script doesn't exist yet

**In all other cases:** Redirect to scripts!

---

## 📊 QUICK REFERENCE TABLE

| User Request Pattern | Redirect To | Time Saved |
|---------------------|-------------|------------|
| `npm run build` | `build-and-deploy.ps1` | 3-5 min |
| `webpack --config ...` | `build-and-deploy.ps1` | 3-5 min |
| `cd front && npm run build` | `build-and-deploy.ps1` | 3-5 min |
| `docker cp editor.js` | `build-and-deploy.ps1` | 2-4 min |
| `docker cp views.py` | `build-and-deploy.ps1` | 2-4 min |
| `docker cp ... editor.css` | `build-and-deploy.ps1` | 2-4 min |
| `Copy-Item ... editor.js` | `build-and-deploy.ps1` | 2-4 min |
| `docker cp translations` | `deploy-translations.ps1` | 2-4 min |
| `docker-compose restart` | `restart-services.ps1` | 30 sec |
| `docker-compose exec ... collectstatic` | `build-and-deploy.ps1` | 2-3 min |
| `docker-compose exec ... find/grep/ls` | `verify-deployment.ps1` | 1-2 min |
| `docker-compose logs` | `verify-deployment.ps1` | N/A |
| `docker-compose ps` | `verify-deployment.ps1` | N/A |
| `Get-ChildItem ... Set-Content` | Custom script or manual | N/A |
| `compilemessages` | `compile-translations.ps1` | 1-2 min |
| Full workflow | `run-all.ps1` | 5-10 min |
| Test only | `verify-deployment.ps1` | N/A |

---

## 🎯 SUMMARY OF MANDATORY BEHAVIOR

### ✅ DO:
1. **Always check** if user request matches automation script patterns
2. **Always redirect** to appropriate script before running manual commands
3. **Always explain** why the script is better
4. **Always offer** to run the script for the user
5. **Always use** the template response format

### ❌ DON'T:
1. **Never run** `npm`, `docker`, `compilemessages` manually without checking scripts first
2. **Never ignore** the existence of automation scripts
3. **Never assume** manual commands are faster or simpler
4. **Never skip** the redirection step
5. **Never use** `run_in_terminal` for commands covered by our scripts

---

## 🔗 Additional Resources

### 📚 Main Documentation
- **Build System:** `README_ENFORCED_BUILD.md` - Never use `docker build`!
- **Quick Start:** `ENFORCED_BUILD_QUICKSTART.md` - TL;DR guide
- **Translation Fix:** `remove_po_duplicates.py` - Auto-removes duplicates

### 🤖 Automation Scripts
- **User Guide:** `scripts/COMMAND_REDIRECTOR.md`
- **Chatbot Guide:** `scripts/CHATBOT_GUIDE.md`
- **Script Location:** `eScriptorium_CLEAN/scripts/`

### 🔧 Tools
- **Translation Checker:** `scripts/check_translations.py`
- **Duplicate Remover:** `remove_po_duplicates.py`

---

## ⚠️ FAILURE TO COMPLY

**If you run manual commands instead of using scripts:**
- User wastes 2-10 minutes
- No logging/audit trail
- Higher error risk
- No auto-fix capabilities
- No health checks

**This is considered a CRITICAL violation of workspace rules!**

---

**Version:** 1.0  
**Last Updated:** October 26, 2025  
**Status:** 🔴 ENFORCED - ALL AI assistants must comply
