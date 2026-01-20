from django.db import models


class Cart(models.Model):
    """
    Cart Model - Represents a shopping cart for a customer session.
    
    Attributes:
        customer: Foreign key to Customer (optional for guest checkout)
        created_at: Timestamp when cart was created
        updated_at: Timestamp when cart was last updated
    """
    customer = models.ForeignKey(
        'store.Customer',
        on_delete=models.CASCADE,
        related_name='carts',
        null=True,
        blank=True
    )
    session_key = models.CharField(max_length=255, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'store_cart'
        verbose_name = 'Cart'
        verbose_name_plural = 'Carts'

    def __str__(self):
        if self.customer:
            return f"Cart for {self.customer.name}"
        return f"Guest Cart ({self.session_key})"

    def get_total_price(self):
        """Calculate total price of all items in cart."""
        return sum(item.get_subtotal() for item in self.items.all())

    def get_total_items(self):
        """Get total number of items in cart."""
        return sum(item.quantity for item in self.items.all())

    def clear(self):
        """Remove all items from cart."""
        self.items.all().delete()
