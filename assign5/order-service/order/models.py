from django.db import models

class Order(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Chờ xác nhận'),
        ('confirmed', 'Đã xác nhận'),
        ('shipping', 'Đang vận chuyển'),
        ('delivered', 'Đã giao hàng'),
        ('cancelled', 'Đã hủy'),
    ]
    customer_id = models.IntegerField()
    shipping_method_id = models.IntegerField()
    shipping_method_name = models.CharField(max_length=100, blank=True)
    shipping_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    payment_method_id = models.IntegerField()
    payment_method_name = models.CharField(max_length=100, blank=True)
    subtotal = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    shipping_address = models.TextField()
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Order #{self.id} - Customer {self.customer_id}"


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    book_id = models.IntegerField()
    book_title = models.CharField(max_length=255)
    book_author = models.CharField(max_length=255, blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.IntegerField(default=1)

    @property
    def item_total(self):
        return self.price * self.quantity

    def __str__(self):
        return f"{self.book_title} x{self.quantity}"
