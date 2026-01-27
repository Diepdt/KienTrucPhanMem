from django.db import models


class Wishlist(models.Model):
    """
    Wishlist Model - Customer's wishlist for saving books.
    
    Attributes:
        id: Auto-generated primary key
        customer: Foreign key to Customer (One-to-One)
        name: Wishlist name
        is_public: Whether wishlist is public
    """
    customer = models.OneToOneField(
        'store.Customer',
        on_delete=models.CASCADE,
        related_name='wishlist'
    )
    name = models.CharField(max_length=255, default='My Wishlist')
    is_public = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'store_wishlist'
        verbose_name = 'Wishlist'
        verbose_name_plural = 'Wishlists'

    def __str__(self):
        return f"{self.customer.name}'s Wishlist"

    def get_items_count(self):
        """Return the number of items in wishlist."""
        return self.items.count()

    def get_total_value(self):
        """Calculate total value of all items in wishlist."""
        return sum(item.book.price for item in self.items.all())

    def clear(self):
        """Remove all items from wishlist."""
        self.items.all().delete()


class WishlistItem(models.Model):
    """
    WishlistItem Model - An item in customer's wishlist.
    
    Attributes:
        id: Auto-generated primary key
        wishlist: Foreign key to Wishlist
        book: Foreign key to Book
        priority: Priority level (1=high, 2=medium, 3=low)
        notes: Personal notes about the item
    """
    PRIORITY_CHOICES = [
        (1, 'High'),
        (2, 'Medium'),
        (3, 'Low'),
    ]

    wishlist = models.ForeignKey(
        Wishlist,
        on_delete=models.CASCADE,
        related_name='items'
    )
    book = models.ForeignKey(
        'store.Book',
        on_delete=models.CASCADE,
        related_name='wishlist_items'
    )
    priority = models.PositiveIntegerField(choices=PRIORITY_CHOICES, default=2)
    notes = models.TextField(blank=True, null=True)
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'store_wishlist_item'
        verbose_name = 'Wishlist Item'
        verbose_name_plural = 'Wishlist Items'
        unique_together = ['wishlist', 'book']
        ordering = ['priority', '-added_at']

    def __str__(self):
        return f"{self.book.title} in {self.wishlist.customer.name}'s Wishlist"

    def move_to_cart(self):
        """Move this item to customer's cart."""
        from store.models.order.cart import Cart
        from store.models.order.cart_item import CartItem
        
        cart, created = Cart.objects.get_or_create(customer=self.wishlist.customer)
        cart_item, item_created = CartItem.objects.get_or_create(
            cart=cart,
            book=self.book,
            defaults={'quantity': 1}
        )
        if not item_created:
            cart_item.quantity += 1
            cart_item.save()
        self.delete()
        return cart_item
