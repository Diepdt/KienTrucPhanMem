#!/usr/bin/env python
"""
Seed Categories for All Product Types
Creates categories for: Book, Cloth, Laptop, Mobile

Usage:
    cd catalog-service
    python ../seed-scripts/seed_categories.py
"""

import os
import sys
import django
from pathlib import Path

# Setup Django
sys.path.insert(0, str(Path(__file__).parent.parent / 'catalog-service'))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'catalog_config.settings')
django.setup()

from catalog.models import Category

CATEGORIES_DATA = {
    'book': [
        {'name': 'Tâm linh', 'description': 'Sách về phát triển tâm linh'},
        {'name': 'Tâm lý học', 'description': 'Sách về tâm lý học'},
        {'name': 'Tài chính', 'description': 'Sách về tài chính cá nhân'},
        {'name': 'Phát triển bản thân', 'description': 'Sách về phát triển kỹ năng cá nhân'},
    ],
    'cloth': [
        {'name': 'Áo sơ mi', 'description': 'Áo sơ mi nam và nữ'},
        {'name': 'Sweater', 'description': 'Áo len và sweater'},
        {'name': 'Quần âu', 'description': 'Quần tây và quần âu'},
    ],
    'laptop': [
        {'name': 'Gaming', 'description': 'Laptop chơi game'},
        {'name': 'Văn phòng', 'description': 'Laptop dùng cho công việc văn phòng'},
        {'name': 'Thiết kế', 'description': 'Laptop chuyên dụng cho thiết kế'},
        {'name': 'Ultrabook', 'description': 'Laptop mỏng nhẹ tính năng cao'},
    ],
    'mobile': [
        {'name': 'Smartphone', 'description': 'Điện thoại thông minh'},
        {'name': 'Flagship', 'description': 'Điện thoại cao cấp'},
        {'name': 'Mid-range', 'description': 'Điện thoại tầm trung'},
        {'name': 'Budget', 'description': 'Điện thoại giá rẻ'},
    ],
}

def seed_categories():
    """Create categories for all product types"""
    created_count = 0
    skipped_count = 0
    
    for product_type, categories in CATEGORIES_DATA.items():
        print(f"\n📦 Processing {product_type.upper()} categories:")
        
        for cat_data in categories:
            # Check if category already exists
            exists = Category.objects.filter(
                name=cat_data['name'],
                product_type=product_type
            ).exists()
            
            if exists:
                print(f"  ⊘ {cat_data['name']} (already exists)")
                skipped_count += 1
            else:
                # Create new category
                Category.objects.create(
                    name=cat_data['name'],
                    description=cat_data['description'],
                    product_type=product_type
                )
                print(f"  ✓ {cat_data['name']}")
                created_count += 1
    
    return created_count, skipped_count

if __name__ == '__main__':
    try:
        created, skipped = seed_categories()
        print("\n" + "="*50)
        print("=== CATEGORIES SEED COMPLETE ===")
        print(f"Created: {created} categories")
        print(f"Skipped: {skipped} categories (already exist)")
        print(f"Total: {created + skipped} categories")
    except Exception as e:
        print(f"✗ Error seeding categories: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
