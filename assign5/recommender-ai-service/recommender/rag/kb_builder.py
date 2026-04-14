"""
Knowledge Base Builder: Tạo KB từ thông tin sản phẩm các services
"""
import os
import json
import requests
import re
from typing import List, Dict, Tuple
from pathlib import Path
from datetime import datetime

import numpy as np
from sentence_transformers import SentenceTransformer


KB_DIR = Path(__file__).parent / 'knowledge_base'
KB_DIR.mkdir(exist_ok=True)

# Service URLs
SERVICE_URLS = {
    'book': os.getenv('BOOK_SERVICE_URL', 'http://book-service:8000'),
    'laptop': os.getenv('LAPTOP_SERVICE_URL', 'http://laptop-service:8000'),
    'mobile': os.getenv('MOBILE_SERVICE_URL', 'http://mobile-service:8000'),
    'cloth': os.getenv('CLOTH_SERVICE_URL', 'http://cloth-service:8000'),
    'order': os.getenv('ORDER_SERVICE_URL', 'http://order-service:8000'),
    'ship': os.getenv('SHIP_SERVICE_URL', 'http://ship-service:8000'),
    'pay': os.getenv('PAY_SERVICE_URL', 'http://pay-service:8000'),
}

TIMEOUT = 10


class KnowledgeBaseBuilder:
    """Lớp xây dựng Knowledge Base từ thông tin các services"""
    
    def __init__(self):
        # Khởi tạo embedding model
        print("Loading embedding model...")
        self.embedding_model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')
        
        self.documents = []  # List of (text, metadata) tuples
        self.embeddings = None
    
    def fetch_products_from_service(self, service_name: str) -> List[Dict]:
        """Lấy danh sách sản phẩm từ một service"""
        service_url = SERVICE_URLS.get(service_name)
        if not service_url:
            print(f"❌ Unknown service: {service_name}")
            return []
        
        try:
            endpoints = {
                'book': '/api/books/',
                'laptop': '/api/laptops/',
                'mobile': '/api/mobiles/',
                'cloth': '/api/clothes/'
            }
            
            endpoint = endpoints.get(service_name, '/api/')
            response = requests.get(f'{service_url}{endpoint}', timeout=TIMEOUT)
            response.raise_for_status()
            
            data = response.json()
            if isinstance(data, dict) and 'results' in data:
                return data['results']
            return data if isinstance(data, list) else []
        
        except Exception as e:
            print(f"⚠ Error fetching from {service_name}: {e}")
            return []
    
    def fetch_shipping_info(self) -> Dict:
        """Lấy thông tin shipping policy"""
        try:
            response = requests.get(f'{SERVICE_URLS["ship"]}/api/shipping-info/', timeout=TIMEOUT)
            response.raise_for_status()
            return response.json()
        except:
            return {
                'free_shipping_threshold': 500000,
                'standard_shipping_days': '3-5',
                'express_shipping_days': '1-2'
            }
    
    def fetch_payment_info(self) -> Dict:
        """Lấy thông tin payment methods"""
        try:
            response = requests.get(f'{SERVICE_URLS["pay"]}/api/payment-methods/', timeout=TIMEOUT)
            response.raise_for_status()
            return response.json()
        except:
            return {
                'payment_methods': ['Credit Card', 'Debit Card', 'Bank Transfer', 'E-wallet'],
                'installment_available': True
            }
    
    def add_product_documents(self, service_name: str):
        """Thêm documents cho các sản phẩm từ một service"""
        print(f"Fetching products from {service_name}-service...")
        products = self.fetch_products_from_service(service_name)
        
        for product in products:
            # Tạo document text từ thông tin sản phẩm
            doc_text = self._format_product_text(product, service_name)
            
            metadata = {
                'type': 'product',
                'service': service_name,
                'product_id': product.get('id'),
                'name': product.get('name', 'Unknown'),
                'price': product.get('price'),
                'timestamp': datetime.now().isoformat()
            }
            
            self.documents.append((doc_text, metadata))
        
        print(f"✓ Added {len(products)} products from {service_name}")
    
    def _format_product_text(self, product: Dict, service_name: str) -> str:
        """Format product information into readable text"""
        lines = []
        
        # Product info
        name = product.get('name', 'Unnamed Product')
        lines.append(f"Product: {name}")
        lines.append(f"Category: {service_name}")
        
        # Thông tin chi tiết tùy theo loại sản phẩm
        description = product.get('description', '')
        if description:
            # Clean HTML tags if any
            description = re.sub(r'<[^>]+>', '', description)
            lines.append(f"Description: {description[:500]}")
        
        # Price
        price = product.get('price')
        if price:
            try:
                price_float = float(price)
                lines.append(f"Price: {price_float:,.0f} VND")
            except (ValueError, TypeError):
                lines.append(f"Price: {price} VND")
        
        # Specifications
        if 'specs' in product or 'specifications' in product:
            specs = product.get('specs') or product.get('specifications', {})
            if isinstance(specs, dict):
                for key, value in list(specs.items())[:5]:  # Top 5 specs
                    lines.append(f"{key}: {value}")
        
        # Stock
        stock = product.get('stock') or product.get('quantity')
        if stock:
            lines.append(f"Stock: {stock} units available")
        
        # Rating
        rating = product.get('rating') or product.get('average_rating')
        if rating:
            lines.append(f"Rating: {rating}/5.0")
        
        return "\n".join(lines)
    
    def add_service_info_documents(self):
        """Thêm documents về chính sách và thông tin dịch vụ"""
        print("Adding service information documents...")
        
        # Shipping policy
        shipping = self.fetch_shipping_info()
        try:
            threshold = float(shipping.get('free_shipping_threshold', 500000))
            threshold_str = f"{threshold:,.0f}"
        except (ValueError, TypeError):
            threshold_str = str(shipping.get('free_shipping_threshold', 500000))
        
        shipping_text = f"""
Shipping Policy:
- Free shipping orders over {threshold_str} VND
- Standard shipping: {shipping.get('standard_shipping_days', '3-5')} business days
- Express shipping: {shipping.get('express_shipping_days', '1-2')} business days
- We deliver nationwide using reliable logistics partners
        """
        self.documents.append((shipping_text.strip(), {
            'type': 'policy',
            'policy_type': 'shipping',
            'timestamp': datetime.now().isoformat()
        }))
        
        # Payment policy
        payment = self.fetch_payment_info()
        payment_methods = ", ".join(payment.get('payment_methods', []))
        payment_text = f"""
Payment Methods:
- Accepted methods: {payment_methods}
- Installment available: {payment.get('installment_available', False)}
- All transactions are secured with SSL encryption
- No payment fees for standard transactions
        """
        self.documents.append((payment_text.strip(), {
            'type': 'policy',
            'policy_type': 'payment',
            'timestamp': datetime.now().isoformat()
        }))
        
        # General service info
        service_info = """
About Our E-Commerce Platform:
- We offer a wide variety of products: Books, Laptops, Mobiles, and Clothing
- Fast and reliable delivery across the country
- 30-day return policy on most products
- Professional customer support available 24/7
- Quality guarantee on all products
- Competitive prices with frequent promotions
        """
        self.documents.append((service_info.strip(), {
            'type': 'general',
            'timestamp': datetime.now().isoformat()
        }))
        
        print("✓ Added service information documents (3)")
    
    def build_knowledge_base(self):
        """Xây dựng toàn bộ knowledge base"""
        print("\n" + "="*60)
        print("BUILDING KNOWLEDGE BASE")
        print("="*60 + "\n")
        
        # Thêm products từ tất cả services
        for service_name in ['book', 'laptop', 'mobile', 'cloth']:
            self.add_product_documents(service_name)
        
        # Thêm service info
        self.add_service_info_documents()
        
        print(f"\nTotal documents: {len(self.documents)}")
        
        if len(self.documents) == 0:
            print("❌ ERROR: No documents to embed!")
            return False
        
        # Embedding tất cả documents
        print("\nEmbedding documents...")
        texts = [doc[0] for doc in self.documents]
        self.embeddings = self.embedding_model.encode(texts, show_progress_bar=True)
        
        print(f"✓ Embeddings created - Shape: {self.embeddings.shape}")
        
        # Lưu knowledge base
        self.save_knowledge_base()
        
        print("\n" + "="*60)
        print("✓ KNOWLEDGE BASE BUILT SUCCESSFULLY!")
        print("="*60 + "\n")
        
        return True
    
    def save_knowledge_base(self):
        """Lưu knowledge base vào file"""
        # Lưu documents metadata
        documents_meta = []
        for text, metadata in self.documents:
            documents_meta.append({
                'text': text,
                'metadata': metadata
            })
        
        with open(KB_DIR / 'documents.json', 'w', encoding='utf-8') as f:
            json.dump(documents_meta, f, ensure_ascii=False, indent=2)
        
        # Lưu embeddings
        np.save(KB_DIR / 'embeddings.npy', self.embeddings)
        
        print(f"✓ Saved {len(self.documents)} documents to {KB_DIR}")


def build_kb():
    """Tiện lợi function để build KB"""
    builder = KnowledgeBaseBuilder()
    return builder.build_knowledge_base()


if __name__ == '__main__':
    build_kb()
