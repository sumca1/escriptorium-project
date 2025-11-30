# 📊 eScriptorium Translation Flow - Visual Diagrams

**תאריך:** 20 אוקטובר 2025  
**מטרה:** דיאגרמות חזותיות המסבירות את זרימת התרגום

---

## 🎯 Diagram 1: Complete Data Flow (What SHOULD Work)

```
┌────────────────────────────────────────────────────────────────────────────────┐
│                        INTENDED TRANSLATION ARCHITECTURE                       │
│                      (Backend Complete, Frontend Incomplete)                   │
└────────────────────────────────────────────────────────────────────────────────┘

USER VISITS SITE
    │
    ↓
┌─────────────────────┐
│  Browser Request    │  GET /en/documents/  or  GET /fr/documents/
│  (with language)    │  Accept-Language: fr-FR, en-US
└─────────┬───────────┘
          │
          ↓
┌─────────────────────┐
│ LocaleMiddleware    │  ✅ Django detects language → sets LANGUAGE_CODE = 'fr'
│   (Django)          │  ✅ Thread-local storage: get_language() → 'fr'
└─────────┬───────────┘
          │
          ↓
┌─────────────────────┐
│  Django Templates   │  ✅ {% trans "Save" %} → "Enregistrer"
│    (UI Strings)     │  ✅ Works perfectly for static text
└─────────┬───────────┘
          │
          ↓
┌─────────────────────┐
│   Render HTML       │  ✅ <html lang="fr">
│  + Load Vue App     │  ❌ NO window.LANGUAGE_CODE set
└─────────┬───────────┘
          │
          ↓
┌─────────────────────┐
│  Vue.js Boots Up    │  ❌ NO language context
│                     │  ❌ NO vue-i18n installed
└─────────┬───────────┘
          │
          ↓
┌─────────────────────┐
│  fetchScripts()     │  ✅ AJAX call: GET /api/scripts/
│  (Vuex Action)      │
└─────────┬───────────┘
          │
          ↓
┌─────────────────────┐
│  ScriptViewSet      │  ✅ Django REST Framework endpoint
│  (API Backend)      │  ✅ Permission check → Allow
└─────────┬───────────┘
          │
          ↓
┌─────────────────────┐
│ ScriptSerializer    │  ✅ fields = '__all__'
│  (DRF Serializer)   │  ✅ Returns: { id, name, name_fr, iso_code, ... }
└─────────┬───────────┘
          │
          ↓
┌─────────────────────┐
│  Database Query     │  ✅ SELECT id, name, name_fr FROM core_script
│  (PostgreSQL)       │  ✅ Returns 208 scripts with French names
└─────────┬───────────┘
          │
          ↓
┌─────────────────────┐
│   JSON Response     │  ✅ { "results": [
│  (API → Frontend)   │       { "id": 3, 
└─────────┬───────────┘         "name": "Arabic",
          │                     "name_fr": "Arabe",  ← 🔥 French translation!
          ↓                     "iso_code": "Arab" }
┌─────────────────────┐     ]}
│  Vuex Mutation      │  ✅ state.scripts = data.results
│ setScripts(results) │  ✅ Stores complete objects with name_fr
└─────────┬───────────┘
          │
          ↓
┌─────────────────────┐
│  Vue Component      │  ✅ Receives: props.scripts = [{ name, name_fr }]
│ (EditDocumentModal) │  ❌ PROBLEM: Only uses script.name
└─────────┬───────────┘  ❌ IGNORES: script.name_fr
          │
          ↓
┌─────────────────────┐
│  scriptOptions()    │  ❌ return scripts.map(s => ({
│ (Computed Property) │        value: s.name,    ← Always English!
└─────────┬───────────┘        label: s.name }))
          │
          ↓
┌─────────────────────┐
│   <select>          │  ❌ Displays: "Arabic", "Armenian", "Balinese"
│  (HTML Dropdown)    │  ❌ SHOULD: "Arabe", "Arménien", "Balinais"
└─────────────────────┘

RESULT: API sends French translations, but Vue doesn't use them!
```

---

## 🔴 Diagram 2: What's MISSING?

