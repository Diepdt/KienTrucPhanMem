from django.db import models

class Cart(models.Model):
    """Giỏ hàng - tạo tự động khi khách hàng đăng ký."""
    customer_id = models.IntegerField(unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Cart #{self.customer_id}"

    @property
    def total(self):
        return sum(item.item_total for item in self.items.all())


class CartItem(models.Model):
    """Item trong giỏ hàng."""
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items')
    product_type = models.CharField(max_length=50, default='book')
    product_id = models.IntegerField()
    product_name = models.CharField(max_length=255, blank=True)
    product_subtitle = models.CharField(max_length=255, blank=True)
    product_image_url = models.URLField(blank=True)
    source_service = models.CharField(max_length=100, blank=True)
    product_snapshot = models.JSONField(default=dict, blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.IntegerField(default=1)

    class Meta:
        unique_together = ['cart', 'product_type', 'product_id']

    @property
    def item_total(self):
        return self.price * self.quantity

    def __str__(self):
        display_name = self.product_name or f"{self.product_type}:{self.product_id}"
        return f"{display_name} x{self.quantity}"
