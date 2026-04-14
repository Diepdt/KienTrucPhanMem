from decimal import Decimal

from django.core.management.base import BaseCommand

from catalog.infrastructure.attributes_store import MongoProductAttributesStore
from catalog.models import Category, Product


DEMO_PRODUCTS = [
    {
        'name': 'Atomic Habits',
        'product_type': 'book',
        'category_name': 'Sach Ky Nang Song',
        'price': Decimal('129000'),
        'stock': 80,
        'description': 'Sach phat trien ban than ban chay toan cau.',
        'image_url': 'https://images.unsplash.com/photo-1512820790803-83ca734da794?q=80&w=1200&auto=format&fit=crop',
        'attributes': {'author': 'James Clear', 'publisher': 'Avery', 'language': 'en'},
    },
    {
        'name': 'Ao Khoac Gio Urban',
        'product_type': 'cloth',
        'category_name': 'Thoi Trang Duong Pho',
        'price': Decimal('599000'),
        'stock': 55,
        'description': 'Ao khoac nhe, can gio va chong mua nhe.',
        'image_url': 'https://images.unsplash.com/photo-1521223890158-f9f7c3d5d504?q=80&w=1200&auto=format&fit=crop',
        'attributes': {'brand': 'CityStyle', 'material': 'polyester', 'size': 'L'},
    },
    {
        'name': 'MacBook Air M2 13',
        'product_type': 'laptop',
        'category_name': 'Laptop Van Phong',
        'price': Decimal('26990000'),
        'stock': 20,
        'description': 'Laptop nhe, pin lau, toi uu cho cong viec.',
        'image_url': 'https://images.unsplash.com/photo-1517336714739-489689fd1ca8?q=80&w=1200&auto=format&fit=crop',
        'attributes': {'brand': 'Apple', 'cpu': 'M2', 'ram': '8GB', 'storage': '256GB SSD'},
    },
    {
        'name': 'Samsung Galaxy S24',
        'product_type': 'mobile',
        'category_name': 'Dien Thoai Cao Cap',
        'price': Decimal('18990000'),
        'stock': 40,
        'description': 'Flagship Android voi AI thong minh.',
        'image_url': 'https://images.unsplash.com/photo-1610945265064-0e34e5519bbf?q=80&w=1200&auto=format&fit=crop',
        'attributes': {'brand': 'Samsung', 'storage': '256GB', 'screen': '6.2 inch', 'battery': '4000mAh'},
    },
    {
        'name': 'iPad Air Gen 6',
        'product_type': 'tablet',
        'category_name': 'May Tinh Bang',
        'price': Decimal('17490000'),
        'stock': 25,
        'description': 'Tablet man hinh dep, phu hop hoc tap va giai tri.',
        'image_url': 'https://images.unsplash.com/photo-1561154464-82e9adf32764?q=80&w=1200&auto=format&fit=crop',
        'attributes': {'brand': 'Apple', 'screen': '11 inch', 'storage': '256GB'},
    },
    {
        'name': 'Galaxy Watch 6',
        'product_type': 'smartwatch',
        'category_name': 'Dong Ho Thong Minh',
        'price': Decimal('6490000'),
        'stock': 30,
        'description': 'Smartwatch theo doi suc khoe va thong bao real-time.',
        'image_url': 'https://images.unsplash.com/photo-1523275335684-37898b6baf30?q=80&w=1200&auto=format&fit=crop',
        'attributes': {'brand': 'Samsung', 'display': 'AMOLED', 'battery': '40h'},
    },
    {
        'name': 'Sony WH-1000XM5',
        'product_type': 'headphone',
        'category_name': 'Tai Nghe',
        'price': Decimal('8490000'),
        'stock': 35,
        'description': 'Tai nghe chong on chu dong cho dan van phong.',
        'image_url': 'https://images.unsplash.com/photo-1505740420928-5e560c06d30e?q=80&w=1200&auto=format&fit=crop',
        'attributes': {'brand': 'Sony', 'type': 'Over-ear', 'connectivity': 'Bluetooth 5.3'},
    },
    {
        'name': 'Canon EOS R50',
        'product_type': 'camera',
        'category_name': 'May Anh Ky Thuat So',
        'price': Decimal('19990000'),
        'stock': 12,
        'description': 'May anh mirrorless nho gon cho creator moi.',
        'image_url': 'https://images.unsplash.com/photo-1516035069371-29a1b244cc32?q=80&w=1200&auto=format&fit=crop',
        'attributes': {'brand': 'Canon', 'sensor': 'APS-C', 'video': '4K'},
    },
    {
        'name': 'Keychron K8 Pro',
        'product_type': 'keyboard',
        'category_name': 'Ban Phim Co',
        'price': Decimal('2890000'),
        'stock': 60,
        'description': 'Ban phim co hot-swap cho lap trinh vien.',
        'image_url': 'https://images.unsplash.com/photo-1511467687858-23d96c32e4ae?q=80&w=1200&auto=format&fit=crop',
        'attributes': {'brand': 'Keychron', 'layout': 'TKL', 'switch': 'Gateron Brown'},
    },
    {
        'name': 'Logitech MX Master 3S',
        'product_type': 'mouse',
        'category_name': 'Chuot Khong Day',
        'price': Decimal('2490000'),
        'stock': 75,
        'description': 'Chuot cong thai hoc cho nang suat lam viec cao.',
        'image_url': 'https://images.unsplash.com/photo-1527864550417-7fd91fc51a46?q=80&w=1200&auto=format&fit=crop',
        'attributes': {'brand': 'Logitech', 'dpi': '8000', 'connectivity': 'Bluetooth'},
    },
    {
        'name': 'LG UltraFine 27 inch 4K',
        'product_type': 'monitor',
        'category_name': 'Man Hinh Do Hoa',
        'price': Decimal('10990000'),
        'stock': 28,
        'description': 'Man hinh 4K sac net cho thiet ke va edit video.',
        'image_url': 'https://images.unsplash.com/photo-1527443224154-c4a3942d3acf?q=80&w=1200&auto=format&fit=crop',
        'attributes': {'brand': 'LG', 'resolution': '4K', 'size': '27 inch'},
    },
    {
        'name': 'JBL Charge 5',
        'product_type': 'speaker',
        'category_name': 'Loa Bluetooth',
        'price': Decimal('3490000'),
        'stock': 42,
        'description': 'Loa di dong am thanh manh me, chong nuoc IP67.',
        'image_url': 'https://images.unsplash.com/photo-1545454675-3531b543be5d?q=80&w=1200&auto=format&fit=crop',
        'attributes': {'brand': 'JBL', 'battery': '20h', 'waterproof': 'IP67'},
    },
]


