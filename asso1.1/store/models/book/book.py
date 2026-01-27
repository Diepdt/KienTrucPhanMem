from django.db import models


class Book(models.Model):
    """
    Book Model - Represents a book in the bookstore inventory.
    
    Attributes:
        id: Auto-generated primary key
        title: Book title
        author: Book author name (legacy field)
        author_obj: Foreign key to Author
        publisher: Foreign key to Publisher
        price: Book price (decimal)
        stock_quantity: Number of books in stock
        category: Foreign key to Category (Many-to-One)
        isbn: International Standard Book Number
        description: Book description
        publication_date: Publication date
        pages: Number of pages
    """
    category = models.ForeignKey(
        'store.Category',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='books'
    )
    author_obj = models.ForeignKey(
        'store.Author',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='books'
    )
    publisher = models.ForeignKey(
        'store.Publisher',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='books'
    )
    title = models.CharField(max_length=255)
    author = models.CharField(max_length=255)  # Legacy field for backward compatibility
    isbn = models.CharField(max_length=13, unique=True, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    stock_quantity = models.IntegerField(default=0)
    pages = models.PositiveIntegerField(blank=True, null=True)
    publication_date = models.DateField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

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

    def get_average_rating(self):
        """Calculate average rating from reviews."""
        reviews = self.reviews.filter(is_approved=True)
        if not reviews.exists():
            return 0
        return reviews.aggregate(models.Avg('rating'))['rating__avg']

    def get_reviews_count(self):
        """Return number of approved reviews."""
        return self.reviews.filter(is_approved=True).count()
