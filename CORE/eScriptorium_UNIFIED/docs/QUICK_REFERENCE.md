# 📋 Quick Reference Card
**Chatbot Control API - Documentation & Cleanup**

<div dir="rtl">

## 🚀 פעולות נפוצות

### יצירת מסמך

```python
from chatbot_control_api import ChatbotAPI
api = ChatbotAPI()

# מדריך למשתמש → docs/
api.create_documentation(
    "MY_GUIDE.md", 
    content, 
    doc_type="guide"
)

# תיעוד פנימי → .github/instructions/
api.create_documentation(
    "internal_doc.py", 
    content, 
    doc_type="internal"
)

# קובץ זמני → temp/
api.create_documentation(
    "temp_file.json", 
    content, 
    doc_type="temp"
)
```

### ניקוי

```python
# תצוגה מקדימה
api.cleanup_after_work(dry_run=True)

# ניקוי רגיל
api.cleanup_after_work()

# ניקוי אגרסיבי
api.cleanup_after_work(aggressive=True)
```

### ארגון

```python
# ארגן קבצים מפוזרים
api.organize_workspace()

# העבר קובץ ספציפי
api.move_documentation(
    "file.md",
    from_type="root",
    to_type="guide"
)
```

### Docker Whitelist

```python
# רישום אוטומטי
api.auto_register_new_files(auto_commit=True)

# רישום ידני
api.register_file_to_docker(
    "app/my_file.py",
    category="our_addition",
    reason="New feature"
)

# ולידציה
api.validate_docker_whitelist()
```

---

## 📁 מבנה תיקיות

| מיקום | תוכן | doc_type |
|-------|------|----------|
| `docs/` | מדריכים למשתמש | `"guide"` |
| `.github/instructions/` | תיעוד פנימי | `"internal"` או `"api"` |
| `temp/` | קבצים זמניים | `"temp"` |
| root | רק חיוניים | - |

---

## 🧹 מה נמחק ב-cleanup?

### תמיד:
- `temp/*`
- `__pycache__/`, `*.pyc`
- `.pytest_cache/`, `htmlcov/`
- `*.log`, `bandit_*.json`
- `build_results_*.json`

### Aggressive:
- `BACKUP_*.md`
- `*_MANIFEST.md`
- `*.bak`, `*~`

---

## ⚡ One-Liners

```python
from chatbot_control_api import ChatbotAPI
api = ChatbotAPI()

# ניקוי מהיר
api.cleanup_after_work()

# ארגון + ניקוי
api.organize_workspace(); api.cleanup_after_work()

# רישום + ולידציה
api.auto_register_new_files(auto_commit=True); api.validate_docker_whitelist()
```

---

## 🎯 Workflow מלא

```python
# אחרי סיום Priority
api.create_documentation("PRIORITY_X.md", summary, "guide")
api.organize_workspace()
api.auto_register_new_files(auto_commit=True)
api.cleanup_after_work()
api.validate_docker_whitelist()
api.smart_docker_build("web")
```

---

## 📖 מדריכים מלאים

- **Docker Whitelist**: [docs/DOCKER_WHITELIST_API_GUIDE.md](./DOCKER_WHITELIST_API_GUIDE.md)
- **System Summary**: [docs/SMART_DOCUMENTATION_SYSTEM_SUMMARY.md](./SMART_DOCUMENTATION_SYSTEM_SUMMARY.md)
- **Examples**: `example_smart_workflow.py`

</div>
