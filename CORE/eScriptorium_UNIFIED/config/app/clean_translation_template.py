#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
סקריפט לניקוי וארגון קובץ תבנית התרגום
מסיר מחרוזות שאינן ניתנות לתרגום ומארגן את הקובץ לעבודה נוחה
"""

import re
import os
from datetime import datetime

# דפוסים של מחרוזות שלא צריך לתרגם
NON_TRANSLATABLE_PATTERNS = [
    # CSS Classes ו-IDs
    r'^[a-z-]+-[0-9]+$',  # my-1, mr-2
    r'^[a-z]+[A-Z][a-zA-Z]*$',  # camelCase IDs
    r'^id_[a-z_]+$',  # id_old_password
    r'^form-[a-z-]+$',  # form-check-label
    r'^[a-z]+Modal[A-Za-z]*$',  # migrateModalLabel
    
    # פרמטרים טכניים
    r'^\{[^}]*\}$',  # {error}, {filename}
    r'^[a-z]+\.[a-z]+$',  # file.ext
    r'^[A-Z_][A-Z_0-9]*$',  # CONSTANTS
    
    # מחרוزות חלקיות או פגומות
    r'^>.*</.*>$',  # HTML fragments
    r'^.*\{%.*%\}.*$',  # Django template tags
    r'^[<>].*$',  # HTML tags
    r'^\s*$',  # Empty strings
    
    # כתובות וקישורים
    r'^https?://.*$',
    r'^www\..*$',
    r'^.*\.com.*$',
    r'^.*\.org.*$',
]

# מילות מפתח שמעידות על מחרוזות שאין לתרגם
NON_TRANSLATABLE_KEYWORDS = [
    'css', 'class', 'id', 'style', 'href', 'src', 'onclick',
    'javascript', 'json', 'xml', 'html', 'url', 'uri',
    'modal', 'dropdown', 'navbar', 'container', 'wrapper'
]

def is_translatable(msgid):
    """בדיקה האם מחרוזת ניתנת לתרגום"""
    # בדיקת דפוסים
    for pattern in NON_TRANSLATABLE_PATTERNS:
        if re.match(pattern, msgid.strip()):
            return False
    
    # בדיקת מילות מפתח
    msgid_lower = msgid.lower()
    for keyword in NON_TRANSLATABLE_KEYWORDS:
        if keyword in msgid_lower:
            return False
    
    # מחרוזות קצרות מדי (פחות משני תווים)
    if len(msgid.strip()) < 2:
        return False
    
    # מחרוזות שמכילות רק סימנים או מספרים
    if re.match(r'^[^a-zA-Z]*$', msgid):
        return False
    
    return True

def clean_translation_template(input_file, output_file):
    """ניקוי וארגון קובץ תבנית התרגום"""
    
    print(f"מנקה קובץ תרגום: {input_file}")
    
    with open(input_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    lines = content.split('\n')
    clean_lines = []
    current_msgid = None
    skipped_count = 0
    kept_count = 0
    
    # כותרת מנוקה
    clean_lines.extend([
        "# תבנית תרגום מנוקה - BiblIA eScriptorium",
        "# =======================================",
        f"# נוצר בתאריך: {datetime.now().strftime('%d/%m/%Y %H:%M')}",
        "# רק מחרוזות הניתנות לתרגום",
        "",
        "# הוראות:",
        "# 1. מלא את השדה msgstr בתרגום עברי",
        "# 2. שמור על המרכאות",
        "# 3. השתמש בתווי בריחה לפי הצורך (\\n, \\', \\\")",
        "# 4. אחרי השלמת התרגום, הפעל את merge_translations.py",
        "",
        "# ============================================",
        ""
    ])
    
    i = 0
    while i < len(lines):
        line = lines[i].strip()
        
        # זיהוי msgid
        if line.startswith('msgid "'):
            msgid_match = re.match(r'msgid "(.*)"', line)
            if msgid_match:
                current_msgid = msgid_match.group(1)
                
                # בדיקה אם ניתן לתרגום
                if is_translatable(current_msgid):
                    # חפש את השורה הקודמת עם המקור
                    source_line = ""
                    for j in range(i-1, max(i-5, 0), -1):
                        if lines[j].strip().startswith('# #') and 'מקור:' in lines[j]:
                            source_line = lines[j].strip()
                            break
                    
                    if source_line:
                        clean_lines.append(source_line)
                    
                    clean_lines.append(line)
                    
                    # הוסף msgstr ריק
                    if i + 1 < len(lines) and lines[i + 1].strip().startswith('msgstr'):
                        clean_lines.append('msgstr ""')
                    else:
                        clean_lines.append('msgstr ""')
                    
                    clean_lines.append("")  # שורה ריקה להפרדה
                    kept_count += 1
                else:
                    skipped_count += 1
        
        i += 1
    
    # כתיבת הקובץ המנוקה
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write('\n'.join(clean_lines))
    
    print(f"✅ סיים לנקות!")
    print(f"📊 סטטיסטיקה:")
    print(f"   • נשמרו: {kept_count} מחרוזות")
    print(f"   • דולגו: {skipped_count} מחרוזות")
    print(f"   • קובץ חדש נוצר: {output_file}")

def main():
    """פונקציית ראשית"""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    # אם אנחנו בקונטיינר, השתמש בנתיב הנוכחי
    if script_dir.startswith('/usr/src/app'):
        input_file = "/usr/src/app/translation_template_to_complete.po"
        output_file = "/usr/src/app/translation_template_clean.po"
    else:
        project_root = os.path.dirname(script_dir)
        input_file = os.path.join(project_root, "translation_template_to_complete.po")
        output_file = os.path.join(project_root, "translation_template_clean.po")
    
    if not os.path.exists(input_file):
        print(f"❌ שגיאה: הקובץ לא נמצא: {input_file}")
        return
    
    clean_translation_template(input_file, output_file)

if __name__ == "__main__":
    main()