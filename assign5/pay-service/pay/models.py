from django.db import models
import uuid

class PaymentMethod(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name


class Payment(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Chờ thanh toán'),
        ('processing', 'Đang xử lý'),
        ('completed', 'Thanh toán thành công'),
        ('failed', 'Thanh toán thất bại'),
        ('refunded', 'Đã hoàn tiền'),
    ]
    order_id = models.IntegerField(unique=True)
    method = models.ForeignKey(PaymentMethod, on_delete=models.PROTECT)
    method_name = models.CharField(max_length=100, blank=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    transaction_id = models.CharField(max_length=64, unique=True, blank=True)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.transaction_id:
            self.transaction_id = f"PAY-{uuid.uuid4().hex[:12].upper()}"
        if not self.method_name and self.method_id:
            self.method_name = self.method.name
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Payment #{self.order_id} - {self.transaction_id}"
