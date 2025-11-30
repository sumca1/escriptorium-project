#!/usr/bin/env python3
"""
Translation Coverage Checker - French
בודק כיסוי תרגומים צרפתית מול אנגלית
"""

import re
import os

def extract_msgids_from_pot(file_path):
    """חולץ msgid מקובץ POT/PO"""
    msgids = []
    if not os.path.exists(file_path):
        print(f"❌ קובץ לא נמצא: {file_path}")
        return msgids
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # מוצא את כל ה-msgid
    pattern = r'^msgid "([^"]*)"'
    matches = re.findall(pattern, content, re.MULTILINE)
    
    # מנקה את הערכים הריקים (השורה הראשונה)
    msgids = [msg for msg in matches if msg.strip()]
    
    return msgids

def extract_msgids_from_po(file_path):
    """חולץ msgid מקובץ PO ובודק אם יש תרגום"""
    msgids_with_translation = []
    msgids_without_translation = []
    
    if not os.path.exists(file_path):
        print(f"❌ קובץ לא נמצא: {file_path}")
        return msgids_with_translation, msgids_without_translation
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # מחלק לבלוקים של msgid/msgstr
    blocks = re.split(r'\n(?=msgid)', content)
    
    for block in blocks:
        msgid_match = re.search(r'^msgid "([^"]*)"', block, re.MULTILINE)
        if msgid_match:
            msgid = msgid_match.group(1)
            if msgid.strip():  # מתעלם מהשורה הריקה הראשונה
                msgstr_match = re.search(r'^msgstr "([^"]*)"', block, re.MULTILINE)
                if msgstr_match and msgstr_match.group(1).strip():
                    msgids_with_translation.append(msgid)
                else:
                    msgids_without_translation.append(msgid)
    
    return msgids_with_translation, msgids_without_translation

def main():
    print("🇫🇷 בודק כיסוי תרגומים צרפתית מול אנגלית")
    print("=" * 50)
    
    base_path = "G:/OCR_Arabic_Testing/BiblIA_dataset-project/BiblIA_dataset/escriptorium/app/locale"
    english_file = f"{base_path}/en/LC_MESSAGES/django.pot"
    french_file = f"{base_path}/fr/LC_MESSAGES/django.po"
    
    print("🔍 מחלץ msgid מקובץ האנגלית...")
    english_msgids = extract_msgids_from_pot(english_file)
    print(f"נמצאו {len(english_msgids)} מחרוזות באנגלית")
    
    print("🔍 מחלץ msgid מקובץ הצרפתית...")
    french_with_translation, french_without_translation = extract_msgids_from_po(french_file)
    all_french_msgids = french_with_translation + french_without_translation
    
    print(f"נמצאו {len(all_french_msgids)} מחרוזות בצרפתית")
    print(f"מתורגמות: {len(french_with_translation)}")
    print(f"לא מתורגמות: {len(french_without_translation)}")
    
    # מוצא הבדלים
    english_set = set(english_msgids)
    french_set = set(all_french_msgids)
    
    missing_in_french = english_set - french_set
    extra_in_french = french_set - english_set
    
    print("\n" + "=" * 60)
    print("📊 תוצאות ההשוואה:")
    print("=" * 60)
    
    print(f"📝 סך הכל מחרוזות באנגלית: {len(english_msgids)}")
    print(f"📝 סך הכל מחרוזות בצרפתית: {len(all_french_msgids)}")
    print(f"✅ מתורגמות בצרפתית: {len(french_with_translation)}")
    print(f"❌ לא מתורגמות בצרפתית: {len(french_without_translation)}")
    print(f"❌ חסר בצרפתית: {len(missing_in_french)}")
    print(f"➕ עודף בצרפתית: {len(extra_in_french)}")
    
    # חישוב אחוזים
    if len(english_msgids) > 0:
        coverage_percent = (len(all_french_msgids) / len(english_msgids)) * 100
        translation_percent = (len(french_with_translation) / len(english_msgids)) * 100
        print(f"\n📈 אחוז כיסוי (כמות): {coverage_percent:.1f}%")
        print(f"📈 אחוז תרגום פועל: {translation_percent:.1f}%")
    
    # שומר דוח מפורט
    report_file = "french_translation_coverage_report.txt"
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write("דוח כיסוי תרגומים - צרפתית מול אנגלית\n")
        f.write("=" * 50 + "\n\n")
        
        f.write(f"סך הכל מחרוזות באנגלית: {len(english_msgids)}\n")
        f.write(f"סך הכל מחרוזות בצרפתית: {len(all_french_msgids)}\n")
        f.write(f"מתורגמות בצרפתית: {len(french_with_translation)}\n")
        f.write(f"לא מתורגמות בצרפתית: {len(french_without_translation)}\n")
        f.write(f"חסר בצרפתית: {len(missing_in_french)}\n")
        f.write(f"עודף בצרפתית: {len(extra_in_french)}\n\n")
        
        if missing_in_french:
            f.write("מחרוזות חסרות בצרפתית:\n")
            f.write("-" * 40 + "\n")
            for i, msg in enumerate(sorted(missing_in_french)[:50], 1):
                preview = msg[:70] + "..." if len(msg) > 70 else msg
                f.write(f"{i:3d}. {preview}\n")
            if len(missing_in_french) > 50:
                f.write(f"... ועוד {len(missing_in_french) - 50} מחרוזות\n")
        
        if french_without_translation:
            f.write("\nמחרוזות לא מתורגמות בצרפתית:\n")
            f.write("-" * 40 + "\n")
            for i, msg in enumerate(sorted(french_without_translation)[:50], 1):
                preview = msg[:70] + "..." if len(msg) > 70 else msg
                f.write(f"{i:3d}. {preview}\n")
            if len(french_without_translation) > 50:
                f.write(f"... ועוד {len(french_without_translation) - 50} מחרוזות\n")
    
    print(f"\n💾 הדוח נשמר ב: {os.path.abspath(report_file)}")
    
    if missing_in_french or french_without_translation:
        print("⚠️  יש בעיות בתרגום הצרפתי")
    else:
        print("✅ התרגום הצרפתי מלא!")
    
    print("\n✅ הבדיקה הושלמה")

if __name__ == "__main__":
    main()