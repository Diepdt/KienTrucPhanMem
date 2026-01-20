from django.db import models
from django.contrib.auth.hashers import make_password, check_password


class Staff(models.Model):
    """
    Staff Model - Represents a staff member who manages the bookstore.
    
    Attributes:
        id: Auto-generated primary key
        name: Staff member's full name
        email: Unique email address (used for login)
        password: Hashed password for authentication
        role: Staff role (admin, manager, clerk)
    """
    ROLE_CHOICES = [
        ('admin', 'Administrator'),
        ('manager', 'Manager'),
        ('clerk', 'Clerk'),
    ]

    name = models.CharField(max_length=255)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=255)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='clerk')

    class Meta:
        db_table = 'store_staff'
        verbose_name = 'Staff'
        verbose_name_plural = 'Staff Members'

    def __str__(self):
        return f"{self.name} ({self.get_role_display()})"

    def set_password(self, raw_password):
        """Hash and set the staff's password."""
        self.password = make_password(raw_password)

    def verify_password(self, raw_password):
        """Verify the staff's password."""
        return check_password(raw_password, self.password)

    def save(self, *args, **kwargs):
        # Hash password if it's not already hashed
        if self.password and not self.password.startswith('pbkdf2_'):
            self.set_password(self.password)
        super().save(*args, **kwargs)

    def is_admin(self):
        """Check if staff member is an administrator."""
        return self.role == 'admin'

    def is_manager(self):
        """Check if staff member is a manager or higher."""
        return self.role in ['admin', 'manager']

    def can_manage_inventory(self):
        """Check if staff member can manage book inventory."""
        return self.role in ['admin', 'manager', 'clerk']
