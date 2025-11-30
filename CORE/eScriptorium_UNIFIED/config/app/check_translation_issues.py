#!/usr/bin/env python3
"""
סקריפט מתקדם לבדיקת בעיות נפוצות בקבצי תרגום
"""

import re
import sys

def check_translation_issues(po_file_path):
    """בודק בעיות נפוצות בקובץ תרגום"""
    
    print("🔍 בודק בעיות נפוצות בתרגומים...")
    print("=" * 70)
    
    issues = []
    
    with open(po_file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    for i, line in enumerate(lines, 1):
        line_stripped = line.strip()
        
        # בדיקה 1: תווים בעייתיים בתחילת/סוף מחרוזת
        if line_stripped.startswith('msgstr "') and line_stripped.endswith('"'):
            content = line_stripped[8:-1]
            
            # תווים בעייתיים
            if content.startswith(' ') or content.endswith(' '):
                issues.append({
                    'line': i,
                    'type': 'רווחים',
                    'issue': 'רווח מיותר בתחילת/סוף מחרוזת',
                    'content': content[:50]
                })
            
            # בדיקת quotes לא מקודדים
            if content.count('"') % 2 != 0:
                issues.append({
                    'line': i,
                    'type': 'quotes',
                    'issue': 'מספר לא זוגי של גרשיים (") במחרוזת',
                    'content': content[:50]
                })
            
            # בדיקת תגי HTML פתוחים
            open_tags = re.findall(r'<(\w+)[^/>]*>(?![^<]*</\1>)', content)
            if open_tags and 'br' not in open_tags:
                issues.append({
                    'line': i,
                    'type': 'HTML',
                    'issue': f'תגים פתוחים אפשריים: {open_tags}',
                    'content': content[:50]
                })
            
            # בדיקת % formatting
            msgid_placeholders = set()
            msgstr_placeholders = set()
            
            # חיפוש placeholders במחרוזת הנוכחית
            placeholders = re.findall(r'%\((\w+)\)[sd]', content)
            if placeholders:
                msgstr_placeholders = set(placeholders)
                
                # חיפוש msgid המתאים (שורות קודמות)
                for j in range(max(0, i-10), i):
                    if lines[j].strip().startswith('msgid "'):
                        msgid_content = lines[j].strip()[7:-1]
                        msgid_placeholders = set(re.findall(r'%\((\w+)\)[sd]', msgid_content))
                        break
                
                # השוואה
                if msgid_placeholders and msgstr_placeholders != msgid_placeholders:
                    issues.append({
                        'line': i,
                        'type': 'placeholders',
                        'issue': f'אי-התאמה בplaceholders',
                        'msgid_ph': list(msgid_placeholders),
                        'msgstr_ph': list(msgstr_placeholders),
                        'content': content[:50]
                    })
        
        # בדיקה 2: שורות רב-שורתיות לא תקינות
        if line_stripped == 'msgstr ""' and i < len(lines):
            # בדיקה אם יש המשך
            next_line = lines[i].strip() if i < len(lines) else ""
            if next_line and not next_line.startswith('"'):
                issues.append({
                    'line': i,
                    'type': 'empty',
                    'issue': 'תרגום ריק ללא המשך',
                    'content': ''
                })
    
    # הצגת תוצאות
    if not issues:
        print("\n✅ לא נמצאו בעיות!")
        return 0
    
    print(f"\n⚠️  נמצאו {len(issues)} בעיות אפשריות:\n")
    
    issues_by_type = {}
    for issue in issues:
        itype = issue['type']
        if itype not in issues_by_type:
            issues_by_type[itype] = []
        issues_by_type[itype].append(issue)
    
    for itype, type_issues in issues_by_type.items():
        print(f"\n📌 {itype.upper()} ({len(type_issues)} בעיות):")
        for i, issue in enumerate(type_issues[:5], 1):
            print(f"\n   {i}. שורה {issue['line']}:")
            print(f"      בעיה: {issue['issue']}")
            if 'content' in issue and issue['content']:
                print(f"      תוכן: {issue['content']}...")
            if 'msgid_ph' in issue:
                print(f"      Placeholders במקור: {issue['msgid_ph']}")
                print(f"      Placeholders בתרגום: {issue['msgstr_ph']}")
        
        if len(type_issues) > 5:
            print(f"\n   ... ועוד {len(type_issues) - 5} בעיות נוספות")
    
    return len(issues)

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python check_translation_issues.py <po_file>")
        sys.exit(1)
    
    po_file = sys.argv[1]
    
    try:
        issue_count = check_translation_issues(po_file)
        
        if issue_count > 0:
            print(f"\n⚠️  נמצאו {issue_count} בעיות אפשריות.")
            print("   מומלץ לבדוק ולתקן אותן.")
        else:
            print("\n✅ הקובץ נראה תקין!")
        
        sys.exit(0)
        
    except FileNotFoundError:
        print(f"❌ קובץ לא נמצא: {po_file}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ שגיאה: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
