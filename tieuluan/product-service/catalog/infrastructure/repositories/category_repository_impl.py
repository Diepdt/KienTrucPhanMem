from catalog.domain.repositories.category_repository import CategoryRepository
from catalog.models import Category


class DjangoCategoryRepository(CategoryRepository):
    def list_root(self, product_type: str = ''):
        queryset = Category.objects.filter(parent=None)
        if product_type:
            queryset = queryset.filter(product_type=product_type)
        return queryset

    def get_by_id(self, category_id: int):
        try:
            return Category.objects.get(pk=category_id)
        except Category.DoesNotExist:
            return None

    def create(self, entity):
        return Category.objects.create(
            name=entity.name,
            product_type=entity.product_type,
            description=entity.description,
            parent=entity.parent,
        )

    def update(self, category, entity):
        category.name = entity.name
        category.product_type = entity.product_type
        category.description = entity.description
        category.parent = entity.parent
        category.save()
        return category

    def delete(self, category):
        category.delete()
