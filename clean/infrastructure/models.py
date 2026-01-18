from django.db import models

class CustomerModel(models.Model):
    """Django Model: Customer - dùng chung với monolith"""
    name = models.CharField(max_length=255)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'accounts_customer'  # Dùng chung table với monolith
    
    def __str__(self):
        return self.name

class BookModel(models.Model):
    """Django Model: Book - dùng chung với monolith"""
    title = models.CharField(max_length=255)
    author = models.CharField(max_length=255)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'books_book'  # Dùng chung table với monolith
    
    def __str__(self):
        return self.title

class CartModel(models.Model):
    """Django Model: Cart - dùng chung với monolith"""
    customer = models.OneToOneField(CustomerModel, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'cart_cart'  # Dùng chung table với monolith
    
    def __str__(self):
        return f"Cart {self.customer.name}"

class CartItemModel(models.Model):
    """Django Model: CartItem - dùng chung với monolith"""
    cart = models.ForeignKey(CartModel, on_delete=models.CASCADE, related_name='items')
    book = models.ForeignKey(BookModel, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1)
    
    class Meta:
        db_table = 'cart_cartitem'  # Dùng chung table với monolith
        unique_together = ('cart', 'book')
    
    def __str__(self):
        return f"{self.book.title} x {self.quantity}"
