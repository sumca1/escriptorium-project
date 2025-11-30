# תכנון API פטפטן - מבוסס TaskReport אמיתי
## 22 אוקטובר 2025

### ✅ עקרון: לא להמציא - רק להציג!

**מקור האמת:** `reporting_taskreport.messages` (55KB+ של אזהרות!)

---

## 🎯 Endpoint חדש: GET /api/tasks/{id}/detailed/

**מטרה:** להציג את ה-messages בצורה מובנית וקריאה

### תשובה לדוגמה:

```json
{
  "task_id": 506,
  "status": "error",
  "status_display": "קרס",
  "method": "imports.tasks.document_import",
  "document": {
    "id": 8,
    "name": "Pinkas Training Set"
  },
  "timing": {
    "queued_at": "2025-10-22T17:15:00Z",
    "started_at": "2025-10-22T17:15:05Z",
    "done_at": "2025-10-22T17:15:48Z",
    "duration_seconds": 43,
    "cpu_cost": 0.0095,
    "gpu_cost": null
  },
  "summary": {
    "total_warnings": 48,
    "total_errors": 2,
    "lines_without_baseline": 45,
    "auto_added_block_types": ["paragraph", "other", "signature-mark"]
  },
  "warnings": [
    {
      "type": "missing_baseline",
      "file": "Page 105_1.xml",
      "line_number": 11,
      "message": "שורה ללא קו בסיס ב-Page 105_1.xml שורה מס' 11, סביר מאוד שלא תהיה שמישה!"
    },
    {
      "type": "missing_baseline",
      "file": "Page 105_1.xml",
      "line_number": 107,
      "message": "שורה ללא קו בסיס ב-Page 105_1.xml שורה מס' 107, סביר מאוד שלא תהיה שמישה!"
    }
    // ... 43 more
  ],
  "errors": [
    {
      "type": "duplicate_blocktype",
      "message": "get() returned more than one BlockType -- it returned 2!"
    },
    {
      "type": "duplicate_blocktype",  
      "message": "get() returned more than one BlockType -- it returned 2!"
    }
  ],
  "impact_assessment": {
    "severity": "medium",
    "usable_data_percentage": 93.8,
    "recommendation": "רוב הנתונים תקינים. 45 שורות ללא baseline לא ישמשו לאימון. שקול לנקות XMLs או לתקן ידנית."
  },
  "next_steps": [
    "בדוק את השורות עם בעיות בעורך",
    "אם רוצה לאמן - יש מספיק נתונים (93.8%)",
    "שקול לתקן XMLs לשיפור איכות"
  ]
}
```

---

## 🔧 יישום

### 1. Parser ל-messages

```python
# app/apps/api/message_parser.py

import re
from typing import List, Dict, Any

class TaskMessageParser:
    """Parse TaskReport.messages into structured data"""
    
    @staticmethod
    def parse(messages: str) -> Dict[str, Any]:
        """
        Parse raw messages string into structured warnings/errors
        
        Returns:
            {
                "warnings": [...],
                "errors": [...],
                "summary": {...}
            }
        """
        lines = messages.split('\n')
        
        warnings = []
        errors = []
        auto_added_blocks = []
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            # Parse: "שורה ללא קו בסיס ב-Page 105_1.xml שורה מס' 11, סביר..."
            baseline_match = re.search(
                r'שורה ללא קו בסיס ב-(.+\.xml) שורה מס\' (\d+)',
                line
            )
            if baseline_match:
                warnings.append({
                    'type': 'missing_baseline',
                    'file': baseline_match.group(1),
                    'line_number': int(baseline_match.group(2)),
                    'message': line
                })
                continue
            
            # Parse: "סוג בלוק paragraph נוסף אוטומטית לאונטולוגיה"
            block_match = re.search(
                r'סוג בלוק (.+) נוסף אוטומטית לאונטולוגיה',
                line
            )
            if block_match:
                block_type = block_match.group(1)
                if block_type not in auto_added_blocks:
                    auto_added_blocks.append(block_type)
                warnings.append({
                    'type': 'auto_added_block',
                    'block_type': block_type,
                    'message': line
                })
                continue
            
            # Parse: "get() returned more than one BlockType -- it returned 2!"
            if 'BlockType' in line or 'returned more than' in line:
                errors.append({
                    'type': 'duplicate_blocktype',
                    'message': line
                })
                continue
            
            # Generic error/warning
            if 'error' in line.lower() or 'שגיאה' in line:
                errors.append({'type': 'generic', 'message': line})
            else:
                warnings.append({'type': 'generic', 'message': line})
        
        # Calculate stats
        missing_baseline_count = sum(
            1 for w in warnings if w['type'] == 'missing_baseline'
        )
        
        return {
            'warnings': warnings,
            'errors': errors,
            'summary': {
                'total_warnings': len(warnings),
                'total_errors': len(errors),
                'lines_without_baseline': missing_baseline_count,
                'auto_added_block_types': auto_added_blocks
            }
        }
```

### 2. Enhanced Serializer

