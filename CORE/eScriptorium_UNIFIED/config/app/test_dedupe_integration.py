#!/usr/bin/env python
"""
Integration test for PO deduplication in Django.
This script verifies that the dedupe_po_messages command works correctly.
"""

import os
import sys
import django
from pathlib import Path

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'escriptorium.settings')
sys.path.insert(0, str(Path(__file__).parent))

try:
    django.setup()
except Exception as e:
    print(f"Warning: Could not setup Django: {e}")
    print("Continuing with basic polib test...")

try:
    import polib
except ImportError:
    print("Error: polib not installed. Install with: pip install polib")
    sys.exit(1)

from django.core.management import call_command
from django.conf import settings

def test_dedupe_command():
    """Test the dedupe_po_messages management command."""
    print("=" * 60)
    print("Testing PO Deduplication Integration")
    print("=" * 60)
    
    # Get locale path
    if hasattr(settings, 'LOCALE_PATHS') and settings.LOCALE_PATHS:
        locale_path = Path(settings.LOCALE_PATHS[0])
    else:
        locale_path = Path(settings.BASE_DIR) / 'locale'
    
    print(f"\nLocale directory: {locale_path}")
    
    # Find all .po files
    po_files = sorted(locale_path.glob('**/*.po'))
    print(f"Found {len(po_files)} .po files:")
    
    for po_file in po_files:
        po = polib.pofile(str(po_file))
        print(f"  - {po_file.relative_to(locale_path)}: {len(po)} entries")
    
    # Run dedupe command in dry-run mode first
    print("\n" + "=" * 60)
    print("Running dedupe_po_messages --dry-run")
    print("=" * 60)
    
    try:
        call_command('dedupe_po_messages', dry_run=True)
    except Exception as e:
        print(f"Error running command: {e}")
        return False
    
    print("\n" + "=" * 60)
    print("✓ Integration test completed successfully!")
    print("=" * 60)
    print("\nTo actually deduplicate files, run:")
    print("  python manage.py dedupe_po_messages --inplace --backup")
    
    return True

if __name__ == '__main__':
    success = test_dedupe_command()
    sys.exit(0 if success else 1)
