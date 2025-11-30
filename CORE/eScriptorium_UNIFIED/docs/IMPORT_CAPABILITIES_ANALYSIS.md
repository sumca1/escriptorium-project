# 📥 ניתוח יכולות ייבוא - eScriptorium
**תאריך:** 30 אוקטובר 2025

---

## 🎯 שאלות המשתמש

### 1️⃣ **ייבוא קבצי ABBYY FineReader**
> "האם התוספת הבאה תעזור לי?"  
> https://github.com/UB-Mannheim/ocr-fileformat/blob/main/script/transform/abbyy__page

### 2️⃣ **ייבוא מ-Transkribus**
> "האם כבר קיים אצלי?"  
> https://github.com/UB-Mannheim/eScriptorium_Dokumentation/blob/main/Modell%C3%BCbertragung_Transkribus_nach_eScriptorium.md  
> https://github.com/alix-tz/aspyre-gt?tab=readme-ov-file#configuring-the-export-from-transkribus

### 3️⃣ **חילוץ טקסט מ-PDF עם שכבת OCR**
> "האם כבר קיים אפשרות לחלץ טקסט מתחת לשכבת תמונה של PDF כדי לעשות השוואה?"

---

## 📊 סיכום מהיר

| פורמט | סטטוס | פרטים |
|-------|--------|--------|
| **ABBYY XML** | ⚠️ מבוטל | קוד קיים אבל מנוטרל |
| **Transkribus PAGE XML** | �? **תמיכה מלאה** | `TranskribusPageXmlParser` |
| **PDF �? טקסט** | �? **לא קיים** | רק PDF �? תמונות |
| **ALTO XML** | �? תמיכה מלאה | `AltoParser` |
| **PAGE XML** | �? תמיכה מלאה | `PagexmlParser` |
| **IIIF** | �? תמיכה מלאה | `IIIFManifestParser` |
| **METS** | �? תמיכה מלאה | `METSRemoteParser`, `METSZipParser` |

---

## 🔍 ניתוח מפורט

### 1️⃣ ייבוא ABBYY FineReader

#### �? **מה כבר קיים:**

**קובץ:** `app/apps/imports/parsers.py`

```python
# שורה 48:
XML_EXTENSIONS = ["xml", "alto"]  # , 'abbyy'  �? מנוטרל!

# שורה 1279-1280:
# if 'abbyy' in schema:  # Not super robust
#     return AbbyyParser(root, name=name)  �? הקוד קיים אבל מנוטרל!
```

**מסקנה:**
- 🟡 **התמיכה ב-ABBYY הייתה קיימת אבל הושבתה**
- הסיבה: "Not super robust" - לא מספיק חזק
- הקוד עדיין קיים בבסיס הנתונים (migrations):
  ```python
  # 0003_auto_20190409_0942.py:
  allowed_extensions=['xml', 'alto', 'abbyy']
  ```

#### 🔧 **מה צריך להוסיף:**

**אופציה A: להפעיל מחדש את AbbyyParser הישן**
```python
# ב-parsers.py שורה 48:
XML_EXTENSIONS = ["xml", "alto", "abbyy"]  # �? להסיר את ההערה

# שורה 1279-1280:
if 'abbyy' in schema:
    return AbbyyParser(root, name=name)  # �? להפעיל מחדש
```

**⚠️ אבל:** הקוד לא חזק, עלול להיכשל.

**אופציה B: להשתמש ב-UB-Mannheim ocr-fileformat (מומלץ!)**

הכלי: https://github.com/UB-Mannheim/ocr-fileformat/blob/main/script/transform/abbyy__page

**יתרונות:**
1. �? ממיר ABBYY XML �? PAGE XML (פורמט נתמך!)
2. �? נבדק ויציב
3. �? eScriptorium כבר תומך ב-PAGE XML

**תהליך עבודה מומלץ:**
```bash
# 1. המרה מ-ABBYY ל-PAGE XML:
python ocr-fileformat/transform/abbyy__page my_abbyy_file.xml > my_page_file.xml

# 2. ייבוא ל-eScriptorium:
# Import �? XML �? העלה my_page_file.xml
```

