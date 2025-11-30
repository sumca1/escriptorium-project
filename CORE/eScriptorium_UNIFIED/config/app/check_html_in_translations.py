#!/usr/bin/env python3
"""
סקריפט לבדיקת תקינות HTML בקבצי תרגום
מחפש תגים לא מאוזנים, תגים פתוחים, בעיות תחביר
"""

import re
import sys

def check_html_tags(po_file_path):
    """בודק תקינות תגי HTML בקובץ .po"""
    
    print("🔍 בודק תקינות תגי HTML בתרגומים...")
    print("=" * 60)
    
    errors = []
    warnings = []
    
    with open(po_file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    current_msgid = ""
    current_msgstr = ""
    line_num = 0
    in_msgid = False
    in_msgstr = False
    
    for i, line in enumerate(lines, 1):
        line = line.strip()
        
        # זיהוי msgid
        if line.startswith('msgid "'):
            current_msgid = line[7:-1]  # הסרת msgid " ו- "
            in_msgid = True
            in_msgstr = False
            line_num = i
            
        # זיהוי msgstr
        elif line.startswith('msgstr "'):
            current_msgstr = line[8:-1]  # הסרת msgstr " ו- "
            in_msgstr = True
            in_msgid = False
            
        # המשך של מחרוזת רב-שורתית
        elif line.startswith('"') and line.endswith('"'):
            text = line[1:-1]
            if in_msgid:
                current_msgid += text
            elif in_msgstr:
                current_msgstr += text
                
        # כשמסתיים בלוק - בדיקה
        elif line == "" or not line.startswith('"'):
            if current_msgid and current_msgstr:
                # בדיקת התאמת תגים
                msgid_tags = extract_html_tags(current_msgid)
                msgstr_tags = extract_html_tags(current_msgstr)
                
                if msgid_tags != msgstr_tags:
                    # בדיקה אם זה תג עצמי-סוגר כמו <br>
                    if '<br>' in current_msgstr or '<br/>' in current_msgstr:
                        if '<br>' in current_msgid or '<br/>' in current_msgid:
                            pass  # זה OK
                        else:
                            warnings.append({
                                'line': line_num,
                                'msgid': current_msgid[:50],
                                'msgstr': current_msgstr[:50],
                                'issue': 'תג <br> נוסף בתרגום אבל לא במקור'
                            })
                    else:
                        errors.append({
                            'line': line_num,
                            'msgid': current_msgid[:50],
                            'msgstr': current_msgstr[:50],
                            'msgid_tags': msgid_tags,
                            'msgstr_tags': msgstr_tags
                        })
                
                # בדיקת תגים לא סגורים
                unclosed_msgid = find_unclosed_tags(current_msgid)
                unclosed_msgstr = find_unclosed_tags(current_msgstr)
                
                if unclosed_msgid:
                    errors.append({
                        'line': line_num,
                        'msgid': current_msgid[:50],
                        'issue': f'תגים לא סגורים במקור: {unclosed_msgid}'
                    })
                    
                if unclosed_msgstr:
                    errors.append({
                        'line': line_num,
                        'msgstr': current_msgstr[:50],
                        'issue': f'תגים לא סגורים בתרגום: {unclosed_msgstr}'
                    })
            
            current_msgid = ""
            current_msgstr = ""
            in_msgid = False
            in_msgstr = False
    
    # הצגת תוצאות
    print(f"\n📊 סיכום:")
    print(f"   ❌ שגיאות קריטיות: {len(errors)}")
    print(f"   ⚠️  אזהרות: {len(warnings)}")
    
    if errors:
        print(f"\n❌ שגיאות קריטיות ({len(errors)}):")
        for i, error in enumerate(errors[:10], 1):
            print(f"\n   {i}. שורה {error.get('line', '?')}:")
            if 'msgid' in error:
                print(f"      msgid:  {error['msgid']}...")
            if 'msgstr' in error:
                print(f"      msgstr: {error['msgstr']}...")
            if 'msgid_tags' in error:
                print(f"      תגי מקור: {error['msgid_tags']}")
                print(f"      תגי תרגום: {error['msgstr_tags']}")
            if 'issue' in error:
                print(f"      בעיה: {error['issue']}")
    
    if warnings:
        print(f"\n⚠️  אזהרות ({len(warnings)}):")
        for i, warn in enumerate(warnings[:10], 1):
            print(f"\n   {i}. שורה {warn.get('line', '?')}:")
            print(f"      msgid:  {warn['msgid']}...")
            print(f"      msgstr: {warn['msgstr']}...")
            print(f"      בעיה: {warn['issue']}")
    
    return len(errors), len(warnings)

def extract_html_tags(text):
    """מחלץ תגי HTML מטקסט"""
    # מציאת כל התגים
    tags = re.findall(r'<(/?)(\w+)[^>]*>', text)
    
    # ספירת תגים פותחים וסוגרים
    tag_counts = {}
    for closing, tag in tags:
        tag = tag.lower()
        if tag == 'br':  # תגים עצמיים-סוגרים
            continue
        if closing:
            tag_counts[tag] = tag_counts.get(tag, 0) - 1
        else:
            tag_counts[tag] = tag_counts.get(tag, 0) + 1
    
    return tag_counts

def find_unclosed_tags(text):
    """מוצא תגים לא סגורים"""
    stack = []
    unclosed = []
    
    # מציאת תגים
    tags = re.finditer(r'<(/?)(\w+)[^>]*>', text)
    
    for match in tags:
        closing = match.group(1)
        tag = match.group(2).lower()
        
        # דילוג על תגים עצמיים-סוגרים
        if tag in ['br', 'hr', 'img', 'input', 'meta', 'link']:
            continue
        
        if closing:
            if stack and stack[-1] == tag:
                stack.pop()
            else:
                unclosed.append(f'</{tag}> ללא פתיחה')
        else:
            stack.append(tag)
    
    # תגים שנשארו בstack הם תגים פתוחים
    for tag in stack:
        unclosed.append(f'<{tag}> לא נסגר')
    
    return unclosed

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python check_html_in_translations.py <po_file>")
        sys.exit(1)
    
    po_file = sys.argv[1]
    
    try:
        errors, warnings = check_html_tags(po_file)
        
        if errors > 0:
            print(f"\n🚨 נמצאו {errors} שגיאות קריטיות!")
            print("   יש לתקן אותן כדי למנוע שיבוש HTML.")
            sys.exit(1)
        elif warnings > 0:
            print(f"\n⚠️  נמצאו {warnings} אזהרות.")
            print("   מומלץ לבדוק אותן.")
            sys.exit(0)
        else:
            print("\n✅ כל תגי ה-HTML מאוזנים ותקינים!")
            sys.exit(0)
            
    except FileNotFoundError:
        print(f"❌ קובץ לא נמצא: {po_file}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ שגיאה: {e}")
        sys.exit(1)
