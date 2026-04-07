import os
import sys
import time
import requests
import random

GATEWAY_URL = "http://localhost:8000"

def run_seed():
    print("==================================================")
    print("      SEEDING CUSTOMERS & INTERACTIONS            ")
    print("==================================================")
    
    # 1. Fetch available products
    print("\n[1/4] Fetching available products...")
    products = {}
    type_map = {
        'books': 'book',
        'clothes': 'cloth'
    }
    for ptype, service_type in type_map.items():
        resp = requests.get(f"{GATEWAY_URL}/api/{ptype}/")
        if resp.status_code == 200:
            data = resp.json()
            items = data.get('results', data) if isinstance(data, dict) else data
            products[service_type] = items
            print(f"  ✓ Got {len(items)} {ptype}")
        else:
            print(f"  ⚠ Failed to get {ptype}: {resp.status_code}")
            products[service_type] = []
            
    total_products = sum(len(items) for items in products.values())
    if total_products == 0:
        print("❌ No products available in the system! Cannot create interactions.")
        sys.exit(1)
        
    all_products = []
    for ptype, items in products.items():
        for item in items:
            all_products.append({'type': ptype, 'id': item['id'], 'stock': item.get('stock', 10)})
    
    # 2. Create fake users
    print("\n[2/4] Registering test customers...")
    customers = []
    
    # Optional: ensure basic customer
    requests.post(f"{GATEWAY_URL}/api/customers/register/", json={
        'name': 'Customer Account', 'email': 'customer@gmail.com', 'password': 'password123'
    })
    
    # Login as default customer if possible, or use the newly generated tokens
    for i in range(1, 10):
        email = f"user{i}@example.com"
        resp = requests.post(f"{GATEWAY_URL}/api/customers/register/", json={
            'name': f'Test User {i}',
            'email': email,
            'password': 'password123'
        })
        
        if resp.status_code in [201]:
            data = resp.json()
            customers.append({
                'id': data['customer']['id'],
                'token': data['token'],
                'email': email
            })
            print(f"  ✓ Created user {email}")
        else:
            # Maybe already exists, try to login
            login_resp = requests.post(f"{GATEWAY_URL}/api/customers/login/", json={
                'email': email, 'password': 'password123'
            })
            if login_resp.status_code == 200:
                data = login_resp.json()
                customers.append({
                    'id': data['customer']['id'],
                    'token': data['token'],
                    'email': email
                })
                print(f"  ✓ Logged in user {email}")
            else:
                print(f"  ⚠ Failed to register/login user {email}: {resp.status_code} - {login_resp.status_code}")
                
    if not customers:
        print("❌ No customers available for interaction seeding!")
        sys.exit(1)

    print(f"\n[3/4] Adding items to carts & creating orders...")
    total_orders = 0
    total_cart_items = 0
    
    # Get shipping methods and payment methods if needed, use static ones if we can't
    # Actually order creation just expects any integer for now
    
    for customer in customers:
        token = customer['token']
        headers = {'Authorization': f"Token {token}"}
        
        # Determine how many items to buy
        num_items = random.randint(1, 4)
        selected = random.sample(all_products, min(num_items, len(all_products)))
        
        # Add to cart
        for item in selected:
            qty = random.randint(1, 2)
            # Make sure we don't try to buy more than stock
            if qty > item['stock']: qty = item['stock']
            if qty <= 0: continue
            
            cart_resp = requests.post(f"{GATEWAY_URL}/api/carts/add/", json={
                'product_type': item['type'],
                'product_id': item['id'],
                'quantity': qty
            }, headers=headers)
            
            if cart_resp.status_code in [200, 201]:
                total_cart_items += 1
            else:
                print(f"  ⚠ Failed to add {item['type']} {item['id']}: {cart_resp.text}")
                
        # 50% chance to checkout and turn cart into an order
        if random.random() > 0.3:
            order_resp = requests.post(f"{GATEWAY_URL}/api/orders/create/", json={
                "shipping_method_id": 1,
                "payment_method_id": 1,
                "shipping_address": f"{random.randint(1, 100)} Main St",
                "notes": "Fast delivery please"
            }, headers=headers)
            
            if order_resp.status_code in [200, 201]:
                total_orders += 1
                print(f"  ✓ Created order for {customer['email']}")
            else:
                print(f"  ⚠ Failed to create order: {order_resp.text}")
                # Clear cart so it doesn't fail next time maybe
                requests.post(f"{GATEWAY_URL}/api/carts/{customer['id']}/clear/", headers=headers)
        
    print("\n[4/4] Summary")
    print(f"  ✓ Created {total_cart_items} valid cart item interactions")
    print(f"  ✓ Checked out {total_orders} orders")
    print("\n✓ Interaction seeding complete! The behavior model now has data to train on.")


if __name__ == "__main__":
    run_seed()