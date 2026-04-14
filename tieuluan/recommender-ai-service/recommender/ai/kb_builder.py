from typing import Dict, List

from django.db import transaction

from recommender.models import KnowledgeDocument

from .product_catalog import fetch_all_products


class KnowledgeBaseBuilder:
    """Build textual knowledge base for RAG retrieval."""

    POLICY_DOCS = [
        {
            "source": "policy",
            "title": "Chinh sach giao hang",
            "content": "Ho tro giao hang toan quoc. Don hang gia tri cao duoc uu tien giao nhanh."
        },
        {
            "source": "policy",
            "title": "Chinh sach thanh toan",
            "content": "Ho tro thanh toan COD, chuyen khoan, the ngan hang va vi dien tu."
        },
        {
            "source": "policy",
            "title": "Chinh sach doi tra",
            "content": "Khach hang co the doi tra trong 30 ngay voi dieu kien san pham con nguyen ven."
        },
    ]

    def _product_doc(self, product: Dict) -> Dict:
        text = (
            f"San pham: {product['name']}. "
            f"Nhom: {product['service_type']}. "
            f"Gia: {product.get('price', 0)}. "
            f"Mo ta: {product.get('description', '')}"
        )
        return {
            "source": "product",
            "service_type": product["service_type"],
            "external_id": str(product["product_id"]),
            "title": product["name"][:255],
            "content": text,
            "metadata": {
                "price": product.get("price", 0),
                "category": product.get("category", product["service_type"]),
            },
        }

    @transaction.atomic
    def rebuild(self) -> Dict:
        KnowledgeDocument.objects.all().delete()

        products = fetch_all_products()
        rows: List[KnowledgeDocument] = [KnowledgeDocument(**self._product_doc(product)) for product in products]
        rows.extend([KnowledgeDocument(**doc) for doc in self.POLICY_DOCS])

        if rows:
            KnowledgeDocument.objects.bulk_create(rows)

        return {
            "documents": len(rows),
            "products": len(products),
            "policies": len(self.POLICY_DOCS),
        }
