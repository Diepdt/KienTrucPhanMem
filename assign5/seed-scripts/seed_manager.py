#!/usr/bin/env python
"""
Seed Manager Account
Creates: manager@gmail.com / 12345678

Usage:
    cd manager-service
    python ../seed-scripts/seed_manager.py
"""

import os
import sys
import django
from pathlib import Path

# Setup Django
sys.path.insert(0, str(Path(__file__).parent.parent / 'manager-service'))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'manager_config.settings')
django.setup()

from manager.models import Manager

def seed_manager_account():
    """Create manager account if it doesn't exist"""
    email = 'manager@gmail.com'
    password = '12345678'
    name = 'Manager Account'
    
    # Check if manager already exists
    if Manager.objects.filter(email=email).exists():
        print(f"✓ Manager account '{email}' already exists")
        manager = Manager.objects.get(email=email)
    else:
        # Create new manager user
        manager = Manager.objects.create(
            name=name,
            email=email,
            is_active=True
        )
        manager.set_password(password)
        manager.save()
        print(f"✓ Manager account created: {email}")
    
    # Verify manager in database
    manager_count = Manager.objects.filter(email=email).count()
    print(f"✓ Manager account verified in database: {manager_count} record(s)")
    return manager

if __name__ == '__main__':
    try:
        manager = seed_manager_account()
        print("\n=== MANAGER ACCOUNT SEED COMPLETE ===")
        print(f"Email: {manager.email}")
        print(f"Name: {manager.name}")
        print("Password: 12345678")
    except Exception as e:
        print(f"✗ Error seeding manager account: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
