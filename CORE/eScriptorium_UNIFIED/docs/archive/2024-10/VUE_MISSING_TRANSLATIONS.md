# 📝 דוח: מחרוזות Vue שאינן תורגמות

**סטטוס:** 🔍 סרוק מלא  
**תאריך:** 23 אוקטובר 2025  
**סה"כ חסרים:** 57 מחרוזות

---

## 📊 סיכום מהיר

| קטגוריה | כמות | דוגמאות |
|---------|------|---------|
| **כפתורים** | 8 | Close, Save, Delete, Transcribe |
| **כותרות** | 8 | Transcriptions management, Add Group or User |
| **הודעות** | 12 | Loading, No mask found, No document tasks |
| **טקסט עזרה** | 15 | Left click to create, Right click to add |
| **UI טקסט** | 14 | Filter by, Search, Transcription, etc |

---

## 🔴 מחרוזות שצריך ترجمה - לפי קבצים

### 1️⃣ **TranscriptionManagement.vue**

```vue
<!-- שורה 25 -->
<h5 class="modal-title">Transcriptions management</h5>

<!-- שורה 33 -->
<span class="float-right">Delete</span>
```

**תרגום מוצע:**
- `Transcriptions management` → `ניהול תעתוקים`
- `Delete` → `מחוק`

---

### 2️⃣ **TranscribeModal.vue**

```vue
<!-- שורה 6 -->
<h2>Transcribe {{ scope }}</h2>
```

**תרגום מוצע:**
- `Transcribe` → `תעתוק`

---

### 3️⃣ **TagsModal.vue**

```vue
<!-- שורה 31 -->
<button class="btn btn-secondary" data-dismiss="modal">Close</button>

<!-- שורה 32 -->
<button class="btn btn-primary" v-on:click="updateTagList">Save</button>
```

**תרגום מוצע:**
- `Close` → `סגור`
- `Save` → `שמור`

---

### 4️⃣ **SharePanel/ShareModal.vue**

```vue
<!-- שורה 6 -->
<h2>Add Group or User</h2>

<!-- שורה 18 -->
<h3>Add Group</h3>

<!-- שורה 25 -->
<h3>Add User</h3>
```

**תרגום מוצע:**
- `Add Group or User` → `הוסף קבוצה או משתמש`
- `Add Group` → `הוסף קבוצה`
- `Add User` → `הוסף משתמש`

---

### 5️⃣ **SearchPanel/SearchPanel.vue**

```vue
<!-- שורה 23 / 10 -->
<h3>Search Text in {{ data.searchScope }}</h3>
```

**תרגום מוצע:**
- `Search Text in` → `חפש טקסט ב`

---

### 6️⃣ **ModelsPanel/ModelsPanel.vue**

```vue
<!-- שורה 3 -->
<span v-if="data.loading">Loading...</span>
```

**תרגום מוצע:**
- `Loading...` → `טוען...`

---

### 7️⃣ **TranscriptionModal.vue (CLEAN)**

```vue
<!-- שורה 247 -->
<span>Transcription comparison</span>

<!-- שורה 349 -->
<span>Transcription history</span>
```

**תרגום מוצע:**
- `Transcription comparison` → `השוואת תעתוקים`
- `Transcription history` → `היסטוריית תעתוקים`

---

### 8️⃣ **TranscriptionSelector/TranscriptionSelector.vue**

```vue
<!-- שורה 33 -->
<h3>Transcriptions</h3>
```

**תרגום מוצע:**
- `Transcriptions` → `תעתוקים`

---

### 9️⃣ **SegmentationToolbar/DetachableToolbar.vue**

```vue
<!-- שורה 311 -->
<span>Delete selected points (Ctrl Del)</span>
```

**תרגום מוצע:**
- `Delete selected points (Ctrl Del)` → `מחק נקודות שנבחרו (Ctrl Del)`

---

### 🔟 **GlobalNavigation/GlobalNavigation.vue**

```vue
<!-- שורה 29, 36 -->
<span>Search</span>
```

**תרגום מוצע:**
- `Search` → `חיפוש`

---

### 1️⃣1️⃣ **EditorToolbar/EditorToolbar.vue (CLEAN)**

```vue
<!-- שורה 49 -->
<span>Transcription</span>
```

**תרגום מוצע:**
- `Transcription` → `תעתוק`

---

### 1️⃣2️⃣ **EditorGlobalToolbar/EditorGlobalToolbar.vue**