```python
# app/apps/api/serializers.py

from api.message_parser import TaskMessageParser

class DetailedTaskReportSerializer(serializers.ModelSerializer):
    """Detailed task report with parsed messages"""
    
    status_display = serializers.CharField(source='get_workflow_state_display')
    document_id = serializers.IntegerField(source='document.id', allow_null=True)
    document_name = serializers.CharField(source='document.name', allow_null=True)
    
    timing = serializers.SerializerMethodField()
    parsed_messages = serializers.SerializerMethodField()
    impact_assessment = serializers.SerializerMethodField()
    
    class Meta:
        model = TaskReport
        fields = [
            'id', 'label', 'method', 'workflow_state', 'status_display',
            'document_id', 'document_name',
            'timing', 'parsed_messages', 'impact_assessment'
        ]
    
    def get_timing(self, obj):
        duration = None
        if obj.started_at and obj.done_at:
            duration = (obj.done_at - obj.started_at).total_seconds()
            
        return {
            'queued_at': obj.queued_at.isoformat() if obj.queued_at else None,
            'started_at': obj.started_at.isoformat() if obj.started_at else None,
            'done_at': obj.done_at.isoformat() if obj.done_at else None,
            'duration_seconds': duration,
            'cpu_cost': obj.cpu_cost,
            'gpu_cost': obj.gpu_cost
        }
    
    def get_parsed_messages(self, obj):
        """Parse messages into structured data"""
        if not obj.messages:
            return {'warnings': [], 'errors': [], 'summary': {}}
        
        return TaskMessageParser.parse(obj.messages)
    
    def get_impact_assessment(self, obj):
        """Assess impact of warnings/errors"""
        parsed = self.get_parsed_messages(obj)
        
        total_warnings = parsed['summary']['total_warnings']
        total_errors = parsed['summary']['total_errors']
        missing_baselines = parsed['summary'].get('lines_without_baseline', 0)
        
        # Simple heuristic for severity
        if total_errors > 5:
            severity = 'high'
        elif total_errors > 0 or missing_baselines > 100:
            severity = 'medium'
        elif missing_baselines > 20:
            severity = 'low'
        else:
            severity = 'minimal'
        
        # Estimate usable data (rough calculation)
        # Assume ~50 lines per part, 24 parts = 1200 lines
        # missing_baselines won't be used
        estimated_total = 1200
        usable = max(0, estimated_total - missing_baselines)
        usable_percentage = (usable / estimated_total * 100) if estimated_total > 0 else 0
        
        recommendation = self._get_recommendation(severity, usable_percentage, total_errors)
        
        return {
            'severity': severity,
            'usable_data_percentage': round(usable_percentage, 1),
            'recommendation': recommendation
        }
    
    def _get_recommendation(self, severity, usable_pct, errors):
        if severity == 'high':
            return "יש בעיות רציניות. מומלץ לבדוק ולתקן לפני המשך."
        elif severity == 'medium':
            if usable_pct > 90:
                return f"רוב הנתונים תקינים ({usable_pct}%). ניתן להמשיך לאימון."
            else:
                return f"יש בעיות. רק {usable_pct}% מהנתונים שמישים. שקול תיקון."
        else:
            return "הנתונים באיכות טובה. ניתן להמשיך."
```

### 3. View

```python
# app/apps/api/views.py

class DetailedTaskReportView(RetrieveAPIView):
    """
    Get detailed task report with parsed messages
    
    GET /api/tasks/{id}/detailed/
    """
    permission_classes = [IsAuthenticated]
    serializer_class = DetailedTaskReportSerializer
    queryset = TaskReport.objects.all()
```

### 4. URL

```python
# app/apps/api/urls.py

path('tasks/<int:pk>/detailed/', 
     DetailedTaskReportView.as_view(), 
     name='task-detailed'),
```

---

## 🧪 שימוש

```powershell
# בדיקת ייבוא Document 8
$taskId = 506  # מזהה TaskReport
$result = Invoke-RestMethod `
    -Uri "http://localhost:8082/api/tasks/$taskId/detailed/" `
    -Headers @{ 'Authorization' = "Token $token" }

# הצג סיכום
Write-Host "Severity: $($result.impact_assessment.severity)"
Write-Host "Usable Data: $($result.impact_assessment.usable_data_percentage)%"
Write-Host "Warnings: $($result.parsed_messages.summary.total_warnings)"
Write-Host "Errors: $($result.parsed_messages.summary.total_errors)"
```

---

## ✅ יתרונות הגישה הזו

1. **אמיתי** - קורא מ-TaskReport, לא ממציא
2. **מובנה** - JSON קריא במקום text blob
3. **שימושי** - impact_assessment + recommendations
4. **הרחבה** - קל להוסיף parsers למסרים נוספים
5. **פטפטן** - מסביר מה קרה ומה לעשות

---

## 🚀 מה הלאה?

1. **ליישם את זה!**
2. **לבדוק עם ייבוא אמיתי**
3. **להוסיף parsers למסרים נוספים** (train, segtrain, etc.)
4. **לשפר recommendations** (ML-based?)
5. **להוסיף WebSocket** לעדכונים בזמן אמת
