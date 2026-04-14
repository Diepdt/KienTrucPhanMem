from dataclasses import dataclass, field


@dataclass
class ProductEntity:
    name: str
    product_type: str
    price: float
    stock: int
    category: object = None
    attributes: dict = field(default_factory=dict)
    description: str = ''
    image_url: str = ''
    is_active: bool = True
    created_by_staff_id: int | None = None

    @staticmethod
    def normalize_product_type(value: str) -> str:
        normalized = str(value or '').strip().lower().replace(' ', '_')
        if not normalized:
            raise ValueError('product_type is required')
        for char in normalized:
            if not (char.isalnum() or char in {'_', '-'}):
                raise ValueError('product_type contains invalid characters')
        return normalized

    @classmethod
    def from_payload(cls, payload: dict):
        if not isinstance(payload, dict):
            raise ValueError('payload must be a dict')

        product_type = cls.normalize_product_type(payload.get('product_type', ''))
        name = str(payload.get('name', '')).strip()
        if not name:
            raise ValueError('name is required')

        price = float(payload.get('price', 0))
        if price <= 0:
            raise ValueError('price must be greater than 0')

        stock = int(payload.get('stock', 0))
        if stock < 0:
            raise ValueError('stock cannot be negative')

        attributes = payload.get('attributes') or {}
        if not isinstance(attributes, dict):
            raise ValueError('attributes must be a JSON object')

        return cls(
            name=name,
            product_type=product_type,
            price=price,
            stock=stock,
            category=payload.get('category'),
            attributes=attributes,
            description=str(payload.get('description', '') or ''),
            image_url=str(payload.get('image_url', '') or ''),
            is_active=bool(payload.get('is_active', True)),
            created_by_staff_id=payload.get('created_by_staff_id'),
        )
