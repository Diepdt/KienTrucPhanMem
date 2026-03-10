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
    book_id = models.IntegerField()
    book_title = models.CharField(max_length=255, blank=True)   # snapshot
    book_author = models.CharField(max_length=255, blank=True)  # snapshot
    price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.IntegerField(default=1)

    class Meta:
        unique_together = ['cart', 'book_id']

    @property
    def item_total(self):
        return self.price * self.quantity

    def __str__(self):
        return f"{self.book_title} x{self.quantity}"
