from django.db import models


class CartItem(models.Model):
    """
    CartItem Model - Represents an item in a shopping cart.
    
    Attributes:
        cart: Foreign key to Cart
        book: Foreign key to Book
        quantity: Number of this book in the cart
    """
    cart = models.ForeignKey(
        'store.Cart',
        on_delete=models.CASCADE,
        related_name='items'
    )
    book = models.ForeignKey(
        'store.Book',
        on_delete=models.CASCADE,
        related_name='cart_items'
    )
    quantity = models.PositiveIntegerField(default=1)
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'store_cart_item'
        verbose_name = 'Cart Item'
        verbose_name_plural = 'Cart Items'
        unique_together = ['cart', 'book']  # One entry per book per cart

    def __str__(self):
        return f"{self.quantity}x {self.book.title}"

    def get_subtotal(self):
        """Calculate subtotal for this cart item."""
        return self.book.price * self.quantity

    def increase_quantity(self, amount=1):
        """Increase item quantity."""
        self.quantity += amount
        self.save()

    def decrease_quantity(self, amount=1):
        """Decrease item quantity. Removes item if quantity reaches 0."""
        self.quantity -= amount
        if self.quantity <= 0:
            self.delete()
        else:
            self.save()