```
┌────────────────────────────────────────────────────────────────────────────────┐
│                          ✅ COMPLETED IMPLEMENTATION                           │
│                          (October 24, 2024)                                    │
└────────────────────────────────────────────────────────────────────────────────┘

WHAT WAS IMPLEMENTED:

1️⃣ Vue i18n for UI Strings (TYPE 3 & 4)
   ──────────────────────────────────────
   
   COMPLETED:
   • TYPE 3: Template translations with {{ $t() }} - 467 usages
   • TYPE 4: JavaScript translations with this.$t() - 44 usages
   
   Example:
   Template:
   <button>{{ $t('Cancel') }}</button>
   
   JavaScript:
   computed: {
       tabOptions() {
           return [
               { label: this.$t("Region Types"), value: "regions" },
               { label: this.$t("Line Types"), value: "lines" }
           ]
       }
   }

2️⃣ Detection & Automation Tools
   ─────────────────────────────
   
   COMPLETED:
   • check_translation_status.py - Scans both templates AND JavaScript
   • fix_type4_javascript_translations.py - Automated TYPE 4 fixes
   • quick_auth_test.py - Quality verification (88% UI Hebrew achieved)

3️⃣ Database-Level Translations (TYPE 2)
   ─────────────────────────────────────
   
   STILL VALID - Original eScriptorium approach:
   
   models.py:
   def get_localized_name(self):
       lang = get_language()
       if lang == 'fr' and self.name_fr:
           return self.name_fr
       return self.name
   
   Then in API:
   - Send ONLY get_localized_name() instead of all fields
   - Frontend doesn't need to know about name_fr
```

---

## ✅ Diagram 3: How BiblIA Fixed It

```
┌────────────────────────────────────────────────────────────────────────────────┐
│                        BiblIA HEBREW TRANSLATION SOLUTION                      │
│                      (Hybrid: Server + Client Translation)                     │
└────────────────────────────────────────────────────────────────────────────────┘

PART A: Database Content (Server-Side)
───────────────────────────────────────

USER (Hebrew) → LocaleMiddleware → LANGUAGE_CODE = 'he'
                                         │
                                         ↓
                              Model: script.get_localized_name()
                                         │
                                         ↓
                              If lang == 'he' and name_he:
                                  return name_he  ✅
                              Else:
                                  return name
                                         │
                                         ↓
                              Template: {{ script.get_localized_name }}
                                         │
                                         ↓
                              Displays: "ערבית" (not "Arabic")


PART B: Vue UI Strings (Client-Side)
────────────────────────────────────

Django Template Renders:
    <script src="{% static 'js/editor_translations_he.js' %}"></script>
                                         │
                                         ↓
                         window.EDITOR_TRANSLATIONS = {
                             'Scripts': 'תסריטים',
                             'Main script': 'תסריט ראשי',
                             'Document name': 'שם המסמך',
                         }
                                         │
                                         ↓
                         Vue Component Methods:
                         $t(key) {
                             return window.EDITOR_TRANSLATIONS[key] || key;
                         }
                                         │
                                         ↓
                         Template:
                         <label>{{ $t('Main script') }}</label>
                                         │
                                         ↓
                         Displays: "תסריט ראשי"


RESULT: ✅ Complete Hebrew interface
        ✅ No vue-i18n needed
        ✅ Uses Django's existing language detection
```

---

## 📊 Diagram 4: Field-by-Field Comparison

