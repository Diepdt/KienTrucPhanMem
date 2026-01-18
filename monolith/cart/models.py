from django.db import models
from accounts.models import Customer
from books.models import Book

class Cart(models.Model):
    # Theo yêu cầu: customer_id, created_at [cite: 85]
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

class CartItem(models.Model):
    # Theo yêu cầu: cart_id, book_id, quantity [cite: 85]
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE)
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1) # Slide trang 15 nhấn mạnh cần field này [cite: 336]