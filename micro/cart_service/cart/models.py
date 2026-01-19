# micro/cart_service/cart/models.py
"""
Models cho Cart Service.
QUAN TRỌNG: Không sử dụng ForeignKey đến các model ở Service khác.
Chỉ lưu ID (customer_id, book_id) để tham chiếu cross-service.
"""
from django.db import models


class Cart(models.Model):
    """
    Giỏ hàng của khách hàng.
    Chỉ lưu customer_id thay vì ForeignKey đến Customer model.
    """
    customer_id = models.IntegerField(unique=True)  # ID của customer từ Customer Service
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Cart of Customer #{self.customer_id}"


class CartItem(models.Model):
    """
    Item trong giỏ hàng.
    Lưu book_id thay vì ForeignKey đến Book model.
    Lưu price và book_title tại thời điểm thêm vào giỏ (snapshot).
    """
    cart = models.ForeignKey(Cart, related_name='items', on_delete=models.CASCADE)
    book_id = models.IntegerField()  # ID của sách từ Book Service
    book_title = models.CharField(max_length=255, blank=True)  # Snapshot tên sách
    quantity = models.IntegerField(default=1)
    price = models.DecimalField(max_digits=10, decimal_places=2)  # Snapshot giá

    class Meta:
        unique_together = ['cart', 'book_id']  # Mỗi sách chỉ có 1 record trong giỏ

    def __str__(self):
        return f"{self.book_title} x {self.quantity}"

    @property
    def item_total(self):
        """Tổng tiền của item này"""
        return self.price * self.quantity