# Generated manually

from django.db import migrations


def populate_typology_hebrew_names(apps, schema_editor):
    """Populate name_he for typology models from translation mapping"""
    from apps.core.typology_translations_he import TYPOLOGY_TRANSLATIONS_HE
    
    BlockType = apps.get_model('core', 'BlockType')
    LineType = apps.get_model('core', 'LineType')
    DocumentType = apps.get_model('core', 'DocumentType')
    DocumentPartType = apps.get_model('core', 'DocumentPartType')
    
    # Update BlockType
    for block_type in BlockType.objects.all():
        if block_type.name in TYPOLOGY_TRANSLATIONS_HE:
            block_type.name_he = TYPOLOGY_TRANSLATIONS_HE[block_type.name]
            block_type.save()
            print(f"Updated BlockType: {block_type.name} -> {block_type.name_he}")
    
    # Update LineType
    for line_type in LineType.objects.all():
        if line_type.name in TYPOLOGY_TRANSLATIONS_HE:
            line_type.name_he = TYPOLOGY_TRANSLATIONS_HE[line_type.name]
            line_type.save()
            print(f"Updated LineType: {line_type.name} -> {line_type.name_he}")
    
    # Update DocumentType
    for doc_type in DocumentType.objects.all():
        if doc_type.name in TYPOLOGY_TRANSLATIONS_HE:
            doc_type.name_he = TYPOLOGY_TRANSLATIONS_HE[doc_type.name]
            doc_type.save()
            print(f"Updated DocumentType: {doc_type.name} -> {doc_type.name_he}")
    
    # Update DocumentPartType
    for part_type in DocumentPartType.objects.all():
        if part_type.name in TYPOLOGY_TRANSLATIONS_HE:
            part_type.name_he = TYPOLOGY_TRANSLATIONS_HE[part_type.name]
            part_type.save()
            print(f"Updated DocumentPartType: {part_type.name} -> {part_type.name_he}")


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0077_add_typology_name_he'),
    ]

    operations = [
        migrations.RunPython(populate_typology_hebrew_names, migrations.RunPython.noop),
    ]
