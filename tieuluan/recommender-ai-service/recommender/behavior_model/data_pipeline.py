"""
Data Pipeline: Lấy dữ liệu từ các services (Order, Cart) để huấn luyện Behavior Model
"""
import os
import json
import requests
import pandas as pd
import numpy as np
from typing import List, Dict, Tuple
from datetime import datetime, timedelta

# API endpoints của các services
CUSTOMER_SERVICE_URL = os.getenv('CUSTOMER_SERVICE_URL', 'http://customer-service:8000')
ORDER_SERVICE_URL = os.getenv('ORDER_SERVICE_URL', 'http://order-service:8000')
CART_SERVICE_URL = os.getenv('CART_SERVICE_URL', 'http://cart-service:8000')
PRODUCT_SERVICE_URL = os.getenv('PRODUCT_SERVICE_URL', 'http://product-service:8004')

# Timeout cho requests
TIMEOUT = 10


class DataPipeline:
    """Lớp xử lý pipeline lấy dữ liệu từ các services để training model"""
    
    def __init__(self):
        self.customer_id_map = {}  # Mapping: customer_id -> embedding_index
        self.item_id_map = {}      # Mapping: item_id (across all services) -> embedding_index
        self.interactions = []     # List of (user_id, item_id, rating/interaction_score)
        
    def fetch_customers(self) -> List[Dict]:
        """Lấy danh sách khách hàng từ customer-service"""
        try:
            response = requests.get(
                f'{CUSTOMER_SERVICE_URL}/api/customers/',
                timeout=TIMEOUT
            )
            response.raise_for_status()
            customers = response.json()
            if isinstance(customers, dict) and 'results' in customers:
                return customers['results']
            return customers if isinstance(customers, list) else []
        except Exception as e:
            print(f"Error fetching customers: {e}")
            return []
    
    def fetch_orders(self) -> List[Dict]:
        """Lấy danh sách đơn hàng từ order-service"""
        try:
            response = requests.get(
                f'{ORDER_SERVICE_URL}/api/orders/',
                timeout=TIMEOUT
            )
            response.raise_for_status()
            orders = response.json()
            if isinstance(orders, dict) and 'results' in orders:
                return orders['results']
            return orders if isinstance(orders, list) else []
        except Exception as e:
            print(f"Error fetching orders: {e}")
            return []
    
    def fetch_cart_items(self) -> List[Dict]:
        """Lấy danh sách các item trong giỏ hàng (dấu hiệu quan tâm)"""
        try:
            response = requests.get(
                f'{CART_SERVICE_URL}/api/carts/',
                timeout=TIMEOUT
            )
            response.raise_for_status()
            carts = response.json()
            if isinstance(carts, dict) and 'results' in carts:
                return carts['results']
            return carts if isinstance(carts, list) else []
        except Exception as e:
            print(f"Error fetching carts: {e}")
            return []
    
    def fetch_products_from_service(self, service_name: str) -> List[Dict]:
        """Lấy danh sách sản phẩm từ product-service theo product_type."""
        try:
            endpoints = {
                'book': '/api/products/?product_type=book',
                'laptop': '/api/products/?product_type=laptop',
                'mobile': '/api/products/?product_type=mobile',
                'cloth': '/api/products/?product_type=cloth'
            }
            endpoint = endpoints.get(service_name, '/api/')
            
            response = requests.get(
                f'{PRODUCT_SERVICE_URL}{endpoint}',
                timeout=TIMEOUT
            )
            response.raise_for_status()
            items = response.json()
            if isinstance(items, dict) and 'results' in items:
                return items['results']
            return items if isinstance(items, list) else []
        except Exception as e:
            print(f"Error fetching products from {service_name}: {e}")
            return []
    
    def build_id_mappings(self, customers: List[Dict], products_by_service: Dict):
        """Xây dựng mapping từ thực tế ID sang sequential ID cho embeddings"""
        # Map customers
        for idx, customer in enumerate(customers):
            customer_id = customer.get('id') or customer.get('customer_id')
            if customer_id:
                self.customer_id_map[customer_id] = idx
        
        # Map products từ tất cả services
        item_idx = 0
        for service_name, products in products_by_service.items():
            for product in products:
                product_id = product.get('id') or product.get('product_id')
                if product_id:
                    # Tạo unique key kết hợp service_name + product_id
                    unique_key = f"{service_name}_{product_id}"
                    self.item_id_map[unique_key] = item_idx
                    item_idx += 1
    
    def extract_interactions_from_orders(self, orders: List[Dict]):
        """
        Trích xuất interactions từ lịch sử mua hàng
        Rating: 1.0 (mua thành công)
        """
        for order in orders:
            customer_id = order.get('customer_id')
            items = order.get('items', [])
            
            if customer_id in self.customer_id_map:
                user_idx = self.customer_id_map[customer_id]
                
                for item in items:
                    # Item có thể là object hoặc ID tùy theo API response
                    if isinstance(item, dict):
                        product_id = item.get('product_id') or item.get('id')
                        service_type = item.get('service_type', 'book').lower()
                    else:
                        product_id = item
                        service_type = 'book'  # Default
                    
                    if product_id:
                        unique_key = f"{service_type}_{product_id}"
                        if unique_key in self.item_id_map:
                            item_idx = self.item_id_map[unique_key]
                            # Rating = 1.0 cho việc mua hàng thành công
                            self.interactions.append((user_idx, item_idx, 1.0))
    
    def extract_interactions_from_carts(self, carts: List[Dict]):
        """
        Trích xuất interactions từ giỏ hàng
        Rating: 0.5 (chưa mua, nhưng có quan tâm)
        """
        for cart in carts:
            customer_id = cart.get('customer_id')
            items = cart.get('items', [])
            
            if customer_id in self.customer_id_map:
                user_idx = self.customer_id_map[customer_id]
                
                for item in items:
                    if isinstance(item, dict):
                        product_id = item.get('product_id') or item.get('id')
                        service_type = item.get('service_type', 'book').lower()
                    else:
                        product_id = item
                        service_type = 'book'
                    
                    if product_id:
                        unique_key = f"{service_type}_{product_id}"
                        if unique_key in self.item_id_map:
                            item_idx = self.item_id_map[unique_key]
                            # Rating = 0.5 cho việc add to cart (quan tâm nhưng chưa mua)
                            self.interactions.append((user_idx, item_idx, 0.5))
    
    def process_pipeline(self) -> Tuple[np.ndarray, int, int]:
        """
        Chạy toàn bộ pipeline và trả về dữ liệu sẵn sàng cho training
        
        Returns:
            - interactions_matrix: numpy array shape (num_interactions, 3) - [user_id, item_id, rating]
            - num_users: số lượng khách hàng
            - num_items: số lượng sản phẩm
        """
        print("[1/5] Fetching customers...")
        customers = self.fetch_customers()
        print(f"  ✓ Got {len(customers)} customers")
        
        print("[2/5] Fetching products from all services...")
        products_by_service = {}
        for service_name in ['book', 'laptop', 'mobile', 'cloth']:
            products = self.fetch_products_from_service(service_name)
            products_by_service[service_name] = products
            print(f"  ✓ Got {len(products)} products from product-service ({service_name})")
        
        print("[3/5] Building ID mappings...")
        self.build_id_mappings(customers, products_by_service)
        print(f"  ✓ Mapped {len(self.customer_id_map)} users and {len(self.item_id_map)} items")
        
        print("[4/5] Extracting interactions from orders & carts...")
        orders = self.fetch_orders()
        self.extract_interactions_from_orders(orders)
        print(f"  ✓ Extracted {len(self.interactions)} interactions from orders")
        
        carts = self.fetch_cart_items()
        self.extract_interactions_from_carts(carts)
        print(f"  ✓ Now have total {len(self.interactions)} interactions (including carts)")
        
        print("[5/5] Converting to numpy array...")
        if len(self.interactions) == 0:
            print("  ⚠ WARNING: No interactions found! Model training may fail.")
            return np.array([]).reshape(0, 3), len(self.customer_id_map), len(self.item_id_map)
        
        interactions_matrix = np.array(self.interactions)
        print(f"  ✓ Created matrix shape: {interactions_matrix.shape}")
        
        return interactions_matrix, len(self.customer_id_map), len(self.item_id_map)


def get_data_for_training() -> Tuple[np.ndarray, int, int, DataPipeline]:
    """Công cụ tiện lợi để lấy dữ liệu training"""
    pipeline = DataPipeline()
    interactions, num_users, num_items = pipeline.process_pipeline()
    
    print("\n" + "="*50)
    print("DATA PIPELINE SUMMARY")
    print("="*50)
    print(f"Total Users (Customers): {num_users}")
    print(f"Total Items (Products): {num_items}")
    print(f"Total Interactions: {len(interactions)}")
    if num_users > 0 and num_items > 0:
        sparsity = 1 - (len(interactions) / (num_users * num_items))
        print(f"Matrix Sparsity: {sparsity:.2%}")
    print("="*50 + "\n")
    
    return interactions, num_users, num_items, pipeline
