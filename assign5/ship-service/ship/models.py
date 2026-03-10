from django.db import models
import uuid

class ShippingMethod(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    cost = models.DecimalField(max_digits=10, decimal_places=2)
    delivery_days = models.IntegerField(default=3)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name


class Shipment(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Chờ xử lý'),
        ('processing', 'Đang xử lý'),
        ('shipped', 'Đang vận chuyển'),
        ('delivered', 'Đã giao hàng'),
        ('failed', 'Giao hàng thất bại'),
        ('returned', 'Đã hoàn hàng'),
    ]
    order_id = models.IntegerField(unique=True)
    method = models.ForeignKey(ShippingMethod, on_delete=models.PROTECT)
    method_name = models.CharField(max_length=100, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    shipping_address = models.TextField()
    tracking_number = models.CharField(max_length=64, unique=True, blank=True)
    estimated_delivery = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.tracking_number:
            self.tracking_number = f"TRK-{uuid.uuid4().hex[:12].upper()}"
        if not self.method_name and self.method_id:
            self.method_name = self.method.name
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Shipment #{self.order_id} - {self.tracking_number}"
