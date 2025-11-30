# 🚀 Command Center - Quick Start Guide for Manager

**Status:** ✅ READY TO USE  
**Time to test:** 2 minutes

---

## 🎯 What You Got

A **centralized dashboard** that shows:
- ✅ All chatbot sessions (who did what, when)
- ✅ Active project stages
- ✅ Known patterns & solutions
- ✅ **Automatic alerts** when maintenance is needed

**No more searching through logs!** Everything in one place.

---

## 🖥️ How to Open (3 ways)

### Option 1: Direct Open (Simplest)
```powershell
# Just double-click this file:
BUILD_MANAGER_DASHBOARD.html
```

### Option 2: From PowerShell
```powershell
cd eScriptorium_CLEAN
start BUILD_MANAGER_DASHBOARD.html
```

### Option 3: With Live Server (if you have CORS issues)
```powershell
cd eScriptorium_CLEAN
npx live-server --open=BUILD_MANAGER_DASHBOARD.html
```

---

## 📊 What You'll See

### 1. **Dashboard Summary** (Top metrics)
- 📈 Total sessions
- 🗺️ Active stages
- 📝 Patterns documented
- 🚨 **SIGNIFICANT CHANGE ALERT** (red if maintenance needed)

### 2. **Stage Map** (What's in progress)
- Lists all active project stages
- Shows session count and last activity
- Color-coded for easy scanning

### 3. **Event Feed** (Timeline)
- Last 20 chatbot sessions
- Shows who did what, when
- Significant changes highlighted in red

### 4. **Patterns Explorer** (Known issues)
- Table of recurring patterns
- Frequency count
- Link to solutions

**Auto-refreshes every 2 minutes!**

---

## 🚨 If You See RED Alert

**"שינוי משמעותי ממתין" = Significant Change Pending**

This means a chatbot made a major change (architecture, schema, etc.).

**What to do:**
1. Open `MAINTENANCE_PLAYBOOK.md`
2. Follow the 8-step checklist (~1-2 hours)
3. After maintenance, update `CURRENT_STATE.md`:
   ```markdown
   significant_change_pending: **false**
   ```
4. Alert turns GREEN ✅

---

## 🔄 How to Refresh Data

The dashboard auto-refreshes, but you can also:

1. **Manual refresh:** Click the **"🔄 רענן מרכז פיקוד"** button
2. **Update data:** Run in PowerShell:
   ```powershell
   python scripts\command_center_export.py
   ```
3. **Reload browser:** Press F5

---

## 📖 Full Documentation

If you want more details:
- **Architecture:** `COMMAND_CENTER.md`
- **Complete summary:** `COMMAND_CENTER_IMPLEMENTATION_SUMMARY.md`
- **Maintenance guide:** `MAINTENANCE_PLAYBOOK.md`

---

## ✅ Test Checklist (2 minutes)

- [ ] Open `BUILD_MANAGER_DASHBOARD.html`
- [ ] See "Command Center" section (blue background)
- [ ] Check "Dashboard Summary" shows 2 sessions
- [ ] Verify "Significant Change" box is RED (true)
- [ ] See "Stage Map" shows "phase-0-infrastructure"
- [ ] Check "Event Feed" shows 2 sessions
- [ ] See "Patterns Explorer" shows 2 patterns
- [ ] Click "🔄 רענן מרכז פיקוד" button (should work)

**If all ✅ → System is working perfectly!**

---

## 🐛 Troubleshooting

### Problem: "Cannot find command_center.json"
**Solution:**
```powershell
python scripts\command_center_export.py
```

### Problem: Fetch error / CORS issue
**Solution:** Use live server:
```powershell
npx live-server --open=BUILD_MANAGER_DASHBOARD.html
```

### Problem: Data not updating
**Solution:**
1. Check `SESSION_LOG.md` has tagged sessions
2. Run `python scripts\command_center_export.py`
3. Refresh browser (F5)

---

## 🎯 Next Steps After Approval

1. **If you approve:** Set `significant_change_pending: false` (after maintenance)
2. **Proceed to:** Phase 1 Implementation (Surya OCR Integration)
3. **Future chatbots:** Will automatically use this system

---

## 💡 Pro Tip

**Bookmark this page:** `BUILD_MANAGER_DASHBOARD.html`

Open it whenever you want to see:
- What chatbots are doing
- Project progress
- Known issues & solutions

**No need to dig through log files anymore!** 🎉

---

**Created:** 27 October 2025  
**By:** Claude - Command Center Architect  
**Status:** ✅ Production Ready

**Questions?** Check `COMMAND_CENTER_IMPLEMENTATION_SUMMARY.md`
