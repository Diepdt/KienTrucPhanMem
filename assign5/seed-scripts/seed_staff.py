#!/usr/bin/env python
"""
Seed Staff Account
Creates: staff@gmail.com / 12345678

Usage:
    cd staff-service
    python ../seed-scripts/seed_staff.py
"""

import os
import sys
import django
from pathlib import Path

# Setup Django
sys.path.insert(0, str(Path(__file__).parent.parent / 'staff-service'))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'staff_config.settings')
django.setup()

from staff.models import Staff

def seed_staff_account():
    """Create staff account if it doesn't exist"""
    email = 'staff@gmail.com'
    password = '12345678'
    name = 'Staff Account'
    
    # Check if staff already exists
    if Staff.objects.filter(email=email).exists():
        print(f"✓ Staff account '{email}' already exists")
        staff = Staff.objects.get(email=email)
    else:
        # Create new staff user
        staff = Staff.objects.create(
            name=name,
            email=email,
            role='staff',
            is_active=True
        )
        staff.set_password(password)
        staff.save()
        print(f"✓ Staff account created: {email}")
    
    # Verify staff in database
    staff_count = Staff.objects.filter(email=email).count()
    print(f"✓ Staff account verified in database: {staff_count} record(s)")
    return staff

if __name__ == '__main__':
    try:
        staff = seed_staff_account()
        print("\n=== STAFF ACCOUNT SEED COMPLETE ===")
        print(f"Email: {staff.email}")
        print(f"Name: {staff.name}")
        print("Password: 12345678")
    except Exception as e:
        print(f"✗ Error seeding staff account: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
