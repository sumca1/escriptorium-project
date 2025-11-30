# Documentation Methods - Quick Reference

## 🚀 Common Usage

### List all methods
```python
api.list_documentation_methods()
```

### Get method info
```python
api.get_method_info("API_DOCUMENTATION")
```

### Use a method
```python
api.use_documentation_method(
    "USER_GUIDE",
    title="My Guide",
    content="..."
)
```

## 📁 Directory Structure

```
eScriptorium_CLEAN/
├── DOCUMENTATION_METHODS.yaml ← Methods config
├── docs/ ← User-facing docs
│   └── DOCUMENTATION_METHODS_GUIDE.md
├── .github/instructions/ ← Internal docs
│   └── chatbot_control_api.py
└── templates/documentation/ ← Templates
    ├── api_documentation_template.md
    ├── user_guide_template.md
    └── quick_reference_template.md
```

## ⚡ Quick Commands

```python
# Python API
from chatbot_control_api import ChatbotAPI
api = ChatbotAPI()
api.use_documentation_method("API_DOCUMENTATION", "My API", content)
```

```bash
# CLI
python chatbot_control_api.py list-methods
python chatbot_control_api.py method-info API_DOCUMENTATION
python chatbot_control_api.py use-method USER_GUIDE "My Guide" content.md
```

---

**Created:** 30/10/2025  
**Version:** 1.0  
**Status:** 🟢 Test Document
