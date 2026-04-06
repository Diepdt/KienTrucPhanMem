#!/usr/bin/env python
"""
Seed Customer Account
Creates: customer@gmail.com / 12345678

Usage:
    cd customer-service
    python ../seed-scripts/seed_customer.py
"""

import os
import sys
import django
from pathlib import Path

# Setup Django
sys.path.insert(0, str(Path(__file__).parent.parent / 'customer-service'))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'customer_config.settings')
django.setup()

from customer.models import Customer

def seed_customer_account():
    """Create customer account if it doesn't exist"""
    email = 'customer@gmail.com'
    password = '12345678'
    name = 'Customer Account'
    
    # Check if customer already exists
    if Customer.objects.filter(email=email).exists():
        print(f"✓ Customer account '{email}' already exists")
        customer = Customer.objects.get(email=email)
    else:
        # Create new customer user
        customer = Customer.objects.create(
            name=name,
            email=email,
            is_active=True
        )
        customer.set_password(password)
        customer.save()
        print(f"✓ Customer account created: {email}")
    
    # Verify customer in database
    customer_count = Customer.objects.filter(email=email).count()
    print(f"✓ Customer account verified in database: {customer_count} record(s)")
    return customer

if __name__ == '__main__':
    try:
        customer = seed_customer_account()
        print("\n=== CUSTOMER ACCOUNT SEED COMPLETE ===")
        print(f"Email: {customer.email}")
        print(f"Name: {customer.name}")
        print("Password: 12345678")
    except Exception as e:
        print(f"✗ Error seeding customer account: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
