from django.db import migrations


def backfill_from_legacy_fields(apps, schema_editor):
    OrderItem = apps.get_model('order', 'OrderItem')

    for item in OrderItem.objects.all().iterator():
        changed_fields = []

        legacy_book_id = getattr(item, 'book_id', None)
        legacy_book_title = getattr(item, 'book_title', '')
        legacy_book_author = getattr(item, 'book_author', '')

        if not item.product_id and legacy_book_id:
            item.product_id = legacy_book_id
            changed_fields.append('product_id')

        if not item.product_name and legacy_book_title:
            item.product_name = legacy_book_title
            changed_fields.append('product_name')

        if not item.product_subtitle and legacy_book_author:
            item.product_subtitle = legacy_book_author
            changed_fields.append('product_subtitle')

        if changed_fields:
            item.save(update_fields=changed_fields)


class Migration(migrations.Migration):

    dependencies = [
        ('order', '0002_schema_hotfix'),
    ]

    operations = [
        migrations.RunPython(backfill_from_legacy_fields, reverse_code=migrations.RunPython.noop),
        migrations.RemoveField(
            model_name='orderitem',
            name='book_id',
        ),
        migrations.RemoveField(
            model_name='orderitem',
            name='book_title',
        ),
        migrations.RemoveField(
            model_name='orderitem',
            name='book_author',
        ),
    ]
