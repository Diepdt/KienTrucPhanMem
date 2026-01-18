from django.db import models

class CustomerModel(models.Model):
    name = models.CharField(max_length=255)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'accounts_customer'
        app_label = 'infrastructure'  # <--- THÊM DÒNG NÀY

    def __str__(self):
        return self.name

class BookModel(models.Model):
    title = models.CharField(max_length=255)
    author = models.CharField(max_length=255)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'books_book'
        app_label = 'infrastructure'  # <--- THÊM DÒNG NÀY

    def __str__(self):
        return self.title

class CartModel(models.Model):
    customer = models.OneToOneField(CustomerModel, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'cart_cart'
        app_label = 'infrastructure'  # <--- THÊM DÒNG NÀY

    def __str__(self):
        return f"Cart {self.customer.name}"

class CartItemModel(models.Model):
    cart = models.ForeignKey(CartModel, on_delete=models.CASCADE, related_name='items')
    book = models.ForeignKey(BookModel, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1)
    
    class Meta:
        db_table = 'cart_cartitem'
        unique_together = ('cart', 'book')
        app_label = 'infrastructure'  # <--- THÊM DÒNG NÀY

    def __str__(self):
        return f"{self.book.title} x {self.quantity}"