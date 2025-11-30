#!/usr/bin/env python3
"""
סקריפט מתקדם ומשופר לחילוץ מחרוזות שצריכות תרגום
מייצר קובץ תבנית נוח לתרגום ללא מחרוזות טכניות מיותרות
"""

import os
import re
import sys
from pathlib import Path
from collections import defaultdict
from datetime import datetime

class SmartTranslationExtractor:
    def __init__(self, project_root):
        self.project_root = Path(project_root)
        
        # זיהוי הנתיבים הנכונים
        if str(self.project_root) == '/usr/src/app':
            # אנחנו בקונטיינר
            self.app_dir = self.project_root
            self.po_file = self.project_root / "locale" / "he" / "LC_MESSAGES" / "django.po"
        else:
            # אנחנו במחשב המארח
            self.app_dir = self.project_root / "app"
            self.po_file = self.app_dir / "locale" / "he" / "LC_MESSAGES" / "django.po"
        
        # מחרוזות שכבר תורגמו
        self.existing_translations = set()
        
        # מחרוזות חסרות
        self.missing_strings = []
        
        # דפוסים של מחרוזות שלא צריך לתרגם
        self.non_translatable_patterns = [
            # CSS Classes ו-IDs
            r'^[a-z-]+-[0-9]+$',  # my-1, mr-2
            r'^[a-z]+-[0-9]+ [a-z]+-[0-9]+$',  # my-1 mr-1
            r'^[a-z]+[A-Z][a-zA-Z]*$',  # camelCase IDs
            r'^id_[a-z_]+$',  # id_old_password, id_email
            r'^form-[a-z-]+$',  # form-check-label
            r'^nav-[a-z-]+$',  # nav-doc-tab
            r'^[a-z]+Modal[A-Za-z]*Label$',  # migrateModalLabel
            
            # פרמטרים טכניים ושמות קבצים
            r'^\{[^}]*\}$',  # {error}, {filename}, {count}
            r'^[a-z]+\.[a-z]+$',  # file.ext
            r'^[A-Z_][A-Z_0-9]*$',  # CONSTANTS
            r'^[a-z_]+_label$',  # report_label
            
            # HTML ו-Django templates
            r'^.*\{%.*%\}.*$',  # Django template tags
            r'^>.*</.*>$',  # HTML fragments
            r'^[<>].*$',  # HTML tags
            r'^.*</div>.*$',  # div fragments
            
            # מחרוזות מינימליות
            r'^[a-zA-Z]{1,2}$',  # תווים בודדים
            r'^\s*$',  # Empty strings
            r'^[^a-zA-Z]*$',  # רק סימנים או מספרים
            
            # טכניות שאין צורך לתרגם
            r'^Toggle [a-z]+$',  # Toggle navigation
            r'^Pagination$',  # (אלא אם רוצים לתרגם)
            r'^on[A-Z][a-zA-Z]*$',  # onClick, onSubmit
        ]
        
        # מילות מפתח שמעידות על מחרוזות טכניות
        self.non_translatable_keywords = [
            'css', 'class', 'id', 'style', 'href', 'src', 'onclick',
            'javascript', 'json', 'xml', 'html', 'url', 'uri',
            'modal', 'dropdown', 'navbar', 'container', 'wrapper'
        ]
        
        # דפוסי חיפוש למחרוזות
        self.search_patterns = [
            r"_\(['\"](.+?)['\"].*?\)",  # _("string")
            r"gettext\(['\"](.+?)['\"].*?\)",  # gettext("string")
            r"gettext_lazy\(['\"](.+?)['\"].*?\)",  # gettext_lazy("string")
            r"{%\s*trans\s+['\"](.+?)['\"].*?%}",  # {% trans "string" %}
            r"label\s*=\s*[_]*\(['\"](.+?)['\"].*?\)",  # label=_("string")
            r"help_text\s*=\s*[_]*\(['\"](.+?)['\"].*?\)",  # help_text
            r"verbose_name\s*=\s*[_]*\(['\"](.+?)['\"].*?\)",  # verbose_name
            r"messages\.\w+\([^,]+,\s*[_]*\(['\"](.+?)['\"].*?\)",  # messages
        ]

    def is_translatable(self, text):
        """בדיקה האם מחרוזת ניתנת לתרגום"""
        
        text = text.strip()
        
        # בדיקת אורך מינימלי
        if len(text) < 3:
            return False
        
        # בדיקת דפוסים
        for pattern in self.non_translatable_patterns:
            if re.match(pattern, text, re.IGNORECASE):
                return False
        
        # בדיקת מילות מפתח
        text_lower = text.lower()
        for keyword in self.non_translatable_keywords:
            if keyword in text_lower and len(text) < 50:  # רק במחרוזות קצרות
                return False
        
        # מחרוזות שמתחילות באותיות גדולות (כנראה כותרות/תוויות)
        # או מכילות רווחים (כנראה משפטים) - כנראה ניתנות לתרגום
        if text[0].isupper() or ' ' in text:
            return True
        
        # אחרת, בדיקה אם יש מספיק אותיות
        letter_count = sum(1 for c in text if c.isalpha())
        return letter_count >= 3

    def load_existing_translations(self):
        """טעינת התרגומים הקיימים"""
        
        print("🔍 טוען תרגומים קיימים...")
        
        if not self.po_file.exists():
            print(f"❌ קובץ .po לא נמצא: {self.po_file}")
            return
        
        try:
            with open(self.po_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # חילוץ כל ה-msgid שכבר יש להם תרגום
            msgid_pattern = r'msgid\s+"(.+?)"\s*\nmsgstr\s+"(.+?)"'
            matches = re.findall(msgid_pattern, content, re.MULTILINE | re.DOTALL)
            
            for msgid, msgstr in matches:
                # רק אם יש תרגום (msgstr לא ריק)
                if msgstr.strip():
                    self.existing_translations.add(msgid)
            
            print(f"✅ נטענו {len(self.existing_translations)} תרגומים קיימים")
            
        except Exception as e:
            print(f"❌ שגיאה בטעינת קובץ .po: {e}")

    def extract_from_file(self, file_path):
        """חילוץ מחרוזות מקובץ"""
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
        except Exception as e:
            return []

        found_strings = set()
        relative_path = str(file_path.relative_to(self.project_root))
        
        # חיפוש לפי כל הדפוסים
        for pattern in self.search_patterns:
            matches = re.findall(pattern, content, re.MULTILINE | re.DOTALL)
            for match in matches:
                if isinstance(match, tuple):
                    # אם יש כמה קבוצות, קח את הראשונה
                    text = match[0]
                else:
                    text = match
                
                # נקה את הטקסט
                text = text.strip()
                if not text:
                    continue
                
                # בדוק אם ניתן לתרגום ועדיין לא תורגם
                if (self.is_translatable(text) and 
                    text not in self.existing_translations and
                    text not in found_strings):
                    
                    found_strings.add(text)
                    self.missing_strings.append({
                        'text': text,
                        'file': relative_path,
                        'line': self.find_line_number(content, text)
                    })

        return len(found_strings)

    def find_line_number(self, content, text):
        """מציאת מספר השורה של הטקסט"""
        lines = content.split('\n')
        for i, line in enumerate(lines, 1):
            if text in line:
                return i
        return 0

    def scan_project(self):
        """סריקת כל הפרויקט"""
        
        print("🔍 סורק קבצים...")
        
        file_extensions = ['.py', '.html', '.js']
        total_files = 0
        total_strings = 0
        
        # סריקת תיקיית app
        for ext in file_extensions:
            pattern = f"**/*{ext}"
            files = list(self.app_dir.glob(pattern))
            
            for file_path in files:
                # דלג על קבצי מיגרציה וטסטים
                if ('/migrations/' in str(file_path) or 
                    '/tests/' in str(file_path) or
                    file_path.name.startswith('test_')):
                    continue
                
                count = self.extract_from_file(file_path)
                if count > 0:
                    total_files += 1
                    total_strings += count
        
        print(f"✅ נסרקו {total_files} קבצים")
        print(f"📊 נמצאו {len(self.missing_strings)} מחרוזות חסרות")

    def generate_clean_template(self, output_file):
        """יצירת תבנית נוחה לתרגום"""
        
        if not self.missing_strings:
            print("❌ לא נמצאו מחרוזות חסרות")
            return
        
        # מיון לפי קובץ ושורה
        self.missing_strings.sort(key=lambda x: (x['file'], x['line']))
        
        lines = []
        
        # כותרת
        lines.extend([
            "# תבנית תרגום נוחה - BiblIA eScriptorium",
            "# =====================================",
            f"# נוצר: {datetime.now().strftime('%d/%m/%Y %H:%M')}",
            f"# מחרוזות לתרגום: {len(self.missing_strings)}",
            "#",
            "# הוראות לתרגום:",
            "# 1. מלא את השדה msgstr=\"\" בתרגום עברי",
            "# 2. שמור על המרכאות והתווים המיוחדים",
            "# 3. אחרי השלמת התרגום, הרץ את merge_translations.py",
            "#",
            "# ==========================================",
            ""
        ])
        
        current_file = None
        counter = 1
        
        for item in self.missing_strings:
            # כותרת קובץ חדש
            if item['file'] != current_file:
                current_file = item['file']
                lines.extend([
                    "",
                    f"# קובץ: {current_file}",
                    "# " + "=" * (len(current_file) + 6),
                    ""
                ])
            
            # המחרוזת עצמה
            lines.extend([
                f"# #{counter} - שורה {item['line']}",
                f"msgid \"{item['text']}\"",
                "msgstr \"\"",
                ""
            ])
            
            counter += 1
        
        # כתיבה לקובץ
        try:
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write('\n'.join(lines))
            
            print(f"✅ תבנית התרגום נוצרה: {output_file}")
            print(f"📄 {len(self.missing_strings)} מחרוזות מוכנות לתרגום")
            print(f"📏 הקובץ מכיל {len(lines)} שורות")
            
        except Exception as e:
            print(f"❌ שגיאה ביצירת הקובץ: {e}")

def main():
    """פונקציה ראשית"""
    
    script_dir = Path(__file__).parent
    
    # זיהוי נתיב הפרויקט
    if str(script_dir).endswith('/usr/src/app/tools') or str(script_dir).endswith('\\usr\\src\\app\\tools'):
        project_root = script_dir.parent
    elif script_dir.name == 'tools':
        project_root = script_dir.parent
    else:
        project_root = script_dir
    
    output_file = project_root / "translation_template_ready.po"
    
    print("🚀 סקריפט חילוץ תרגומים משופר")
    print(f"📂 תיקיית פרויקט: {project_root}")
    print(f"📝 קובץ יעד: {output_file}")
    print()
    
    # הרצת החילוץ
    extractor = SmartTranslationExtractor(project_root)
    extractor.load_existing_translations()
    extractor.scan_project()
    extractor.generate_clean_template(output_file)

if __name__ == "__main__":
    main()