```
┌────────────────────────────────────────────────────────────────────────────────┐
│                    WHERE EACH TRANSLATION TYPE LIVES                           │
└────────────────────────────────────────────────────────────────────────────────┘

TYPE 1: Static UI Strings (Django Templates)
────────────────────────────────────────────
    Location: Django Templates (.html)
    Method: {% trans "text" %}
    Storage: app/locale/fr/LC_MESSAGES/django.po
    Status: ✅ WORKS in eScriptorium
    
    Example:
        English: {% trans "Save Document" %}
        French:  "Enregistrer le document"


TYPE 2: Database Content (Dynamic)
──────────────────────────────────
    Location: Database (PostgreSQL)
    Method: Model fields (name_fr)
    Storage: core_script table
    Status: ⚠️ PARTIAL in eScriptorium
    
    Example:
        English: script.name = "Arabic"
        French:  script.name_fr = "Arabe"
        Used:    ❌ NO - only script.name displayed


TYPE 3: Vue Component Strings
─────────────────────────────
    Location: Vue .vue files
    Method: window.EDITOR_TRANSLATIONS + $t()
    Storage: Static JS files
    Status: ❌ NOT IN eScriptorium
            ✅ ADDED by BiblIA
    
    Example (BiblIA):
        window.EDITOR_TRANSLATIONS['Scripts'] = 'תסריטים'
        Template: {{ $t('Scripts') }}
        Displays: "תסריטים"


TYPE 4: JavaScript Computed Properties
──────────────────────────────────────
    Location: Vue computed properties / data objects
    Method: Wrap hardcoded strings with this.$t()
    Storage: Vue i18n translation files (he.json, fr.json)
    Status: ✅ IMPLEMENTED (October 24, 2024)
            44 strings fixed across 11 files
    
    Example (IMPLEMENTED):
        computed: {
            tabOptions() {
                return [
                    { label: this.$t("Region Types"), value: "regions" },
                    { label: this.$t("Line Types"), value: "lines" },
                    { label: this.$t("Part Types"), value: "parts" }
                ]
            }
        }
    
    Files Modified:
    • OntologyModal.vue (6 strings)
    • AnnotationOntologyTable.vue (7 strings)
    • SegmentModal.vue (8 strings)
    • TagFilter.vue (9 strings)
    • +7 additional files (14 strings)
```

---

## 🔀 Diagram 5: Decision Tree - Which Translation Method?

```
                    Need to translate something?
                               │
                               ↓
                    ┌──────────────────────┐
                    │  What type of text?  │
                    └──────────┬───────────┘
                               │
            ┌──────────────────┼──────────────────┐
            │                  │                  │
            ↓                  ↓                  ↓
    ┌──────────────┐  ┌──────────────┐  ┌──────────────┐
    │ Static UI    │  │ DB Content   │  │ Vue Component│
    │ Text         │  │ (Script name)│  │ Labels       │
    └──────┬───────┘  └──────┬───────┘  └──────┬───────┘
           │                 │                  │
           ↓                 ↓                  ↓
    Use Django i18n   Use get_localized    Use window.
    {% trans %}       _name() method       EDITOR_TRANSLATIONS
           │                 │                  │
           ↓                 ↓                  ↓
    ✅ eScriptorium   ⚠️ eScriptorium      ❌ eScriptorium
       has this!         PARTIAL              missing this!
                         (field exists,    ✅ BiblIA added
                         method missing)


RECOMMENDATION FOR NEW TRANSLATIONS:
────────────────────────────────────

1. Static buttons/labels     → {% trans "text" %} in django.po
2. Database field names       → Add name_XX field + get_localized_name()
3. Vue.js UI labels          → window.EDITOR_TRANSLATIONS
4. Vue.js dynamic content    → Use get_localized_name() in API response
```

---

## 🎓 Diagram 6: Learning from eScriptorium's Mistakes

```
┌────────────────────────────────────────────────────────────────────────────────┐
│                      WHY THE FRENCH TRANSLATION FAILED                         │
└────────────────────────────────────────────────────────────────────────────────┘

MISTAKE 1: No Frontend i18n Library
───────────────────────────────────
    Problem: Created name_fr field but no way for Vue to use it
    Solution: Install vue-i18n OR use server-side selection
    BiblIA: Chose server-side with get_localized_name()


MISTAKE 2: No Language Context in Vue
─────────────────────────────────────
    Problem: Vue doesn't know user's language
    Options:
        a) window.LANGUAGE_CODE = '{{ LANGUAGE_CODE }}'  ← Django → JS
        b) vue-i18n with locale detection
        c) Server-side: return already-translated data
    BiblIA: Used option (c) - server sends correct language


MISTAKE 3: Incomplete Migration Path
────────────────────────────────────
    Problem: Did Phase 1-3, never did Phase 4-5
    
    Phase 1: ✅ Add name_fr to model
    Phase 2: ✅ Populate 208 scripts
    Phase 3: ✅ Send via API
    Phase 4: ❌ Install vue-i18n (never done)
    Phase 5: ❌ Update components (never done)
    
    BiblIA: Skipped Phases 4-5, did different approach


MISTAKE 4: No Utility Method
────────────────────────────
    Problem: No get_localized_name() method
    eScriptorium:
        {{ script.name }}  ← Always English
    
    BiblIA:
        {{ script.get_localized_name }}  ← Language-aware
        
    Why it matters:
        - With method: ONE line in template, Django handles language
        - Without method: Vue must detect language + choose field


LESSON LEARNED:
──────────────
    If adding translation fields to DB:
        1. Add get_localized_name() method IMMEDIATELY
        2. OR commit to full vue-i18n implementation
        3. Don't create fields without consumption plan!
```

