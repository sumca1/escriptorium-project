# 🚀 Smart Category Manager - Quick Start
**The intelligent bridge between chatbot and supervisor**

---

## ⚡ TL;DR - 3 Commands Only!

```powershell
# 1. Start session (AI detects what you're doing)
python cm.py start

# 2. Fill the pre-filled form (3 minutes)
# Editor opens automatically

# 3. Submit
python cm.py submit
```

**That's it!** ✅

---

## 🎯 How It Works

### 1️⃣ You Start a Session
```powershell
python cm.py start
```

**AI asks:** "What are you working on?"

**You type:** 
- "fixing translation bug" ✅
- "need to run batch OCR" ✅
- "Docker container is broken" ✅
- Just keywords: "translation", "ocr", "docker" ✅

### 2️⃣ AI Detects & Builds Context

**AI analyzes:**
- Your description
- Git changes (what files you modified)
- Category keywords

**AI builds context package:**
```
🧠 Smart Detection:
   Category: translation
   Form: translation-fix

📦 Building context...
   ✅ Current status loaded
   ✅ Found 3 guides
   ✅ Found 5 scripts
   ✅ Last 3 sessions loaded
   ✅ Common issues loaded
   ✅ Git changes detected

📝 Creating pre-filled form...
```

### 3️⃣ You Get Pre-Filled Form

**Form opens in editor with:**

```yaml
# ========================================
# CONTEXT (read this first!)
# ========================================
_context:
  category: translation
  current_status:
    last_task: "Added Hebrew translations for CER"
    status: "active"
  
  available_guides:
    - QUICK_GUIDE.md - "Translation workflow"
    - COMMON_ISSUES.md - "Known problems"
  
  available_scripts:
    - compile-translations.ps1
    - deploy-translations.ps1
  
  recent_work:
    - "Fixed duplicate entries in django.po"
    - "Added 74 new strings to he.json"
  
  common_issues:
    - "Translation not showing? Clear browser cache!"
    - "Duplicate entries? Run remove_po_duplicates.py"

# ========================================
# FILL THIS OUT (only 3-5 fields!)
# ========================================

# Auto-filled from git
date: 2025/10/27
time: 22:45

# Fill these:
task_title: "Fix ???"
description: |
  What did you fix?

files_changed:  # Auto-detected!
  - path: front/vue/locales/he.json
    lines_added: 12
    lines_removed: 3

issues:
  - problem: "???"
    solution: "???"

# Done!
```

### 4️⃣ You Fill 3-5 Fields

**Only fill:**
- `task_title` - What you did (1 line)
- `description` - How you did it (2-3 lines)
- `issues` - Problems you encountered (if any)

**Already filled for you:**
- Date/time ✅
- Files changed (from git) ✅
- Context (guides, scripts, status) ✅

**Time: 3 minutes!** ⏱️

### 5️⃣ Submit

```powershell
python cm.py submit
```

**AI processes:**
```
📤 Submitting...
   ✅ Updated categories/translation/session_log.yaml
   ✅ Updated categories/translation/current_state.yaml
   ✅ Updated SESSION_LOG.md (global)
   
✅ Done!
```

---

## 🎨 Example Session

```powershell
PS> python cm.py start

🤖 What are you working on?
Your input: fixing Hebrew translation in editor

🧠 Analyzing: 'fixing Hebrew translation in editor'...

✅ Detected:
   Category: translation
   Form: translation-fix

📦 Building context for translation...
   ✅ Loaded current state
   ✅ Found 2 guides
   ✅ Found 3 scripts
   ✅ Loaded 3 recent sessions
   ✅ Detected 2 changed files

📝 Creating pre-filled form...

✅ Form ready: sessions/translation-fix_2025-10-27_2245.yaml

Opening in editor...

======================================================================
📝 Fill the form and then run:
   python cm.py submit
======================================================================
```

**Form opens in VS Code:**
```yaml
_context:
  current_status:
    last_task: "Added CER translations"
  available_guides:
    - QUICK_GUIDE.md
  available_scripts:
    - compile-translations.ps1
  recent_work:
    - "Fixed duplicate .po entries"
  common_issues:
    - "Clear browser cache if not showing"
  changed_files:
    - path: front/vue/locales/he.json
      lines_added: 5

# Your part (fill this):
task_title: "Fixed RTL alignment in editor tooltips"
description: |
  Editor tooltips were displaying LTR.
  Added dir="rtl" to tooltip component.

issues:
  - problem: "Tooltips ignored Hebrew RTL"
    solution: "Added dir attribute to component"
    time_spent_minutes: 15

# Done!
```

**Save and submit:**
```powershell
PS> python cm.py submit

✅ Session submitted!
```

---

## 📋 Available Categories & Forms

```powershell
python cm.py list-forms
```

