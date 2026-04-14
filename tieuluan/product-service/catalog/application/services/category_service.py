from catalog.domain.entities.category import CategoryEntity


class CategoryApplicationService:
    def __init__(self, repository):
        self.repository = repository

    def list_categories(self, query_params):
        product_type = str(query_params.get('product_type', '')).strip().lower()
        return self.repository.list_root(product_type=product_type)

    def get_category(self, category_id):
        return self.repository.get_by_id(category_id)

    def create_category(self, payload):
        entity = CategoryEntity.from_payload(payload)
        return self.repository.create(entity)

    def update_category(self, category_id, payload):
        category = self.repository.get_by_id(category_id)
        if not category:
            return None

        merged = {
            'name': payload.get('name', category.name),
            'product_type': payload.get('product_type', category.product_type),
            'description': payload.get('description', category.description),
            'parent': payload.get('parent', category.parent),
        }
        entity = CategoryEntity.from_payload(merged)
        return self.repository.update(category, entity)

    def delete_category(self, category_id):
        category = self.repository.get_by_id(category_id)
        if not category:
            return False
        self.repository.delete(category)
        return True
