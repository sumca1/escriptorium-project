# 📚 BiblIA Documentation
**User-Facing Guides & Internal Documentation**

<div dir="rtl">

**Last Updated:** 2025-10-30

## 🗂️ מבנה התיקייה

| תיקייה | תוכן | קהל יעד |
|--------|------|---------|
| **`docs/`** (כאן) | מדריכים למשתמש, API guides | מפתחים, משתמשים |
| **`docs/supervisor/`** | AI Supervisor documentation | AI Chatbots |
| **`docs/archive/`** | תיעוד היסטורי | ארכיון |
| **`.github/instructions/`** | Chatbot control, automation | Automation |
| **`temp/`** | קבצים זמניים | זמני בלבד |

---

## 📖 Quick Navigation

### 🤖 For AI Supervisor
- [**Supervisor Docs**](./supervisor/INDEX.md) - **START HERE** for essential documentation

### 👨‍💻 For Developers

#### 📋 Quick Start
- **[QUICK_REFERENCE.md](./QUICK_REFERENCE.md)** ⚡ **NEW!**
  - כרטיס התייחסות מהיר
  - One-liners, common operations
  - 5-minute read

#### Docker & Build Management
- **[DOCKER_WHITELIST_API_GUIDE.md](./DOCKER_WHITELIST_API_GUIDE.md)** 🔥
  - מדריך מקיף לשימוש ב-Docker Whitelist API
  - רישום אוטומטי של קבצים ל-Docker builds
  - דוגמאות מעשיות, CLI usage, best practices

#### Documentation & Cleanup
- **[AUTO_FILL_FROM_CODE_COMPLETE.md](../AUTO_FILL_FROM_CODE_COMPLETE.md)** 🚀 **LATEST!**
  - **Auto-Fill from Code System** - ייצור דוקומנטציה אוטומטי מקוד Python
  - 95% חסכון בזמן (3-5 דקות → 10 שניות)
  - AST parsing, test extraction, markdown generation
  - **6/6 Tests Passed** ✅

- **[SMART_DOCUMENTATION_SYSTEM_SUMMARY.md](./SMART_DOCUMENTATION_SYSTEM_SUMMARY.md)** ✨
  - סיכום מערכת ניהול מסמכים וניקוי
  - API למסמכים, ניקוי אוטומטי, ארגון workspace
  - 99.3% חסכון בזמן (35 דק → 15 שניות)

- **[DOCUMENTATION_METHODS_GUIDE.md](./DOCUMENTATION_METHODS_GUIDE.md)** 🎯
  - **מתודות לניהול מסמכים** - המדריך המלא
  - 7 documentation methods עם smart routing
  - Decision tree, best practices, דוגמאות מלאות
  - **מבוסס על Smart Questionnaire System (2024-10)**

#### 📚 API Documentation
- [DOCKER_WHITELIST_API_GUIDE.md](./DOCKER_WHITELIST_API_GUIDE.md) - Docker Whitelist Manager API
- [docker_whitelist_manager.add_file()_API_API_GUIDE](docs\docker_whitelist_manager.add_file()_API_API_GUIDE.md)
- [code_documentation_generator_API_Documentation_API_GUIDE](docs\code_documentation_generator_API_Documentation_API_GUIDE.md)

#### 📖 User Guides
- [DOCUMENTATION_METHODS_GUIDE.md](./DOCUMENTATION_METHODS_GUIDE.md) - Documentation Management Methods
- [SMART_DOCUMENTATION_SYSTEM_SUMMARY.md](./SMART_DOCUMENTATION_SYSTEM_SUMMARY.md) - Smart Documentation System

#### ⚡ Quick References
- [QUICK_REFERENCE.md](./QUICK_REFERENCE.md) - Quick Reference Card
- [code_documentation_generator_-_Quick_Reference_QUICK_REFERENCE](docs\code_documentation_generator_-_Quick_Reference_QUICK_REFERENCE.md)
- [Test_Quick_Reference_QUICK_REFERENCE](docs\Test_Quick_Reference_QUICK_REFERENCE.md)

#### 🔧 Troubleshooting Guides
*(No troubleshooting guides yet - create one using `TROUBLESHOOTING_GUIDE` method!)*

#### Archive
- [Archive](./archive/INDEX.md) - Historical documentation

---

## ✍️ יצירת מסמכים חדשים - הדרך הנכונה!

### ❌ אל תעשה ככה (הדרך הישנה):
```python
create_file("MY_GUIDE.md", content)  # איפה זה נשמר? 🤔
```

### ✅ עשה ככה (הדרך החדשה):
```python
from chatbot_control_api import ChatbotAPI

api = ChatbotAPI()

# המערכת תשים את הקובץ במקום הנכון!
api.create_documentation(
    filename="MY_FEATURE_GUIDE.md",
    content=guide_content,
    doc_type="guide",  # → docs/
    description="User guide for my feature",
    auto_register=True  # רישום אוטומטי ל-Docker
)
```

### סוגי מסמכים:
- `doc_type="guide"` → `docs/` (מדריכים למשתמש)
- `doc_type="internal"` → `.github/instructions/` (פנימי)
- `doc_type="api"` → `.github/instructions/` (API docs)
- `doc_type="temp"` → `temp/` (זמני - ימחק)

---

## 🧹 ניקוי אחרי עבודה

```python
api = ChatbotAPI()

# ניקוי רגיל (בטוח)
api.cleanup_after_work()

# ניקוי אגרסיבי (גם backups)
api.cleanup_after_work(aggressive=True)

# תצוגה מקדימה
api.cleanup_after_work(dry_run=True)
```

**מה נמחק:**
- `temp/` - כל התיקייה
- `__pycache__/`, `*.pyc`
- `.pytest_cache/`, `htmlcov/`
- `*.log`, `bandit_*.json`
- `build_results_*.json`

---

## 🗂️ ארגון אוטומטי

```python
# העבר קבצים מהשורש למקום הנכון
api.organize_workspace()
```

---

## 📋 Best Practices

✅ השתמש ב-`api.create_documentation()`  
✅ נקה אחרי עבודה: `api.cleanup_after_work()`  
✅ ארגן workspace: `api.organize_workspace()`  
✅ רשום ל-Docker: `auto_register=True`  

❌ אל תיצור קבצים בשורש  
❌ אל תשכח לנקות temp/  
❌ אל תשמור דוחות ישנים  

---

## Structure

```
docs/
├── supervisor/          # 20 essential files for AI Supervisor
│   ├── INDEX.md        # Main entry point
│   ├── guides/         # How-to instructions (5 files)
│   ├── status/         # Current state (2 files)
│   ├── api/            # API references (2 files)
│   ├── troubleshooting/# Problem solving (3 files)
│   ├── implementation/ # Completed features (5 files)
│   └── quick_reference/# Cheat sheets (3 files)
│
└── archive/            # 171 archived files
    ├── low_quality/    # Quality score < 20 (8 files)
    └── 2024-10/        # General archive (~163 files)
```

## Statistics

- **Total original files:** 191
- **Supervisor essential:** 20 (10.5%)
- **Archived:** 171 (89.5%)
- **Average quality (supervisor):** 80.4

## Philosophy

We keep only **high-quality, actionable, implementation-focused** documentation
in the supervisor directory. Everything else is archived but remains accessible.

---

*This structure was automatically generated on 2025-10-28*