class Command(BaseCommand):
    help = 'Seed 12 demo products and categories for unified product-service.'

    def add_arguments(self, parser):
        parser.add_argument(
            '--reset',
            action='store_true',
            help='Delete existing products/categories and reseed from scratch.',
        )

    def handle(self, *args, **options):
        attributes_store = MongoProductAttributesStore()
        reset_mode = bool(options.get('reset'))

        if reset_mode:
            existing_ids = list(Product.objects.values_list('id', flat=True))
            Product.objects.all().delete()
            Category.objects.all().delete()
            attributes_store.delete_many(existing_ids)
            self.stdout.write(self.style.WARNING('Reset mode: cleared existing products/categories.'))

        created_products = 0
        updated_products = 0

        for item in DEMO_PRODUCTS:
            category, _ = Category.objects.get_or_create(
                name=item['category_name'],
                product_type=item['product_type'],
                defaults={'description': f"Danh muc {item['category_name']}"},
            )

            product, created = Product.objects.get_or_create(
                name=item['name'],
                product_type=item['product_type'],
                defaults={
                    'category': category,
                    'price': item['price'],
                    'stock': item['stock'],
                    'attributes': item['attributes'],
                    'description': item['description'],
                    'image_url': item['image_url'],
                    'is_active': True,
                },
            )

            if created:
                created_products += 1
            else:
                product.category = category
                product.price = item['price']
                product.stock = item['stock']
                product.attributes = item['attributes']
                product.description = item['description']
                product.image_url = item['image_url']
                product.is_active = True
                product.save()
                updated_products += 1

            attributes_store.upsert(product.id, item['attributes'])

        total_products = Product.objects.count()
        total_categories = Category.objects.count()

        self.stdout.write(self.style.SUCCESS(
            f'Seed completed: created={created_products}, updated={updated_products}, '
            f'total_products={total_products}, total_categories={total_categories}'
        ))
