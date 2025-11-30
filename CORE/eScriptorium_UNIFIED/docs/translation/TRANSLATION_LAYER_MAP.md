# 🎯 Translation Layer Map - מפת שכבות תרגום (eScriptorium_CLEAN)

> **Note:** This is a mirror/copy for chatbots working in eScriptorium_CLEAN  
> **Main file:** `../TRANSLATION_LAYER_MAP.md`  
> **Status:** 🔴 CRITICAL - Read before translating!

---

## 📊 Quick Reference

| Layer | File | Missing | Priority |
|-------|------|---------|----------|
| **Frontend** | `front/vue/locales/he.json` | **~74** | 🔴 High |
| **Backend** | `locale/he/LC_MESSAGES/django.po` | **~15** | 🟡 Medium |

---

## 🚨 CRITICAL WARNINGS

### ❌ DON'T:
- ❌ אל תוסיף `cer.*` strings ל-django.po (הם Frontend!)
- ❌ אל תסמוך על `strings_to_translate.txt` - הוא מערבב שכבות!

### ✅ DO:
- ✅ Frontend strings (`cer.*`, ~74) → `front/vue/locales/he.json`
- ✅ Backend strings (~15) → `locale/he/LC_MESSAGES/django.po`
- ✅ Use `translate_cer_strings.py` as source for CER translations

---

## 📁 Files in This Folder:

### Frontend:
```
front/vue/locales/he.json       ← Add CER translations here
```

### Backend:
```
locale/he/LC_MESSAGES/django.po ← Add backend messages here
```

### Tools:
```
translate_cer_strings.py        ← All 74 CER translations ready!
check_translation_status.py     ← Check Frontend status
extract_missing_translations.py ← Lists all (but mixes layers!)
```

---

## 🎯 Quick Actions

### To translate Frontend (CER):
```powershell
# 1. Open he.json
code front/vue/locales/he.json

# 2. Find "cer": { section (line ~1126)

# 3. Copy from translate_cer_strings.py

# 4. Build and deploy
.\scripts\build-and-deploy.ps1 -Quick
```

### To translate Backend:
```powershell
# 1. Open django.po
code locale/he/LC_MESSAGES/django.po

# 2. Find empty msgstr "" entries

# 3. Add Hebrew translations

# 4. Deploy
.\scripts\deploy-translations.ps1
```

---

**📌 For full details, see:** `../TRANSLATION_LAYER_MAP.md`
