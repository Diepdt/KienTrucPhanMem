from django.db import models


class Book(models.Model):
    """
    Book Model - Represents a book in the bookstore inventory.
    
    Attributes:
        id: Auto-generated primary key
        title: Book title
        author: Book author name
        price: Book price (decimal)
        stock_quantity: Number of books in stock
    """
    title = models.CharField(max_length=255)
    author = models.CharField(max_length=255)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    stock_quantity = models.IntegerField(default=0)

    class Meta:
        db_table = 'store_book'
        verbose_name = 'Book'
        verbose_name_plural = 'Books'
        ordering = ['title']

    def __str__(self):
        return f"{self.title} by {self.author}"

    def is_in_stock(self):
        """Check if book is available in stock."""
        return self.stock_quantity > 0

    def reduce_stock(self, quantity):
        """Reduce stock quantity after purchase."""
        if quantity > self.stock_quantity:
            raise ValueError("Insufficient stock quantity")
        self.stock_quantity -= quantity
        self.save()

    def add_stock(self, quantity):
        """Add stock quantity (for staff inventory management)."""
        self.stock_quantity += quantity
        self.save()
