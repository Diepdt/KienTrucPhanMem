from django.db import transaction
from django.db.models import F
from typing import Dict, List

from catalog.domain.repositories import ProductRepository
from catalog.models import Product


class DjangoProductRepository(ProductRepository):
    def list(self, filters: dict):
        queryset = Product.objects.select_related('category').all().order_by('-created_at')

        product_type = filters.get('product_type')
        category_id = filters.get('category_id')
        is_active = filters.get('is_active')
        search = filters.get('search')
        min_price = filters.get('min_price')
        max_price = filters.get('max_price')

        if product_type:
            queryset = queryset.filter(product_type=product_type)

        if str(category_id).isdigit():
            queryset = queryset.filter(category_id=int(category_id))

        if is_active in {'true', '1'}:
            queryset = queryset.filter(is_active=True)
        elif is_active in {'false', '0'}:
            queryset = queryset.filter(is_active=False)

        if search:
            queryset = queryset.filter(name__icontains=search)

        if min_price:
            try:
                queryset = queryset.filter(price__gte=float(min_price))
            except ValueError:
                pass

        if max_price:
            try:
                queryset = queryset.filter(price__lte=float(max_price))
            except ValueError:
                pass

        return queryset

    def get_by_id(self, product_id: int):
        try:
            return Product.objects.select_related('category').get(pk=product_id)
        except Product.DoesNotExist:
            return None

    def create(self, entity):
        return Product.objects.create(
            name=entity.name,
            product_type=entity.product_type,
            category=entity.category,
            price=entity.price,
            stock=entity.stock,
            attributes=entity.attributes,
            description=entity.description,
            image_url=entity.image_url,
            is_active=entity.is_active,
            created_by_staff_id=entity.created_by_staff_id,
        )

    def update(self, product, entity):
        product.name = entity.name
        product.product_type = entity.product_type
        product.category = entity.category
        product.price = entity.price
        product.stock = entity.stock
        product.attributes = entity.attributes
        product.description = entity.description
        product.image_url = entity.image_url
        product.is_active = entity.is_active
        product.created_by_staff_id = entity.created_by_staff_id
        product.save()
        return product

    def delete(self, product):
        product.delete()

    def update_inventory(self, items: List[Dict]):
        errors = []
        updated = []

        with transaction.atomic():
            for item in items:
                try:
                    product_id = int(item.get('product_id'))
                    quantity = int(item.get('quantity'))
                    product_type = str(item.get('product_type', '')).strip().lower()
                except (TypeError, ValueError):
                    errors.append({'item': item, 'error': 'Invalid payload'})
                    continue

                if product_id <= 0 or quantity <= 0:
                    errors.append({'item': item, 'error': 'product_id and quantity must be greater than 0'})
                    continue

                try:
                    product = Product.objects.select_for_update().get(pk=product_id)
                except Product.DoesNotExist:
                    errors.append({'product_id': product_id, 'error': 'Product not found'})
                    continue

                if product_type and product.product_type != product_type:
                    errors.append({
                        'product_id': product_id,
                        'error': 'product_type mismatch',
                        'expected': product.product_type,
                        'provided': product_type,
                    })
                    continue

                if product.stock < quantity:
                    errors.append({
                        'product_id': product_id,
                        'error': 'Insufficient stock',
                        'available': product.stock,
                        'requested': quantity,
                    })
                    continue

                Product.objects.filter(pk=product.pk).update(stock=F('stock') - quantity)
                updated.append({'product_id': product.pk, 'deducted': quantity})

            if errors:
                transaction.set_rollback(True)

        return {'success': len(errors) == 0, 'updated': updated, 'errors': errors}
