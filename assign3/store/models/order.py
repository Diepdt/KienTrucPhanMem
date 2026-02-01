"""
Order Models - All sales and order related models.
Contains: Cart, CartItem, Order, OrderItem, OrderStatusHistory, 
         Wishlist, WishlistItem, Review, Rating
"""
from django.db import models
from decimal import Decimal
from store.models.base import TimeStampedModel


class Cart(TimeStampedModel):
    """
    Cart Model - Shopping cart for customers.
    """
    customer = models.OneToOneField(
        'store.Customer',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='cart'
    )
    guest_session = models.OneToOneField(
        'store.GuestSession',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='cart'
    )
    coupon = models.ForeignKey(
        'store.Coupon',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='carts'
    )

    class Meta:
        db_table = 'store_cart'
        verbose_name = 'Cart'
        verbose_name_plural = 'Carts'

    def __str__(self):
        if self.customer:
            return f"Cart of {self.customer.name}"
        return f"Guest Cart {self.id}"

    def get_total_items(self):
        """Get total number of items in cart."""
        return sum(item.quantity for item in self.items.all())

    def get_subtotal(self):
        """Calculate cart subtotal."""
        return sum(item.get_subtotal() for item in self.items.all())

    def get_discount(self):
        """Calculate discount amount."""
        if self.coupon and self.coupon.is_valid():
            return self.coupon.calculate_discount(self.get_subtotal())
        return Decimal('0')

    def get_total(self):
        """Calculate cart total after discount."""
        return self.get_subtotal() - self.get_discount()

    def clear(self):
        """Clear all items from cart."""
        self.items.all().delete()


class CartItem(TimeStampedModel):
    """
    Cart Item Model - Individual items in a shopping cart.
    """
    cart = models.ForeignKey(
        Cart,
        on_delete=models.CASCADE,
        related_name='items'
    )
    book = models.ForeignKey(
        'store.Book',
        on_delete=models.CASCADE,
        related_name='cart_items'
    )
    quantity = models.PositiveIntegerField(default=1)
    price_at_add = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        db_table = 'store_cart_item'
        verbose_name = 'Cart Item'
        verbose_name_plural = 'Cart Items'
        unique_together = ['cart', 'book']

    def __str__(self):
        return f"{self.book.title} x {self.quantity}"

    def get_subtotal(self):
        """Calculate item subtotal."""
        return self.price_at_add * self.quantity

    def save(self, *args, **kwargs):
        if not self.price_at_add:
            self.price_at_add = self.book.price
        super().save(*args, **kwargs)


class Order(TimeStampedModel):
    """
    Order Model - Represents a customer order.
    """
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('processing', 'Processing'),
        ('shipped', 'Shipped'),
        ('delivered', 'Delivered'),
        ('cancelled', 'Cancelled'),
        ('refunded', 'Refunded'),
    ]

    order_number = models.CharField(max_length=50, unique=True)
    customer = models.ForeignKey(
        'store.Customer',
        on_delete=models.CASCADE,
        related_name='orders'
    )
    shipping_address = models.ForeignKey(
        'store.Address',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='shipping_orders'
    )
    billing_address = models.ForeignKey(
        'store.Address',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='billing_orders'
    )
    staff = models.ForeignKey(
        'store.Staff',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='processed_orders'
    )
    coupon = models.ForeignKey(
        'store.Coupon',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='orders'
    )
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    subtotal = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    discount_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    tax_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    shipping_cost = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    total = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    notes = models.TextField(blank=True, null=True)
    customer_note = models.TextField(blank=True, null=True)
    ordered_at = models.DateTimeField(blank=True, null=True)
    confirmed_at = models.DateTimeField(blank=True, null=True)
    shipped_at = models.DateTimeField(blank=True, null=True)
    delivered_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        db_table = 'store_order'
        verbose_name = 'Order'
        verbose_name_plural = 'Orders'
        ordering = ['-created_at']

    def __str__(self):
        return f"Order #{self.order_number}"

    def calculate_total(self):
        """Calculate total order amount."""
        self.subtotal = sum(item.get_subtotal() for item in self.items.all())
        self.total = self.subtotal - self.discount_amount + self.tax_amount + self.shipping_cost
        self.save()
        return self.total

    def confirm(self):
        """Confirm the order."""
        from django.utils import timezone
        self.status = 'confirmed'
        self.confirmed_at = timezone.now()
        self.save()

    def cancel(self):
        """Cancel the order."""
        self.status = 'cancelled'
        self.save()


