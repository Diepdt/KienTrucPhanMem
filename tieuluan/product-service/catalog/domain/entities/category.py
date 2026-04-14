from dataclasses import dataclass


@dataclass
class CategoryEntity:
    name: str
    product_type: str
    description: str = ''
    parent: object = None

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

        name = str(payload.get('name', '')).strip()
        if not name:
            raise ValueError('name is required')

        product_type = cls.normalize_product_type(payload.get('product_type', ''))

        return cls(
            name=name,
            product_type=product_type,
            description=str(payload.get('description', '') or ''),
            parent=payload.get('parent'),
        )
