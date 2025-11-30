"""
Django management command to remove duplicate msgid entries from .po files.
Runs automatically as part of compilemessages or manually.

Usage:
    python manage.py dedupe_po_messages
    python manage.py dedupe_po_messages --dry-run
    python manage.py dedupe_po_messages --inplace --backup
"""

from pathlib import Path
from datetime import datetime
import shutil

from django.core.management.base import BaseCommand
from django.conf import settings

try:
    import polib
except ImportError:
    print("Error: polib not found. Install it with: pip install polib")
    raise SystemExit(1)


class Command(BaseCommand):
    help = 'Remove duplicate msgid entries from .po translation files'

    def add_arguments(self, parser):
        parser.add_argument(
            '--locale-dir',
            type=str,
            default=None,
            help='Scan this directory for .po files (default: settings.LOCALE_PATHS)'
        )
        parser.add_argument(
            '--inplace',
            action='store_true',
            help='Overwrite original files'
        )
        parser.add_argument(
            '--backup',
            action='store_true',
            help='Create timestamped backup before modifying'
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be done without making changes'
        )

    def dedupe_po(self, po_path):
        """Remove duplicate msgid entries from a .po file."""
        po = polib.pofile(str(po_path))
        seen = {}
        
        # Track which indices to keep
        for i, entry in enumerate(po):
            key = (entry.msgctxt or '', entry.msgid)
            if key in seen:
                prev_idx = seen[key]
                prev = po[prev_idx]
                # Prefer entry with non-empty msgstr
                if (not prev.msgstr.strip()) and entry.msgstr.strip():
                    seen[key] = i
            else:
                seen[key] = i
        
        # Rebuild PO file with only kept entries
        kept_indices = set(seen.values())
        new_po = polib.POFile()
        new_po.metadata = po.metadata
        
        for idx, entry in enumerate(po):
            if idx in kept_indices:
                new_po.append(entry)
        
        removed_count = len(po) - len(new_po)
        return new_po, removed_count

    def handle(self, *args, **options):
        locale_dir = options.get('locale_dir')
        inplace = options.get('inplace', False)
        backup = options.get('backup', False)
        dry_run = options.get('dry_run', False)
        
        # Determine which directory to scan
        if locale_dir:
            locale_path = Path(locale_dir)
        else:
            # Use Django's LOCALE_PATHS if available
            if hasattr(settings, 'LOCALE_PATHS') and settings.LOCALE_PATHS:
                locale_path = Path(settings.LOCALE_PATHS[0])
            else:
                locale_path = Path(settings.BASE_DIR) / 'locale'
        
        if not locale_path.exists():
            self.stdout.write(
                self.style.ERROR(f'Locale directory not found: {locale_path}')
            )
            return
        
        # Find all .po files
        po_files = sorted(locale_path.glob('**/*.po'))
        
        if not po_files:
            self.stdout.write(
                self.style.WARNING(f'No .po files found in {locale_path}')
            )
            return
        
        self.stdout.write(
            self.style.SUCCESS(f'Found {len(po_files)} .po file(s) to scan.')
        )
        
        total_removed = 0
        for po_path in po_files:
            new_po, removed = self.dedupe_po(po_path)
            total_removed += removed
            
            if removed == 0:
                self.stdout.write(f'  ✓ {po_path.relative_to(locale_path)}: No duplicates')
            else:
                self.stdout.write(
                    self.style.WARNING(f'  ⚠ {po_path.relative_to(locale_path)}: Found {removed} duplicate entries')
                )
            
            if dry_run:
                continue
            
            # Determine output path
            if inplace:
                out_path = po_path
            else:
                out_path = po_path.with_name(po_path.stem + '_deduped' + po_path.suffix)
            
            # Create backup if requested
            if backup and removed > 0:
                bak = po_path.with_suffix(po_path.suffix + f'.bak.{datetime.now().strftime("%Y%m%d%H%M%S")}')
                shutil.copy2(po_path, bak)
                self.stdout.write(f'    Backup: {bak.relative_to(locale_path)}')
            
            # Write deduplicated file
            if removed > 0:
                new_po.save(str(out_path))
                if inplace:
                    self.stdout.write(self.style.SUCCESS(f'    Updated: {po_path.name}'))
                else:
                    self.stdout.write(self.style.SUCCESS(f'    Saved to: {out_path.name}'))
        
        # Final summary
        if dry_run:
            self.stdout.write(
                self.style.WARNING(
                    f'\nDry-run complete. Would have removed {total_removed} duplicate entries total.'
                )
            )
        else:
            self.stdout.write(
                self.style.SUCCESS(
                    f'\n✓ Done. Removed {total_removed} duplicate entries total.'
                )
            )