class OrderItem(TimeStampedModel):
    """
    Order Item Model - Individual items in an order.
    """
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name='items'
    )
    book = models.ForeignKey(
        'store.Book',
        on_delete=models.CASCADE,
        related_name='order_items'
    )
    quantity = models.PositiveIntegerField(default=1)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    discount = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    class Meta:
        db_table = 'store_order_item'
        verbose_name = 'Order Item'
        verbose_name_plural = 'Order Items'

    def __str__(self):
        return f"{self.book.title} x {self.quantity}"

    def get_subtotal(self):
        """Calculate item subtotal."""
        return (self.unit_price * self.quantity) - self.discount


class OrderStatusHistory(TimeStampedModel):
    """
    Order Status History Model - Tracks order status changes.
    """
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name='status_history'
    )
    status = models.CharField(max_length=20)
    changed_by = models.ForeignKey(
        'store.Staff',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='order_status_changes'
    )
    notes = models.TextField(blank=True, null=True)

    class Meta:
        db_table = 'store_order_status_history'
        verbose_name = 'Order Status History'
        verbose_name_plural = 'Order Status Histories'
        ordering = ['-created_at']

    def __str__(self):
        return f"Order #{self.order.order_number} - {self.status}"


class Wishlist(TimeStampedModel):
    """
    Wishlist Model - Customer's wishlist.
    """
    customer = models.OneToOneField(
        'store.Customer',
        on_delete=models.CASCADE,
        related_name='wishlist'
    )
    name = models.CharField(max_length=255, default='My Wishlist')
    is_public = models.BooleanField(default=False)

    class Meta:
        db_table = 'store_wishlist'
        verbose_name = 'Wishlist'
        verbose_name_plural = 'Wishlists'

    def __str__(self):
        return f"{self.customer.name}'s Wishlist"

    def get_total_items(self):
        """Get total number of items in wishlist."""
        return self.items.count()


class WishlistItem(TimeStampedModel):
    """
    Wishlist Item Model - Individual items in a wishlist.
    """
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
    priority = models.IntegerField(default=0)
    notes = models.TextField(blank=True, null=True)

    class Meta:
        db_table = 'store_wishlist_item'
        verbose_name = 'Wishlist Item'
        verbose_name_plural = 'Wishlist Items'
        unique_together = ['wishlist', 'book']
        ordering = ['-priority', '-created_at']

    def __str__(self):
        return f"{self.book.title} in {self.wishlist.customer.name}'s wishlist"


class Review(TimeStampedModel):
    """
    Review Model - Customer reviews for books.
    """
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]

    customer = models.ForeignKey(
        'store.Customer',
        on_delete=models.CASCADE,
        related_name='reviews'
    )
    book = models.ForeignKey(
        'store.Book',
        on_delete=models.CASCADE,
        related_name='reviews'
    )
    order = models.ForeignKey(
        Order,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='reviews'
    )
    title = models.CharField(max_length=255, blank=True, null=True)
    content = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    is_verified_purchase = models.BooleanField(default=False)
    helpful_votes = models.IntegerField(default=0)

    class Meta:
        db_table = 'store_review'
        verbose_name = 'Review'
        verbose_name_plural = 'Reviews'
        unique_together = ['customer', 'book']
        ordering = ['-created_at']

    def __str__(self):
        return f"Review by {self.customer.name} for {self.book.title}"


class Rating(TimeStampedModel):
    """
    Rating Model - Customer ratings for books (separate from reviews).
    """
    customer = models.ForeignKey(
        'store.Customer',
        on_delete=models.CASCADE,
        related_name='ratings'
    )
    book = models.ForeignKey(
        'store.Book',
        on_delete=models.CASCADE,
        related_name='ratings'
    )
    score = models.IntegerField(choices=[(i, str(i)) for i in range(1, 6)])  # 1-5 stars

    class Meta:
        db_table = 'store_rating'
        verbose_name = 'Rating'
        verbose_name_plural = 'Ratings'
        unique_together = ['customer', 'book']

    def __str__(self):
        return f"{self.customer.name} rated {self.book.title}: {self.score}/5"