---

## 🚀 Diagram 7: Implementation Roadmap (If Fixing eScriptorium)

```
┌────────────────────────────────────────────────────────────────────────────────┐
│              HOW TO COMPLETE eScriptorium'S FRENCH TRANSLATION                 │
└────────────────────────────────────────────────────────────────────────────────┘

OPTION A: Client-Side Solution (vue-i18n)
─────────────────────────────────────────

Step 1: Install vue-i18n
    $ npm install vue-i18n@8  # Vue 2.x compatible

Step 2: Initialize in main.js
    import VueI18n from 'vue-i18n';
    const i18n = new VueI18n({
        locale: window.LANGUAGE_CODE || 'en',
    });

Step 3: Update components
    computed: {
        scriptOptions() {
            return this.scripts.map(script => ({
                value: script.name,
                label: this.getLocalizedField(script, 'name'),
            }));
        },
    },
    methods: {
        getLocalizedField(obj, field) {
            const locale = this.$i18n.locale;
            return obj[`${field}_${locale}`] || obj[field];
        },
    }

Effort: 🔴🔴🔴 High (new dependency, architectural change)


OPTION B: Server-Side Solution (BiblIA's Way)
─────────────────────────────────────────────

Step 1: Add method to models.py
    def get_localized_name(self):
        from django.utils.translation import get_language
        lang = get_language()
        return getattr(self, f'name_{lang}', None) or self.name

Step 2: Update serializer to use it
    class ScriptSerializer(serializers.ModelSerializer):
        localized_name = serializers.SerializerMethodField()
        
        def get_localized_name(self, obj):
            return obj.get_localized_name()
        
        class Meta:
            model = Script
            fields = ['id', 'localized_name', 'iso_code', ...]

Step 3: Update Vue to use localized_name
    scriptOptions() {
        return this.scripts.map(script => ({
            value: script.name,
            label: script.localized_name,  // ← Already translated!
        }));
    }

Effort: 🟡 Medium (backend-only change)


OPTION C: Hybrid (Recommended)
──────────────────────────────

Django i18n:     For UI strings (already works)
get_localized:   For DB content (add method)
window.EDITOR:   For Vue labels (BiblIA's addition)

Result: Complete translation with minimal dependencies

Effort: 🟢 Low (extends existing patterns)
```

---

## 📈 Summary Matrix

| Feature | eScriptorium | BiblIA | Ideal Solution |
|---------|-------------|--------|----------------|
| **UI Strings (Django)** | ✅ Working | ✅ Working | ✅ django.po |
| **DB Fields** | ⚠️ Created, not used | ✅ get_localized_name() | ✅ Method pattern |
| **Vue UI Labels** | ❌ Missing | ✅ window.EDITOR_TRANSLATIONS | ✅ Simple + works |
| **API Translation** | ❌ Sends all, no selection | ✅ Server-side selection | ✅ Localized at source |
| **Dependencies** | None (incomplete) | None (simple) | Minimal (no vue-i18n) |
| **Maintenance** | Easy (standard Django) | Easy (same pattern) | Easy |

---

**מסקנה**: eScriptorium יצר תשתית מצוינת אבל לא השלים. BiblIA מצא דרך פשוטה וממוקדת שעובדת בלי להוסיף dependencies.
