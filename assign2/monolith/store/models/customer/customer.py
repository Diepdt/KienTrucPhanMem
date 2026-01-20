from django.db import models
from django.contrib.auth.hashers import make_password, check_password


class Customer(models.Model):
    """
    Customer Model - Represents a customer/user of the bookstore.
    
    Attributes:
        id: Auto-generated primary key
        name: Customer's full name
        email: Unique email address (used for login)
        password: Hashed password for authentication
    """
    name = models.CharField(max_length=255)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=255)

    class Meta:
        db_table = 'store_customer'
        verbose_name = 'Customer'
        verbose_name_plural = 'Customers'

    def __str__(self):
        return self.name

    def set_password(self, raw_password):
        """Hash and set the customer's password."""
        self.password = make_password(raw_password)

    def verify_password(self, raw_password):
        """Verify the customer's password."""
        return check_password(raw_password, self.password)

    def save(self, *args, **kwargs):
        # Hash password if it's not already hashed (simple check)
        if self.password and not self.password.startswith('pbkdf2_'):
            self.set_password(self.password)
        super().save(*args, **kwargs)
