from django.db import models
from decimal import Decimal


class Order(models.Model):
    """
    Order Model - Represents a customer order.
    
    Attributes:
        customer: Foreign key to Customer
        shipping: Foreign key to Shipping
        payment: Foreign key to Payment
        status: Order status
        total_amount: Total order amount
    """
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('processing', 'Processing'),
        ('shipped', 'Shipped'),
        ('delivered', 'Delivered'),
        ('cancelled', 'Cancelled'),
    ]

    customer = models.ForeignKey(
        'store.Customer',
        on_delete=models.CASCADE,
        related_name='orders'
    )
    shipping = models.OneToOneField(
        'store.Shipping',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='order'
    )
    payment = models.OneToOneField(
        'store.Payment',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='order'
    )
    # Staff who processes this order (theo diagram)
    staff = models.ForeignKey(
        'store.Staff',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='processed_orders'
    )
    status = models.CharField(max_length=255, choices=STATUS_CHOICES, default='pending')
    total = models.FloatField(default=0)  # Renamed from total_amount theo diagram
    notes = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'store_order'
        verbose_name = 'Order'
        verbose_name_plural = 'Orders'
        ordering = ['-created_at']

    def __str__(self):
        return f"Order #{self.id} - {self.customer.name}"

    def calculate_total(self):
        """Calculate total order amount including shipping."""
        items_total = sum(float(item.get_subtotal()) for item in self.order_items.all())
        shipping_cost = float(self.shipping.cost) if self.shipping else 0.0
        self.total = items_total + shipping_cost
        self.save()
        return self.total

    def confirm(self):
        """Confirm the order."""
        self.status = 'confirmed'
        self.save()

    def cancel(self):
        """Cancel the order and restore stock."""
        if self.status not in ['shipped', 'delivered']:
            for item in self.order_items.all():
                item.book.add_stock(item.quantity)
            self.status = 'cancelled'
            self.save()
            return True
        return False


class OrderItem(models.Model):
    """
    OrderItem Model - Represents an item in an order.
    
    Attributes:
        order: Foreign key to Order
        book: Foreign key to Book
        quantity: Number of books ordered
        price: Price at time of order (snapshot)
    """
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name='order_items'
    )
    book = models.ForeignKey(
        'store.Book',
        on_delete=models.CASCADE,
        related_name='order_items'
    )
    quantity = models.PositiveIntegerField(default=1)
    price = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        db_table = 'store_order_item'
        verbose_name = 'Order Item'
        verbose_name_plural = 'Order Items'

    def __str__(self):
        return f"{self.quantity}x {self.book.title} in Order #{self.order.id}"

    def get_subtotal(self):
        """Calculate subtotal for this order item."""
        return self.price * self.quantity
