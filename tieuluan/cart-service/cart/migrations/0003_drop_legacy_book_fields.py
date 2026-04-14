from django.db import migrations


def backfill_from_legacy_fields(apps, schema_editor):
    CartItem = apps.get_model('cart', 'CartItem')

    for item in CartItem.objects.all().iterator():
        changed_fields = []

        legacy_book_id = getattr(item, 'book_id', None)
        legacy_book_title = getattr(item, 'book_title', '')
        legacy_book_author = getattr(item, 'book_author', '')
        legacy_book_cover_url = getattr(item, 'book_cover_url', '')

        if not item.product_id and legacy_book_id:
            item.product_id = legacy_book_id
            changed_fields.append('product_id')

        if not item.product_name and legacy_book_title:
            item.product_name = legacy_book_title
            changed_fields.append('product_name')

        if not item.product_subtitle and legacy_book_author:
            item.product_subtitle = legacy_book_author
            changed_fields.append('product_subtitle')

        if not item.product_image_url and legacy_book_cover_url:
            item.product_image_url = legacy_book_cover_url
            changed_fields.append('product_image_url')

        if changed_fields:
            item.save(update_fields=changed_fields)


class Migration(migrations.Migration):

    dependencies = [
        ('cart', '0002_schema_hotfix'),
    ]

    operations = [
        migrations.RunPython(backfill_from_legacy_fields, reverse_code=migrations.RunPython.noop),
        migrations.RemoveField(
            model_name='cartitem',
            name='book_id',
        ),
        migrations.RemoveField(
            model_name='cartitem',
            name='book_title',
        ),
        migrations.RemoveField(
            model_name='cartitem',
            name='book_author',
        ),
        migrations.RemoveField(
            model_name='cartitem',
            name='book_cover_url',
        ),
    ]
