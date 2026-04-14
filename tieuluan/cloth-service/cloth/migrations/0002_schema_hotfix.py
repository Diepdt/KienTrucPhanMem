from django.db import migrations


def add_missing_columns(apps, schema_editor):
    table_name = 'cloth_cloth'
    with schema_editor.connection.cursor() as cursor:
        cursor.execute(
            """
            SELECT COLUMN_NAME
            FROM INFORMATION_SCHEMA.COLUMNS
            WHERE TABLE_SCHEMA = DATABASE() AND TABLE_NAME = %s
            """,
            [table_name],
        )
        existing_columns = {row[0] for row in cursor.fetchall()}

        if 'category_id' not in existing_columns:
            cursor.execute(f"ALTER TABLE {table_name} ADD COLUMN category_id INT NULL")

        if 'category_name' not in existing_columns:
            cursor.execute(
                f"ALTER TABLE {table_name} ADD COLUMN category_name VARCHAR(255) NOT NULL DEFAULT ''"
            )

        if 'attributes' not in existing_columns:
            cursor.execute(f"ALTER TABLE {table_name} ADD COLUMN attributes JSON NULL")


def noop_reverse(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('cloth', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(add_missing_columns, reverse_code=noop_reverse),
    ]