**חלופה - אינטגרציה אוטומטית:**
```python
# אפשר להוסיף ב-parsers.py:
from subprocess import run

def convert_abbyy_to_page(abbyy_file):
    """Convert ABBYY XML to PAGE XML using ocr-fileformat"""
    result = run(['python', 'ocr-fileformat/transform/abbyy__page', abbyy_file],
                 capture_output=True, text=True)
    return result.stdout

# ואז ב-make_parser():
if ext == "xml":
    root = etree.parse(file_handler).getroot()
    schema = root.nsmap[None]
    
    if 'abbyy' in schema.lower():
        # המר ל-PAGE XML
        page_xml = convert_abbyy_to_page(file_handler)
        root = etree.fromstring(page_xml)
        return PagexmlParser(document, file_handler, report, xml_root=root)
```

---

### 2️⃣ ייבוא מ-Transkribus

#### �? **כבר קיים ועובד מצוין!**

**קובץ:** `app/apps/imports/parsers.py` (שורה 1235)

```python
class TranskribusPageXmlParser(PagexmlParser):
    """
    A PAGE XML Parser for documents exported from Transkribus to handle data
    """
    
    def clean_coords(self, coordTag):
        """תיקון קואורדינטות שליליות (באג ידוע ב-Transkribus)"""
        try:
            return [
                list(map(lambda x: 0 if float(x) < 0 else float(x), pt.split(",")))
                for pt in coordTag.get("points").strip().split(" ")
            ]
        except (AttributeError, ValueError):
            raise ParseError("Invalid coordinates")
```

**איך זה עובד:**

```python
# ב-make_parser() שורה 1285:
if "PAGE" in schema:
    if b"Transkribus" in etree.tostring(root):  # �? זיהוי אוטומטי!
        return TranskribusPageXmlParser(document, file_handler, report, ...)
    else:
        return PagexmlParser(document, file_handler, report, ...)
```

**מה שהמערכת מטפלת בו:**
1. �? קואורדינטות שליליות (באג ב-Transkribus)
2. �? זיהוי אוטומטי של קבצי Transkribus
3. �? תמיכה מלאה ב-PAGE XML

**תהליך עבודה:**

```bash
# 1. ייצוא מ-Transkribus:
Transkribus �? Export �? PAGE XML (latest version)

# 2. ייבוא ל-eScriptorium:
Import �? XML / ZIP �? העלה את קובץ ה-PAGE XML (או ZIP עם מספר קבצים)

# 3. המערכת מזהה אוטומטית שזה מ-Transkribus ומפעילה TranskribusPageXmlParser!
```

**תמיכה גם ב-aspyre-gt:**

