"""
BiblIA Unified Translation System - Demo View

דוגמה פשוטה שמראה איך המערכת עובדת.

תאריך: 2 בנובמבר 2025
"""

from django.shortcuts import render
from django.http import HttpResponse
from translations.translation_loader import t


def translation_demo(request):
    """
    Demo page להצגת מערכת התרגום החדשה.
    
    URL: /translation-demo/
    """
    # דוגמה לשימוש ב-t() בתוך view
    context = {
        'page_title': t('BiblIA Translation Demo'),
        'total_translations': '3,466',
        'categories': {
            'ui': 251,
            'forms': 141,
            'messages': 146,
            'tooltips': 9,
            'pages': 337,
            'general': 2582,
        }
    }
    
    return render(request, 'translation_demo.html', context)


def translation_test(request):
    """
    בדיקה פשוטה של תרגומים (JSON response).
    
    URL: /translation-test/
    """
    from django.http import JsonResponse
    
    tests = {
        'Home': t('Home'),
        'Close': t('Close'),
        'Save': t('Save'),
        'Cancel': t('Cancel'),
        'Name': t('Name'),
        'Description': t('Description'),
        'My Projects': t('My Projects'),
        'Create New': t('Create New'),
    }
    
    return JsonResponse({
        'success': True,
        'translations': tests,
        'total_available': 3466,
        'message': 'מערכת התרגום עובדת! ✅'
    }, json_dumps_params={'ensure_ascii': False})
