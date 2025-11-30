#!/usr/bin/env python3
"""
השוואת msgid בין האנגלית (template) לעברית
מוצא מה חסר בתרגום העברי
"""

import re
import sys

def extract_msgids(filepath):
    """מחלץ את כל ה-msgid מקובץ po/pot"""
    msgids = set()
    
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # מוצא את כל ה-msgid (עם תמיכה במחרוזות רב-שורתיות)
        pattern = r'msgid\s+"([^"]*(?:\\.[^"]*)*)"'
        matches = re.findall(pattern, content, re.MULTILINE | re.DOTALL)
        
        for match in matches:
            # מנקה escape characters
            cleaned = match.replace('\\"', '"').replace('\\n', '\n').replace('\\t', '\t')
            if cleaned.strip():  # רק מחרוזות לא ריקות
                msgids.add(cleaned)
                
        return msgids
        
    except Exception as e:
        print(f"שגיאה בקריאת {filepath}: {e}")
        return set()

def compare_translations():
    """משווה בין הקובצים"""
    
    # נתיבי הקבצים
    en_file = "G:/OCR_Arabic_Testing/BiblIA_dataset-project/BiblIA_dataset/escriptorium/app/locale/en/LC_MESSAGES/django.pot"
    he_file = "G:/OCR_Arabic_Testing/BiblIA_dataset-project/BiblIA_dataset/escriptorium/app/locale/he/LC_MESSAGES/django.po"
    
    print("🔍 מחלץ msgid מקובץ האנגלית...")
    en_msgids = extract_msgids(en_file)
    print(f"נמצאו {len(en_msgids)} מחרוזות באנגלית")
    
    print("🔍 מחלץ msgid מקובץ העברית...")
    he_msgids = extract_msgids(he_file)
    print(f"נמצאו {len(he_msgids)} מחרוזות בעברית")
    
    # מוצא מה חסר בעברית
    missing_in_hebrew = en_msgids - he_msgids
    
    # מוצא מה עודף בעברית (לא צריך להיות)
    extra_in_hebrew = he_msgids - en_msgids
    
    print("\n" + "="*60)
    print("📊 תוצאות ההשוואה:")
    print("="*60)
    
    print(f"📝 סך הכל מחרוזות באנגלית: {len(en_msgids)}")
    print(f"📝 סך הכל מחרוזות בעברית: {len(he_msgids)}")
    print(f"❌ חסר בעברית: {len(missing_in_hebrew)}")
    print(f"➕ עודף בעברית: {len(extra_in_hebrew)}")
    
    if missing_in_hebrew:
        print(f"\n🔍 המחרוזות החסרות בעברית ({len(missing_in_hebrew)}):")
        print("-" * 40)
        for i, msgid in enumerate(sorted(missing_in_hebrew), 1):
            preview = msgid[:60] + "..." if len(msgid) > 60 else msgid
            print(f"{i:2d}. {preview}")
            
    if extra_in_hebrew:
        print(f"\n➕ מחרוזות עודפות בעברית ({len(extra_in_hebrew)}):")
        print("-" * 40)
        for i, msgid in enumerate(sorted(extra_in_hebrew), 1):
            preview = msgid[:60] + "..." if len(msgid) > 60 else msgid
            print(f"{i:2d}. {preview}")
    
    # חישוב אחוז הכיסוי
    if len(en_msgids) > 0:
        coverage = (len(he_msgids) / len(en_msgids)) * 100
        print(f"\n📈 אחוז כיסוי: {coverage:.1f}%")
    
    # שמירת הדוח
    report_file = "G:/OCR_Arabic_Testing/BiblIA_dataset-project/BiblIA_dataset/eScriptorium_CLEAN/translation_coverage_report.txt"
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write("דוח כיסוי תרגומים - אנגלית מול עברית\n")
        f.write("="*50 + "\n\n")
        f.write(f"סך הכל מחרוזות באנגלית: {len(en_msgids)}\n")
        f.write(f"סך הכל מחרוזות בעברית: {len(he_msgids)}\n")
        f.write(f"חסר בעברית: {len(missing_in_hebrew)}\n")
        f.write(f"עודף בעברית: {len(extra_in_hebrew)}\n")
        
        if coverage:
            f.write(f"אחוז כיסוי: {coverage:.1f}%\n")
        
        if missing_in_hebrew:
            f.write(f"\nמחרוזות חסרות בעברית:\n")
            f.write("-" * 30 + "\n")
            for msgid in sorted(missing_in_hebrew):
                f.write(f"• {msgid}\n")
    
    print(f"\n💾 הדוח נשמר ב: {report_file}")
    
    return len(missing_in_hebrew) == 0

if __name__ == "__main__":
    print("🔍 בודק כיסוי תרגומים עברית מול אנגלית")
    print("="*50)
    
    is_complete = compare_translations()
    
    if is_complete:
        print("\n🎉 כל המחרוזות מתורגמות!")
    else:
        print("\n⚠️  יש מחרוזות חסרות בתרגום העברי")
    
    print("\n✅ הבדיקה הושלמה")