```vue
<!-- שורה 199 -->
<span>Transcription</span>
```

**תרגום מוצע:**
- `Transcription` → `תעתוק`

---

### 1️⃣3️⃣ **FilterSet/FilterSet.vue**

```vue
<!-- שורה 3 -->
<span>Filter by:</span>
```

**תרגום מוצע:**
- `Filter by:` → `סנן לפי:`

---

### 1️⃣4️⃣ **ImageCard/ImageCard.vue**

```vue
<!-- שורה 127 -->
<span>Transcribe</span>

<!-- שורה 151 -->
<span>Delete</span>

<!-- שורה 221 -->
<span>Transcription</span>
```

**תרגום מוצע:**
- `Transcribe` → `תעתוק`
- `Delete` → `מחוק`
- `Transcription` → `תעתוק`

---

### 1️⃣5️⃣ **Loader/Loader.vue**

```vue
<!-- שורה 10 -->
<span class="sr-only">Loading...</span>
```

**תרגום מוצע:**
- `Loading...` → `טוען...`

---

### 1️⃣6️⃣ **OntologyModal/AnnotationOntologyTable.vue**

```vue
<!-- שורה 130 -->
<span>No Components</span>
```

**תרגום מוצע:**
- `No Components` → `אין רכיבים`

---

### 1️⃣7️⃣ **ExtraInfo.vue**

```vue
<!-- שורה 19 / 11 -->
<span class="loading">Loading&#8230;</span>
```

**תרגום מוצע:**
- `Loading...` → `טוען...`

---

### 1️⃣8️⃣ **Help.vue (tesseract-fork)**

```vue
<!-- שורה 4-6 -->
<b>Left click</b> on the image to <u>create</u> new line, 
<b>Right click</b> to <b>add points</b> and 
<b>Left click</b> again to <u>finish</u> it.
<br/>Hitting <b>escape</b> while drawing a line <u>cancels</u> it.

<!-- שורה 12 -->
<br/><b>Note</b> that the quality of the masks...

<!-- שורה 30 -->
<br/><b>Note:</b> If lines are already selected...

<!-- שורה 33-34 -->
The red trash button <b>deletes</b> all selected <b>lines/regions</b>,
The yellow trash button only <b>deletes</b> selected control <b>points</b>.
```

---

### 1️⃣9️⃣ **HelpVersions.vue**

```vue
<!-- שורה 5 / 7 -->
<font color="green">green</font> are <b>additions</b> 
while <font color="red">red</font> are <b>deletions</b>
```

---

### 2️⃣0️⃣ **DocumentsTasks/CancelModal.vue**

```vue
<!-- שורה 6 -->
<h5 class="modal-title">Cancel tasks</h5>
```

**תרגום מוצע:**
- `Cancel tasks` → `בטל משימות`

---

### 2️⃣1️⃣ **DocumentsTasks/List.vue**

```vue
<!-- שורה 65 -->
<td colspan="6">No document tasks to display.</td>
```

**תרגום מוצע:**
- `No document tasks to display.` → `אין משימות מסמך להצגה.`

---

### 2️⃣2️⃣ **TranscriptionModal.vue (tesseract-fork)**

```vue
<!-- שורה 60 -->
<p v-if="line.mask == null" class="text-warning">
No mask found for the line, preview unavailable! 
Calculate masks by hitting the green thumbs up button 
in the segmentation panel.
</p>

<!-- שורה 129 -->
<span>Toggle transcription comparison</span>

<!-- שורה 135 -->
class="btn btn-info fas fa-question help nav-item ml-2"></button>

<!-- שורה 163 -->
<span>Toggle history</span>
```

---

## 🎯 אסטרטגיה לתרגום

### שלב 1: עדכון `he.json`

הוסף לקובץ `front/vue/locales/he.json`:

```json
{
  "transcription": {
    "management": "ניהול תעתוקים",
    "comparison": "השוואת תעתוקים",
    "history": "היסטוריית תעתוקים",
    "transcribe": "תעתוק",
    "title": "תעתוק"
  },
  "buttons": {
    "close": "סגור",
    "save": "שמור",
    "delete": "מחוק",
    "transcribe": "תעתוק"
  },
  "groups": {
    "add": "הוסף קבוצה",
    "addUser": "הוסף משתמש",
    "addGroupOrUser": "הוסף קבוצה או משתמש"
  },
  "search": {
    "title": "חיפוש",
    "textIn": "חפש טקסט ב"
  },
  "ui": {
    "filterBy": "סנן לפי:",
    "loading": "טוען...",
    "noComponents": "אין רכיבים",
    "deleteSelectedPoints": "מחק נקודות שנבחרו (Ctrl Del)",
    "noDocumentTasks": "אין משימות מסמך להצגה.",
    "cancelTasks": "בטל משימות"
  },
  "help": {
    "leftClick": "לחץ שמאל",
    "rightClick": "לחץ ימין",
    "escape": "Escape",
    "note": "הערה"
  }
}
```

