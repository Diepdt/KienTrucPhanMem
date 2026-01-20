from django.db import models


class Address(models.Model):
    """
    Address Model - Represents a customer's address.
    One-to-One relationship with Customer.
    
    Attributes:
        num: House/Building number
        street: Street name
        city: City name
    """
    customer = models.OneToOneField(
        'store.Customer',
        on_delete=models.CASCADE,
        related_name='address'
    )
    num = models.CharField(max_length=50, verbose_name='House Number')
    street = models.CharField(max_length=255, verbose_name='Street')
    city = models.CharField(max_length=100, verbose_name='City')

    class Meta:
        db_table = 'store_address'
        verbose_name = 'Address'
        verbose_name_plural = 'Addresses'

    def __str__(self):
        return f"{self.num} {self.street}, {self.city}"

    def get_full_address(self):
        """Return the full address as a formatted string."""
        return f"{self.num} {self.street}, {self.city}"
