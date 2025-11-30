# 🔧 SegmOnto Installation - All Browsers Complete Guide

**תאריך:** 26 אוקטובר 2025  
**גרסה:** 1.1 (Official Release)  
**מקום הקבצים:** `G:\OCR_Arabic_Testing\BiblIA_dataset-project\BiblIA_dataset\eScriptorium_CLEAN\segmonto-official\`

---

## ✅ **STEP 1: Chrome Installation**

### **1. Open Chrome Extensions**
```
URL: chrome://extensions/
or: ⋮ Menu → More Tools → Extensions
```

### **2. Enable Developer Mode**
- Top right corner
- Toggle: **Developer mode** → **ON** (blue) ✅

### **3. Click "Load unpacked"**
- Button at top left
- Select folder: 
  ```
  G:\OCR_Arabic_Testing\BiblIA_dataset-project\BiblIA_dataset\eScriptorium_CLEAN\segmonto-official
  ```
- Click **Select Folder**

### **4. Verify Installation**
✅ Extension appears in list  
✅ Name: "eScriptorium Segmonto Live Checker"  
✅ Icon: ✓ in circle  
✅ Status: Enabled (blue toggle)  
✅ Icon appears in top-right toolbar

### **5. Test It**
- Click the ✓ icon in top-right
- Should see popup window
- Success! 🎉

---

## ✅ **STEP 2: Edge Installation**

### **1. Open Edge Extensions**
```
URL: edge://extensions/
or: ⋮ Menu → Extensions → Manage extensions
```

### **2. Enable Developer Mode**
- Bottom right corner
- Toggle: **Developer mode** → **ON** (blue) ✅

### **3. Click "Load unpacked"**
- Button at top left
- Select folder: 
  ```
  G:\OCR_Arabic_Testing\BiblIA_dataset-project\BiblIA_dataset\eScriptorium_CLEAN\segmonto-official
  ```
- Click **Select Folder**

### **4. Verify Installation**
✅ Extension appears in list  
✅ Name: "eScriptorium Segmonto Live Checker"  
✅ Icon: ✓ in circle  
✅ Status: Enabled (blue toggle)  
✅ Icon appears in top-right toolbar

### **5. Test It**
- Click the ✓ icon in top-right
- Should see popup window
- Success! 🎉

---

## ✅ **STEP 3: Firefox Installation**

### **1. Open Firefox about:debugging**
```
URL: about:debugging
or: about:debugging#/runtime/this-firefox
```

### **2. Click "This Firefox"**
- Left sidebar
- Select: **This Firefox**

### **3. Click "Load Temporary Add-on..."**
- Button at top
- Navigate to: 
  ```
  G:\OCR_Arabic_Testing\BiblIA_dataset-project\BiblIA_dataset\eScriptorium_CLEAN\segmonto-official\manifest.json
  ```
- Select **manifest.json**
- Click **Open**

### **4. Verify Installation**
✅ Extension appears in list  
✅ Name: "eScriptorium Segmonto Live Checker"  
✅ Status: Temporary extension  
✅ Icon appears in top-right toolbar

### **5. Test It**
- Click the ✓ icon in top-right
- Should see popup window
- Success! 🎉

**Note:** ⚠️ Temporary in Firefox = removed when Firefox closes. Reload with about:debugging each session.

---

## 🧪 **Testing SegmOnto After Installation**

### **Test in Each Browser:**

1. **Open eScriptorium**
   ```
   http://localhost:8082/document/16/part/251/edit/
   ```

2. **Click SegmOnto Icon** (✓ in top-right)
   - Popup should appear

3. **Enter Information (Optional)**
   ```
   Auth Token: [leave empty for demo]
   URL: http://localhost:8082/document/16/part/251/edit/
   ```

4. **Click "Check Document"**
   - Should analyze regions and lines
   - Show results:
     - ✅ Regions OK
     - ✅ Lines OK
     - ❌ Any errors

5. **Expected Output**
   ```
   Overall: 85% compliant
   
   ✅ 17/20 Regions are valid
   ❌ 3 regions have invalid types:
      - Region 5: "UnknownZone" (invalid)
      - Region 12: "BadType" (invalid)
   
   ✅ 45/47 Lines are valid
   ❌ 2 lines have issues:
      - Line 23: No typology
      - Line 44: Invalid type "WeirdLine"
   ```

---

## 📊 **SegmOnto Valid Types Reference**

### **Valid Zones (Regions):**
```
CustomZone, DamageZone, GraphicZone, DigitizationArtefactZone,
DropCapitalZone, MainZone, MarginTextZone, MusicZone,
NumberingZone, QuireMarksZone, RunningTitleZone, SealZone,
StampZone, TableZone, TitlePageZone
```

### **Valid Lines:**
```
CustomLine, DefaultLine, DropCapitalLine, HeadingLine,
InterlinearLine, MusicLine
```

---

## 🐛 **Troubleshooting**

### **Chrome/Edge: Extension doesn't appear**
1. ✅ Developer Mode ON?
2. ✅ Path correct?
3. ✅ manifest.json exists in folder?
4. Solution: Reload (↻ button on Extensions page)

### **Chrome/Edge: "Cannot load extension"**
1. Check: manifest.json valid JSON?
2. Check: No syntax errors in content.js?
3. Solution: Re-download Release 1.1

### **Firefox: Popup doesn't appear**
1. ✅ about:debugging shows extension?
2. Solution: F12 → Console → Check for errors
3. Solution: Load Temporary again

### **Icon doesn't appear in toolbar**
1. ✅ Extension enabled (toggle blue)?
2. ✅ Browser fully reloaded?
3. Solution: Close browser completely, reopen
4. Solution: Right-click extension icon area → "Always show"

### **Popup appears but doesn't work**
1. Open DevTools (F12)
2. Check: Console tab for errors
3. Check: Network tab for API calls
4. Try: Hard refresh (Ctrl+Shift+R)

---

## ✅ **Installation Checklist**

### **Chrome:**
- [ ] chrome://extensions/ open
- [ ] Developer mode ON (blue)
- [ ] "Load unpacked" clicked
- [ ] segmonto-official/ folder selected
- [ ] Extension appears in list
- [ ] ✓ icon visible in toolbar
- [ ] Popup opens when clicked
- [ ] ✅ COMPLETE

### **Edge:**
- [ ] edge://extensions/ open
- [ ] Developer mode ON (blue)
- [ ] "Load unpacked" clicked
- [ ] segmonto-official/ folder selected
- [ ] Extension appears in list
- [ ] ✓ icon visible in toolbar
- [ ] Popup opens when clicked
- [ ] ✅ COMPLETE

### **Firefox:**
- [ ] about:debugging open
- [ ] "This Firefox" selected
- [ ] "Load Temporary Add-on..." clicked
- [ ] manifest.json selected
- [ ] Extension appears in list
- [ ] ✓ icon visible in toolbar
- [ ] Popup opens when clicked
- [ ] ✅ COMPLETE (temporary)

---

## 🎉 **Success Indicators**

✅ **Installation successful when:**
1. Extension icon (✓) visible in toolbar of each browser
2. Clicking icon opens popup window
3. Popup shows form with fields
4. Can run checks on eScriptorium documents

✅ **Everything working when:**
1. SegmOnto checks regions and lines
2. Results show percentage compliance
3. Error list appears for invalid types
4. CSV export works (if available)

---

## 📝 **Next Steps**

1. **In each browser:**
   - [ ] Click SegmOnto icon
   - [ ] Navigate to eScriptorium document
   - [ ] Run check
   - [ ] Verify results

2. **Report findings:**
   - [ ] Does popup appear?
   - [ ] Does check work?
   - [ ] Are results accurate?
   - [ ] Any console errors?

3. **Optional: Integration Test**
   - [ ] Compare extension results vs integrated panel
   - [ ] Both should show same data

---

**Status:** Ready to install! 🚀  
**Installation Time:** ~5 minutes per browser  
**Support:** All 3 browsers now compatible! ✅

---

## 🎯 **Quick Reference**

| Browser | Command | Time | Permanent |
|---------|---------|------|-----------|
| Chrome | Load Unpacked | 1 min | ✅ Yes |
| Edge | Load Unpacked | 1 min | ✅ Yes |
| Firefox | Load Temporary | 1 min | ⚠️ Per Session |

**Start with Chrome, then Edge, then Firefox!** 🚀
