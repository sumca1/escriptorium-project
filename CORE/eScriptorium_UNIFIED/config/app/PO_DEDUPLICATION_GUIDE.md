# PO File Deduplication Integration

## Overview
This integration automatically removes duplicate translation entries from `.po` files during the Django build/compilation process. It ensures that all locale files (`he/LC_MESSAGES/django.po`, `fr/LC_MESSAGES/django.po`, etc.) remain clean and free of duplicate msgid entries.

## Components

### 1. Django Management Command
**File:** `escriptorium/management/commands/dedupe_po_messages.py`

A Django management command that:
- Scans locale directories for `.po` files
- Identifies duplicate msgid entries
- Removes duplicates while preferring entries with translations
- Optionally creates timestamped backups

**Usage:**
```bash
# Scan and remove duplicates in-place with backup
python manage.py dedupe_po_messages --inplace --backup

# Dry-run (no changes)
python manage.py dedupe_po_messages --dry-run

# Custom locale directory
python manage.py dedupe_po_messages --locale-dir /path/to/locale --inplace
```

### 2. Automatic Integration
**File:** `entrypoint.sh`

Updated Docker entrypoint that automatically:
1. Compiles messages with `compilemessages`
2. Removes duplicates with `dedupe_po_messages --inplace --backup`
3. Continues with normal Django startup

**Workflow:**
```
Docker Container Starts
    ↓
compilemessages (compile .po to .mo)
    ↓
dedupe_po_messages (remove duplicates)
    ↓
collectstatic
    ↓
migrate
    ↓
Application running ✓
```

### 3. Testing
**File:** `test_dedupe_integration.py`

Integration test that:
- Verifies the command can be imported
- Lists all `.po` files in locale directories
- Runs a dry-run test to show what would be deduplicated

**Usage:**
```bash
python test_dedupe_integration.py
```

## Files Modified/Created

| File | Type | Purpose |
|------|------|---------|
| `escriptorium/management/commands/dedupe_po_messages.py` | NEW | Django management command |
| `entrypoint.sh` | MODIFIED | Added dedupe step |
| `test_dedupe_integration.py` | NEW | Integration test |
| `.github/workflows/dedupe-po.yml` | NEW | GitHub Actions workflow |
| `remove_po_duplicates.py` | UPDATED | Added --locale-dir support |

## Requirements

The only additional Python dependency is `polib`:
```bash
pip install polib
```

This is already included in the Docker image requirements.

## How It Works

### Deduplication Logic

1. **Load PO File:** Uses `polib` to safely parse the `.po` file
2. **Identify Duplicates:** Groups entries by `(msgctxt, msgid)` key
3. **Keep First:** Preserves the first occurrence of each unique msgid
4. **Prefer Translations:** If duplicates exist, keeps the one with a non-empty `msgstr`
5. **Write:** Saves the deduplicated file

### Example

**Before (9 duplicates):**
```
msgid "Description"
msgstr "תיאור"

msgid "Description"  # DUPLICATE
msgstr ""

msgid "Owner"
msgstr "בעלים"

msgid "Owner"  # DUPLICATE
msgstr ""
```

**After (deduplicated):**
```
msgid "Description"
msgstr "תיאור"

msgid "Owner"
msgstr "בעלים"
```

## Running Manually

### One-time cleanup:
```bash
# In Docker container
python manage.py dedupe_po_messages --inplace --backup

# Or via Docker
docker-compose exec app python manage.py dedupe_po_messages --inplace --backup
```

### Check without modifying:
```bash
python manage.py dedupe_po_messages --dry-run
```

### With custom locale path:
```bash
python manage.py dedupe_po_messages --locale-dir ./locale --inplace --backup
```

## Continuous Integration

### GitHub Actions
**File:** `.github/workflows/dedupe-po.yml`

Workflow triggers:
- On push to `main`, `master`, or `develop`
- On pull requests
- Weekly schedule (Mondays)

Automatically:
1. Installs Python + polib
2. Scans all `.po` files
3. Removes duplicates
4. Commits cleaned files back to repo
5. Pushes changes (for push events)

## Troubleshooting

### Issue: "polib not found"
**Solution:** Install it
```bash
pip install polib
```

### Issue: Management command not found
**Solution:** Ensure the file structure exists:
```
escriptorium/
  management/
    __init__.py
    commands/
      __init__.py
      dedupe_po_messages.py
```

### Issue: No .po files found
**Solution:** Check Django settings:
```python
# settings.py
LOCALE_PATHS = [
    os.path.join(BASE_DIR, 'locale'),
]
```

## Performance

- **Typical execution time:** < 1 second per .po file
- **Memory usage:** Minimal (loads entire file into memory)
- **I/O:** Sequential (one file at a time)

The operation is fast enough to run as part of every build without noticeable overhead.

## Hebrew Translation Example

The Hebrew django translation file (`he/LC_MESSAGES/django.po`) had:
- **Original:** 1237 entries with 9 duplicates
- **After dedup:** 1228 unique entries
- **Duplicates removed:** Description, Owner, Created At, Total Characters, Content, Metadata, Document, Ground Truth Corpus, Running

## Future Enhancements

Possible additions:
- [ ] Fuzzy translation handling
- [ ] Cross-language duplicate detection
- [ ] Translation coverage reports
- [ ] Automatic translation suggestion for duplicates
- [ ] Integration with Weblate or other TMS

---

**Last Updated:** October 26, 2025
**Status:** ✓ Production Ready