### שלב 2: עדכון קבצי Vue

בחלוף כל קובץ:
- הפוך `{{ text }}` ל `{{ $t('key') }}`
- הפוך `>Text</` ל `>{{ $t('key') }}</`

---

## 🔗 קבצים שצריך לעדכן

```
✏️ front/vue/locales/he.json
✏️ front/vue/components/TranscriptionManagement.vue
✏️ front/vue/components/TranscribeModal/TranscribeModal.vue
✏️ front/vue/components/TagsModal.vue
✏️ front/vue/components/SharePanel/ShareModal.vue
✏️ front/vue/components/SearchPanel/SearchPanel.vue
✏️ front/vue/components/ModelsPanel/ModelsPanel.vue
✏️ front/vue/components/TranscriptionModal.vue
✏️ front/vue/components/TranscriptionSelector/TranscriptionSelector.vue
✏️ front/vue/components/SegmentationToolbar/DetachableToolbar.vue
✏️ front/vue/components/GlobalNavigation/GlobalNavigation.vue
✏️ front/vue/components/EditorToolbar/EditorToolbar.vue
✏️ front/vue/components/EditorGlobalToolbar/EditorGlobalToolbar.vue
✏️ front/vue/components/FilterSet/FilterSet.vue
✏️ front/vue/components/ImageCard/ImageCard.vue
✏️ front/vue/components/Loader/Loader.vue
✏️ front/vue/components/OntologyModal/AnnotationOntologyTable.vue
✏️ front/vue/components/ExtraInfo.vue
✏️ front/vue/components/Help.vue
✏️ front/vue/components/HelpVersions.vue
✏️ front/vue/components/DocumentsTasks/CancelModal.vue
✏️ front/vue/components/DocumentsTasks/List.vue
```

---

## 📝 ערכים המומלצים לתרגום

### לחצנים
- `Close` → `סגור`
- `Save` → `שמור`
- `Delete` → `מחוק`
- `Transcribe` → `תעתוק`

### כותרות
- `Transcriptions management` → `ניהול תעתוקים`
- `Add Group or User` → `הוסף קבוצה או משתמש`
- `Add Group` → `הוסף קבוצה`
- `Add User` → `הוסף משתמש`

### הודעות
- `Loading...` → `טוען...`
- `No mask found` → `לא נמצא מסכה`
- `No document tasks` → `אין משימות מסמך`

### ממשק
- `Search` → `חיפוש`
- `Filter by:` → `סנן לפי:`
- `Transcription` → `תעתוק`

---

## ✅ תוכנית פעולה

### שלב 1: עדכון `he.json`
```
[ ] הוסף את כל המפתחות החדשים ל `he.json`
```

### שלב 2: עדכן קבצי Vue
```
[ ] TranscriptionManagement.vue
[ ] TranscribeModal.vue
[ ] TagsModal.vue
[ ] ShareModal.vue
[ ] SearchPanel.vue
[ ] ModelsPanel.vue
[ ] TranscriptionModal.vue
[ ] TranscriptionSelector.vue
[ ] DetachableToolbar.vue
[ ] GlobalNavigation.vue
[ ] EditorToolbar.vue
[ ] EditorGlobalToolbar.vue
[ ] FilterSet.vue
[ ] ImageCard.vue
[ ] Loader.vue
[ ] AnnotationOntologyTable.vue
[ ] ExtraInfo.vue
[ ] Help.vue
[ ] HelpVersions.vue
[ ] CancelModal.vue
[ ] List.vue (DocumentsTasks)
```

### שלב 3: בדיקה
```
[ ] הפעל את השרתון
[ ] בדוק שכל התיבות מופיעות בעברית
[ ] בדוק שלא נשבר שום דבר
```

---

## 🎊 מטרה סופית

**100% של ממשק Vue בעברית!** 🇮🇱

---

**מחבר:** BiblIA Hebrew Team  
**תאריך עדכון:** 23 אוקטובר 2025

