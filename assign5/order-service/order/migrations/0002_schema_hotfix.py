from django.db import migrations
from django.db.utils import OperationalError


def _safe_add_column(cursor, sql):
    try:
        cursor.execute(sql)
    except OperationalError as exc:
        # MySQL duplicate column error code.
        if exc.args and exc.args[0] == 1060:
            return
        raise


def reconcile_orderitem_schema(apps, schema_editor):
    table_name = 'order_orderitem'
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

        if 'product_type' not in existing_columns:
            cursor.execute(
                f"ALTER TABLE {table_name} ADD COLUMN product_type VARCHAR(50) NOT NULL DEFAULT 'book'"
            )
        else:
            cursor.execute(
                f"ALTER TABLE {table_name} MODIFY COLUMN product_type VARCHAR(50) NOT NULL DEFAULT 'book'"
            )

        if 'product_id' not in existing_columns:
            _safe_add_column(cursor, f"ALTER TABLE {table_name} ADD COLUMN product_id INT NULL")

        if 'product_name' not in existing_columns:
            _safe_add_column(
                cursor,
                f"ALTER TABLE {table_name} ADD COLUMN product_name VARCHAR(255) NOT NULL DEFAULT ''"
            )

        if 'product_subtitle' not in existing_columns:
            _safe_add_column(
                cursor,
                f"ALTER TABLE {table_name} ADD COLUMN product_subtitle VARCHAR(255) NOT NULL DEFAULT ''"
            )

        if 'product_image_url' not in existing_columns:
            _safe_add_column(
                cursor,
                f"ALTER TABLE {table_name} ADD COLUMN product_image_url VARCHAR(200) NOT NULL DEFAULT ''"
            )

        if 'product_snapshot' not in existing_columns:
            _safe_add_column(cursor, f"ALTER TABLE {table_name} ADD COLUMN product_snapshot JSON NULL")

        if 'book_id' in existing_columns:
            cursor.execute(f"ALTER TABLE {table_name} MODIFY COLUMN book_id INT NULL")

        cursor.execute(
            f"""
            UPDATE {table_name}
            SET product_id = CASE
                    WHEN product_id IS NULL OR product_id = 0 THEN book_id
                    ELSE product_id
                END,
                product_name = CASE
                    WHEN product_name = '' THEN COALESCE(book_title, '')
                    ELSE product_name
                END,
                product_subtitle = CASE
                    WHEN product_subtitle = '' THEN COALESCE(book_author, '')
                    ELSE product_subtitle
                END
            """
        )

        if 'product_brand' in existing_columns:
            cursor.execute(
                f"UPDATE {table_name} SET product_subtitle = product_brand WHERE product_subtitle = '' AND product_brand <> ''"
            )


def noop_reverse(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('order', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(reconcile_orderitem_schema, reverse_code=noop_reverse),
    ]