הכלי `aspyre-gt` (https://github.com/alix-tz/aspyre-gt) מיועד ליצירת Ground Truth מ-Transkribus.

**האם צריך אותו?** 
- 🟢 **לא בהכרח** - eScriptorium כבר תומך ב-PAGE XML מ-Transkribus
- 🟡 **אם צריך המרה מתקדמת** - aspyre-gt מציע אפשרויות נוספות
- 🟢 **אבל:** התמיכה המובנית ב-eScriptorium מספיקה למרבית המקרים

---

### 3️⃣ חילוץ טקסט מ-PDF עם שכבת OCR

#### �? **לא קיים כרגע**

**מה שכן קיים:**

**קובץ:** `app/apps/imports/parsers.py` (שורה 113)

```python
class PdfParser(ParserDocument):
    """ייבוא PDF כתמונות בלבד"""
    
    def parse(self, start_at=0, override=False, user=None):
        # קריאת PDF עם pyvips
        doc = pyvips.Image.pdfload_buffer(buff, n=-1, access='sequential')
        
        for page_nb in range(start_at, n_pages):
            # טעינת עמוד כתמונה (DPI 300)
            page = pyvips.Image.pdfload_buffer(buff, page=page_nb, dpi=300)
            
            # שמירה כתמונה PNG
            part.image.save(name, image_file, format="png")
```

**מה חסר:**
- �? אין חילוץ טקסט מ-PDF
- �? אין קריאת שכבת OCR מוטמעת ב-PDF
- �? אין השוואה בין OCR קיים ל-OCR חדש

**ספריות נפוצות לחילוץ טקסט מ-PDF:**
1. **pdfminer.six** - מומלץ (pure Python)
2. **PyPDF2 / pypdf** - פשוט אבל פחות חזק
3. **pdfplumber** - מתקדם, עם תמיכה בטבלאות
4. **PyMuPDF (fitz)** - מהיר, אבל תלות ב-C

---

## 🚀 המלצות יישום

### **תרחיש A: ייבוא מ-FineReader (ABBYY)**

#### שיטה 1: המרה חיצונית (מומלץ!)
```bash
# התקנה:
git clone https://github.com/UB-Mannheim/ocr-fileformat.git

# המרה:
python ocr-fileformat/script/transform/abbyy__page finereader_output.xml > page_format.xml

# ייבוא ל-eScriptorium:
# UI �? Import �? XML �? page_format.xml
```

**יתרונות:**
- �? לא צריך לשנות קוד eScriptorium
- �? שיטה יציבה ונבדקת
- �? ניתן לאוטמט ב-script

#### שיטה 2: אינטגרציה פנימית (מתקדם)

**צעדים:**
1. להתקין `ocr-fileformat` ב-Docker
2. להוסיף פונקציה `convert_abbyy_to_page()` ב-`parsers.py`
3. לשנות `make_parser()` כדי לזהות ABBYY ולהמיר אוטומטית

**קוד לדוגמה:**

```python
# ב-parsers.py:

import subprocess
from pathlib import Path

OCR_FILEFORMAT_PATH = Path("/opt/ocr-fileformat")  # נתיב להתקנה

def convert_abbyy_to_page_xml(abbyy_file_content):
    """
    Convert ABBYY XML to PAGE XML using ocr-fileformat.
    
    Args:
        abbyy_file_content: String content of ABBYY XML
    
    Returns:
        String content of PAGE XML
    """
    import tempfile
    
    # שמירה זמנית
    with tempfile.NamedTemporaryFile(mode='w', suffix='.xml', delete=False) as tmp:
        tmp.write(abbyy_file_content)
        tmp_path = tmp.name
    
    try:
        # המרה
        result = subprocess.run(
            ['python', str(OCR_FILEFORMAT_PATH / 'script/transform/abbyy__page'), tmp_path],
            capture_output=True,
            text=True,
            check=True
        )
        return result.stdout
    finally:
        # מחיקת קובץ זמני
        Path(tmp_path).unlink()

# שינוי ב-make_parser():
def make_parser(...):
    ext = os.path.splitext(file_handler.name)[1][1:]
    
    if ext in XML_EXTENSIONS:
        root = etree.parse(file_handler).getroot()
        schema = root.nsmap.get(None, '')
        
        # זיהוי ABBYY XML
        if 'abbyy' in schema.lower():
            logger.info(f"Detected ABBYY XML, converting to PAGE XML: {file_handler.name}")
            
            # קריאת תוכן
            file_handler.seek(0)
            abbyy_content = file_handler.read().decode('utf-8')
            
            # המרה ל-PAGE XML
            page_content = convert_abbyy_to_page_xml(abbyy_content)
            
            # טעינה מחדש
            root = etree.fromstring(page_content.encode('utf-8'))
            
            # שימוש ב-PagexmlParser
            return PagexmlParser(
                document, file_handler, report, 
                transcription_name=name, xml_root=root
            )
        
        # המשך קוד רגיל...
```

---

### **תרחיש B: חילוץ טקסט מ-PDF עם שכבת OCR**

#### יכולות מבוקשות:
1. 📖 חילוץ טקסט מוטמע ב-PDF (שכבת OCR)
2. 🆚 השוואה בין OCR מקורי (PDF) ל-OCR חדש (eScriptorium)
3. 📊 דוח הבדלים (diff report)

#### מימוש מוצע:

**שלב 1: הוספת ספריות**

`requirements.txt`:
```
pdfminer.six==20221105
pdfplumber==0.10.0  # אופציונלי - לתכונות מתקדמות
```

**שלב 2: פונקציה לחילוץ טקסט**

`app/apps/imports/pdf_text_extractor.py` (חדש):
```python
"""
PDF Text Extraction - חילוץ טקסט משכבת OCR ב-PDF
"""
import logging
from io import BytesIO
from typing import Dict, List, Optional

from pdfminer.high_level import extract_text_to_fp, extract_pages
from pdfminer.layout import LAParams, LTTextBox, LTTextLine, LTChar

logger = logging.getLogger(__name__)


class PDFTextExtractor:
    """חילוץ טקסט מ-PDF עם שכבת OCR"""
    
    def __init__(self, pdf_buffer):
        """
        Args:
            pdf_buffer: BytesIO or file-like object with PDF content
        """
        self.pdf_buffer = pdf_buffer
    
    def extract_full_text(self) -> str:
        """
        חילוץ טקסט מלא מכל העמודים.
        
        Returns:
            String with full text from all pages
        """
        output = BytesIO()
        try:
            extract_text_to_fp(self.pdf_buffer, output, laparams=LAParams())
            return output.getvalue().decode('utf-8')
        except Exception as e:
            logger.error(f"Failed to extract text from PDF: {e}")
            return ""
    
    def extract_page_text(self, page_num: int) -> str:
        """
        חילוץ טקסט מעמוד בודד.
        
        Args:
            page_num: Page number (0-indexed)
        
        Returns:
            String with text from the specified page
        """
        try:
            pages = list(extract_pages(self.pdf_buffer))
            if page_num < len(pages):
                page = pages[page_num]
                texts = []
                for element in page:
                    if isinstance(element, (LTTextBox, LTTextLine)):
                        texts.append(element.get_text())
                return ''.join(texts)
            return ""
        except Exception as e:
            logger.error(f"Failed to extract text from page {page_num}: {e}")
            return ""
    
    def extract_lines_with_positions(self, page_num: int) -> List[Dict]:
        """
        חילוץ שורות טקסט עם מיקומן בעמוד.
        
        Args:
            page_num: Page number (0-indexed)
        
        Returns:
            List of dicts: [{'text': '...', 'bbox': (x0, y0, x1, y1)}, ...]
        """
        try:
            pages = list(extract_pages(self.pdf_buffer))
            if page_num >= len(pages):
                return []
            
            page = pages[page_num]
            lines = []
            
            for element in page:
                if isinstance(element, LTTextLine):
                    lines.append({
                        'text': element.get_text().strip(),
                        'bbox': (element.x0, element.y0, element.x1, element.y1),
                        'height': element.height,
                        'width': element.width
                    })
            
            # מיון לפי y (מלמעלה למטה)
            lines.sort(key=lambda l: -l['bbox'][3])  # y1 descending
            
            return lines
        except Exception as e:
            logger.error(f"Failed to extract lines from page {page_num}: {e}")
            return []
    
    def has_text_layer(self) -> bool:
        """
        בדיקה האם ל-PDF יש שכבת טקסט.
        
        Returns:
            True if PDF has embedded text, False otherwise
        """
        text = self.extract_full_text()
        return len(text.strip()) > 0


class OCRComparison:
    """השוואה בין OCR מקורי (PDF) ל-OCR חדש (eScriptorium)"""
    
    def __init__(self, pdf_text: List[str], escriptorium_text: List[str]):
        """
        Args:
            pdf_text: List of lines from PDF OCR
            escriptorium_text: List of lines from eScriptorium OCR
        """
        self.pdf_text = pdf_text
        self.escriptorium_text = escriptorium_text
    
    def compute_character_error_rate(self) -> float:
        """
        חישוב CER (Character Error Rate) בין שני ה-OCR.
        
        Returns:
            CER as percentage (0-100)
        """
        from difflib import SequenceMatcher
        
        pdf_str = '\n'.join(self.pdf_text)
        escr_str = '\n'.join(self.escriptorium_text)
        
        matcher = SequenceMatcher(None, pdf_str, escr_str)
        similarity = matcher.ratio()
        
        return (1 - similarity) * 100
    
    def get_diff_report(self) -> Dict:
        """
        דוח הבדלים מפורט.
        
        Returns:
            Dict with comparison statistics
        """
        import difflib
        
        differ = difflib.Differ()
        diff = list(differ.compare(self.pdf_text, self.escriptorium_text))
        
        added = [line[2:] for line in diff if line.startswith('+ ')]
        removed = [line[2:] for line in diff if line.startswith('- ')]
        unchanged = [line[2:] for line in diff if line.startswith('  ')]
        
        return {
            'total_lines_pdf': len(self.pdf_text),
            'total_lines_escriptorium': len(self.escriptorium_text),
            'lines_added': len(added),
            'lines_removed': len(removed),
            'lines_unchanged': len(unchanged),
            'cer': self.comxxxxxxxxxacter_error_rate(),
            'added_lines': added,
            'removed_lines': removed
        }
```

**שלב 3: שינוי PdfParser לחילוץ טקסט**

`app/apps/imports/parsers.py`:
```python
from imports.pdf_text_extractor import PDFTextExtractor, OCRComparison

class PdfParser(ParserDocument):
    """Enhanced PDF parser with OCR text extraction"""
    
    def __init__(self, document, file_handler, report, extract_text=False):
        super().__init__(document, file_handler, report)
        self.extract_text = extract_text  # האם לחלץ טקסט מוטמע
        self.text_extractor = None
        pyvips.voperation.cache_set_max(10)
    
    def validate(self):
        try:
            self.doc = pyvips.Image.pdfload_buffer(self.file.read(), n=-1, access='sequential')
            
            # בדיקת שכבת טקסט
            if self.extract_text:
                self.file.seek(0)
                self.text_extractor = PDFTextExtractor(BytesIO(self.file.read()))
                
                if self.text_extractor.has_text_layer():
                    logger.info(f"PDF has embedded text layer: {self.file.name}")
                    self.report.append(_("PDF contains embedded OCR text"))
                else:
                    logger.info(f"PDF has no text layer: {self.file.name}")
                    self.report.append(_("PDF has no embedded text (image-only PDF)"))
                    
        except pyvips.error.Error as e:
            logger.exception(e)
            raise ParseError(_("Invalid PDF file."))
    
    def parse(self, start_at=0, override=False, user=None):
        # ... קוד קיים ...
        
        for page_nb in range(start_at, n_pages):
            # ... יצירת DocumentPart ...
            
            # חילוץ טקסט מוטמע אם קיים
            if self.extract_text and self.text_extractor:
                extracted_text = self.text_extractor.extract_page_text(page_nb)
                
                if extracted_text.strip():
                    # שמירה כ-transcription "PDF OCR"
                    pdf_transcription, _ = Transcription.objects.get_or_create(
                        document=self.document,
                        name="PDF OCR (Original)"
                    )
                    
                    # יצירת LineTranscription לכל שורה
                    lines_with_positions = self.text_extractor.extract_lines_with_positions(page_nb)
                    
                    for idx, line_data in enumerate(lines_with_positions):
                        # TODO: צריך Line objects - נדרש segmentation
                        # אפשר ליצור dummy lines או לדרוש segmentation מראש
                        pass
            
            # ... המשך קוד רגיל ...
            yield part
```

**שלב 4: הוספת אופציה ב-UI**

`front/vue/components/ImportModal/ImportPDFForm.vue`:
```vue
<template>
    <div>
        <input type="file" @change="handleFileChange" accept=".pdf" />
        
        <!-- אופציה חדשה: חילוץ טקסט -->
        <div class="form-check">
            <input 
                type="checkbox" 
                id="extractText" 
                v-model="extractTextLayer"
                class="form-check-input"
            />
            <label for="extractText" class="form-check-label">
                Extract embedded OCR text from PDF
                <small class="text-muted">
                    (If PDF contains text layer, import it as "PDF OCR (Original)" transcription)
                </small>
            </label>
        </div>
    </div>
</template>

<script>
export default {
    data() {
        return {
            extractTextLayer: false
        }
    },
    methods: {
        handleFileChange(event) {
            // ... קוד קיים ...
            
            // שמירת אופציה ב-store
            this.$store.dispatch('forms/handleGenericInput', {
                form: 'import',
                field: 'extractText',
                value: this.extractTextLayer
            })
        }
    }
}
</script>
```

**שלב 5: תרחיש שימוש מלא**

```python
# views.py או tasks.py:

from imports.pdf_text_extractor import PDFTextExtractor, OCRComparison

def compare_pdf_ocr_with_escriptorium(document, pdf_file):
    """
    השוואה בין OCR מקורי ב-PDF ל-OCR שנוצר ב-eScriptorium.
    
    Returns:
        Dict with comparison report
    """
    # חילוץ טקסט מ-PDF
    extractor = PDFTextExtractor(pdf_file)
    pdf_texts = []
    for page_num in range(document.parts.count()):
        page_text = extractor.extract_page_text(page_num)
        pdf_texts.extend(page_text.split('\n'))
    
    # קבלת OCR מ-eScriptorium
    transcription = document.transcriptions.get(name="manual")  # או כל שם אחר
    escr_texts = [
        lt.content 
        for lt in transcription.linetranscription_set.all()
    ]
    
    # השוואה
    comparison = OCRComparison(pdf_texts, escr_texts)
    report = comparison.get_diff_report()
    
    return report
```

---

## 📋 סיכום והמלצות

### �? **מה שכבר עובד מצוין:**

1. **Transkribus PAGE XML** ✅
   - תמיכה מלאה עם `TranskribusPageXmlParser`
   - זיהוי אוטומטי
   - תיקון באגים ידועים (קואורדינטות שליליות)

2. **ALTO XML** �?
   - תמיכה מלאה ב-פורמט ALTO

3. **PAGE XML כללי** ✅
   - תמיכה מלאה

4. **IIIF, METS** ✅
   - תמיכה מלאה

### ⚠️ **מה שצריך להוסיף:**

1. **ABBYY FineReader** (2 אפשרויות):
   - **מומלץ:** המרה חיצונית עם `ocr-fileformat` �? PAGE XML
   - **אופציה 2:** אינטגרציה פנימית (דורש פיתוח)

2. **חילוץ טקסט מ-PDF**:
   - **צריך:** הוספת `pdfminer.six`
   - **צריך:** פיתוח `PDFTextExtractor`
   - **צריך:** שינוי `PdfParser`
   - **צריך:** הוספת UI checkbox
   - **זמן פיתוח משוער:** 4-6 שעות

### 🎯 **המלצה לעדיפויות:**

#### עדיפות 1: **Transkribus** (כבר קיים! �?)
```
אין צורך בפעולה - המערכת כבר תומכת!
```

#### עדיפות 2: **ABBYY FineReader** (המרה חיצונית - 30 דק')
```bash
# התקנה:
git clone https://github.com/UB-Mannheim/ocr-fileformat.git
cd ocr-fileformat

# שימוש:
python script/transform/abbyy__page finereader.xml > page.xml
# ייבוא page.xml ל-eScriptorium
```

#### עדיפות 3: **חילוץ טקסט מ-PDF** (פיתוח - 4-6 שעות)
```
1. הוסף pdfminer.six ל-requirements.txt
2. צור PDFTextExtractor (הקוד למעלה)
3. שנה PdfParser
4. הוסף checkbox ב-UI
5. בדיקות
```

---

## 🔗 קישורים רלוונטיים

### כלים חיצוניים:
- **ocr-fileformat**: https://github.com/UB-Mannheim/ocr-fileformat
- **aspyre-gt**: https://github.com/alix-tz/aspyre-gt
- **Transkribus Documentation**: https://github.com/UB-Mannheim/eScriptorium_Dokumentation

### ספריות Python:
- **pdfminer.six**: https://github.com/pdfminer/pdfminer.six
- **pdfplumber**: https://github.com/jsvine/pdfplumber

### קבצים רלוונטיים בפרויקט:
- `app/apps/imports/parsers.py` - כל ה-parsers
- `front/vue/components/ImportModal/` - UI לייבוא

---

**נוצר:** 30 אוקטובר 2025  
**מחבר:** GitHub Copilot  
**גרסה:** 1.0
