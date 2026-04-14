from catalog.domain.entities import ProductEntity


class ProductApplicationService:
    def __init__(self, repository):
        self.repository = repository

    def list_products(self, query_params):
        filters = {
            'product_type': str(query_params.get('product_type', '')).strip().lower(),
            'category_id': str(query_params.get('category_id', '')).strip(),
            'is_active': str(query_params.get('is_active', '')).strip().lower(),
            'search': str(query_params.get('search', '')).strip(),
            'min_price': str(query_params.get('min_price', '')).strip(),
            'max_price': str(query_params.get('max_price', '')).strip(),
        }
        return self.repository.list(filters)

    def get_product(self, product_id):
        return self.repository.get_by_id(product_id)

    def create_product(self, payload):
        entity = ProductEntity.from_payload(payload)
        return self.repository.create(entity)

    def update_product(self, product_id, payload):
        product = self.repository.get_by_id(product_id)
        if not product:
            return None
        merged = {
            'name': payload.get('name', product.name),
            'product_type': payload.get('product_type', product.product_type),
            'price': payload.get('price', product.price),
            'stock': payload.get('stock', product.stock),
            'category': payload.get('category', product.category),
            'attributes': payload.get('attributes', product.attributes),
            'description': payload.get('description', product.description),
            'image_url': payload.get('image_url', product.image_url),
            'is_active': payload.get('is_active', product.is_active),
            'created_by_staff_id': payload.get('created_by_staff_id', product.created_by_staff_id),
        }
        entity = ProductEntity.from_payload(merged)
        return self.repository.update(product, entity)

    def delete_product(self, product_id):
        product = self.repository.get_by_id(product_id)
        if not product:
            return False
        self.repository.delete(product)
        return True

    def update_inventory(self, items):
        return self.repository.update_inventory(items)