Output:
```
📂 TRANSLATION:
   • translation-fix
   • translation-update
   • translation-feature

📂 OCR SURYA:
   • ocr_surya-bugfix
   • ocr_surya-batch-run
   • ocr_surya-new-engine

📂 DOCKER DEVOPS:
   • docker_devops-fix
   • docker_devops-deployment

📂 BUILD DEPLOYMENT:
   • build_deployment-optimization
   • build_deployment-fix
```

---

## 🔍 How Intent Detection Works

**AI looks for:**

### Keywords in Your Description
- Translation: `translation`, `translate`, `תרגום`, `he.json`
- OCR: `ocr`, `surya`, `batch`, `images`
- Docker: `docker`, `container`, `deploy`
- Build: `build`, `npm`, `webpack`, `frontend`

### Files You Changed (Git)
- Modified `he.json`? → Translation category
- Modified `batch_ocr.py`? → OCR category
- Modified `docker-compose.yml`? → Docker category
- Modified `package.json`? → Build category

### Form Type Detection
- Keywords `fix`, `bug`, `תיקון` → Fix form
- Keywords `add`, `update`, `new` → Update form
- Keywords `optimize`, `faster` → Optimization form

**Score-based ranking:** Best match wins! 🏆

---

## 🎯 Benefits vs Manual Method

### ⏱️ Time Comparison

| Task | Manual | Smart CM | Saved |
|------|--------|----------|-------|
| Read docs | 5 min | 0 min | 5 min |
| Find guides | 3 min | Auto | 3 min |
| Open files | 2 min | Auto | 2 min |
| Fill session log | 4 min | 3 min | 1 min |
| Update state | 2 min | Auto | 2 min |
| **Total** | **16 min** | **3 min** | **13 min** |

**81% time saving!** 🚀

### 📦 What You Get Automatically

**Context Package:**
- ✅ Current status of category
- ✅ Available guides (auto-discovered)
- ✅ Available scripts (auto-discovered)
- ✅ Last 3 sessions (what others did)
- ✅ Common issues & solutions
- ✅ Your git changes (auto-detected)

**Pre-filled Form:**
- ✅ Date/time
- ✅ Files changed (from git)
- ✅ Basic structure
- ❌ Only 3-5 fields you need to fill!

**Auto-routing:**
- ✅ Updates category session log
- ✅ Updates category current state
- ✅ Updates global SESSION_LOG.md
- ✅ Creates new guides/scripts if you add them

---

## 🐛 Troubleshooting

### "Could not detect category"
**Solution:** Be more specific
- ❌ "fixing stuff"
- ✅ "fixing translation in he.json"

### "No form template found"
**Solution:** Use generic template
- AI will create basic template
- You can add your own template to `forms/` directory

### "Git not available"
**Solution:** Manual context building
- AI will work without git
- You'll need to fill `files_changed` manually

---

## 💡 Pro Tips

### Tip 1: Use Keywords
```
Good: "translation bug in Hebrew strings"
Better: "he.json translation fix"
Best: "fixing RTL in front/vue/locales/he.json"
```

### Tip 2: Review Context First
The `_context` section has everything you need:
- Check recent work → avoid duplication
- Check common issues → known solutions
- Check available guides → read before starting

### Tip 3: Add Resources While Working
```yaml
new_resources:
  - type: guide
    filename: "my_discovery.md"
    content: |
      # I discovered that...
      This will help others!
```

Auto-saved to `categories/[category]/guides/`!

### Tip 4: Check Category Status
```powershell
python cm.py view translation
```

Shows:
- Last task
- Recent changes
- Active issues

---

## 🎓 Advanced Usage

### Custom Form Template
Create your own in `forms/`:

```yaml
# forms/my-custom-form.yaml
task_title: ???
my_field: ???
```

Use it:
```powershell
python cm.py start
# Type: "my custom task"
# AI detects your keywords
```

### Multiple Sessions
```powershell
# Session 1
python cm.py start
# ... work ...
python cm.py submit

# Session 2 (same day)
python cm.py start
# Context includes Session 1 results!
```

---

## 📊 Architecture

```
cm.py (Smart Manager)
    ↓
Intent Detection → Category + Form Type
    ↓
Context Building → Load everything relevant
    ↓
Form Generation → Pre-filled YAML
    ↓
You fill 3-5 fields (3 min)
    ↓
Submit → Auto-routes to correct files
```

---

## ✅ Quick Reference

```bash
# Start new session (interactive)
python cm.py start

# Submit filled form
python cm.py submit

# List all available forms
python cm.py list-forms

# View category status
python cm.py view [category]
```

---

## 🚀 Ready to Start?

```powershell
python cm.py start
```

**The AI will guide you from here!** 🤖✨

---

**Version:** 1.0  
**Created:** October 27, 2025  
**Goal:** Make documentation effortless! 📝
