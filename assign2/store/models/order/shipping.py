from django.db import models
from decimal import Decimal


class Shipping(models.Model):
    """
    Shipping Model - Represents shipping options and addresses.
    
    Attributes:
        method: Shipping method type
        address: Shipping address
        city: City name
        postal_code: Postal/ZIP code
        country: Country name
        cost: Shipping cost
    """
    METHOD_CHOICES = [
        ('standard', 'Standard Shipping (5-7 days)'),
        ('express', 'Express Shipping (2-3 days)'),
        ('overnight', 'Overnight Shipping (1 day)'),
    ]

    SHIPPING_COSTS = {
        'standard': Decimal('5.00'),
        'express': Decimal('15.00'),
        'overnight': Decimal('25.00'),
    }

    method = models.CharField(max_length=20, choices=METHOD_CHOICES, default='standard')
    address = models.CharField(max_length=255)
    city = models.CharField(max_length=100)
    postal_code = models.CharField(max_length=20)
    country = models.CharField(max_length=100, default='Vietnam')
    cost = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('5.00'))
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'store_shipping'
        verbose_name = 'Shipping'
        verbose_name_plural = 'Shipping Records'

    def __str__(self):
        return f"{self.get_method_display()} to {self.address}, {self.city}"

    def save(self, *args, **kwargs):
        # Auto-set shipping cost based on method
        if self.method in self.SHIPPING_COSTS:
            self.cost = self.SHIPPING_COSTS[self.method]
        super().save(*args, **kwargs)

    def get_full_address(self):
        """Return formatted full address."""
        return f"{self.address}, {self.city}, {self.postal_code}, {self.country}"
