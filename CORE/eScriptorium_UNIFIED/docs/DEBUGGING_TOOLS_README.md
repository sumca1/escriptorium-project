# 🐛 כלי דיבאג ל-Supervisor MCP Server

**שני כלים עוצמתיים לדיבאג של MCP Servers**

---

## 🎯 סקירה מהירה

יש לך שני כלי דיבאג מתקדמים:

1. **Anthropic MCP Inspector** - ממשק ויזואלי בדפדפן
2. **MCP-Analyzer** - קריאה וניתוח של logs

---

## 🔍 Anthropic MCP Inspector

### מה זה?
ממשק ויזואלי שמאפשר לך:
- ✅ לראות רשימת כלים
- ✅ לבדוק כלים אינטראקטיבית
- ✅ לראות requests/responses
- ✅ לדבג בזמן אמת

### התקנה והרצה

#### אופציה 1: NPM Script (מומלץ!)
```bash
npm install
npm run debug
```

פתח דפדפן ב: **http://127.0.0.1:6274**

#### אופציה 2: NPX ישיר
```bash
npx @modelcontextprotocol/inspector node mcp-inspector-wrapper.js
```

### שימוש
1. פתח http://127.0.0.1:6274
2. לחץ **Connect**
3. לחץ **List Tools**
4. בחר כלי (למשל `get_project_status`)
5. לחץ **Execute**
6. ראה תוצאות!

---

## 📊 MCP-Analyzer

### מה זה?
שרת MCP שקורא ומנתח logs:
- 🔍 חיפוש בקבצי log
- 📄 פילטור לפי טקסט
- 📑 Pagination
- 🌐 עובד עם Claude/Copilot

### התקנה

```bash
npx -y @smithery/cli install @klara-research/MCP-Analyzer --client claude
```

### הגדרה ב-VS Code

ערוך `.vscode/mcp-servers.json`:

```json
{
  "mcpServers": {
    "supervisor": { /* ... existing ... */ },
    "log-reader": {
      "command": "node",
      "args": ["C:/path/to/MCP-Analyzer/build"]
    }
  }
}
```

### שימוש
```
@log-reader תציג logs אחרונים
@log-reader חפש עם filter="error"
```

---

## 📝 Logs שלנו

### איפה הם?

```
G:\OCR_Arabic_Testing\BiblIA_dataset-project\BiblIA_dataset\eScriptorium_CLEAN\
├── mcp_supervisor_debug.log      ← Wrapper logs
├── mcp_requests.log               ← Request/Response trace
├── mcp_errors.log                 ← Errors only
└── mcp_inspector_wrapper.log      ← Inspector wrapper logs
```

### צפייה ב-logs

```powershell
# 20 שורות אחרונות
npm run logs:tail

# כל ה-log
npm run logs

# או ישירות
cat mcp_supervisor_debug.log
```

---

## 🧪 בדיקה מהירה

```bash
# בדיקה אוטומטית
npm test
# או
python test_supervisor_local.py
```

---

## 🧹 ניקוי

```bash
# מחק logs
npm run clean:logs

# מחק Python cache
npm run clean:cache
```

---

## 📚 מידע נוסף

קרא: **[SUPERVISOR_MCP_DEBUGGING_GUIDE.md](SUPERVISOR_MCP_DEBUGGING_GUIDE.md)**

---

**עודכן:** 30 אוקטובר 2025
