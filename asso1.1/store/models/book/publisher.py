from django.db import models


class Publisher(models.Model):
    """
    Publisher Model - Represents a book publisher.
    
    Attributes:
        id: Auto-generated primary key
        name: Publisher's name
        address: Publisher's address
        city: Publisher's city
        country: Publisher's country
        website: Publisher's website URL
        email: Publisher's contact email
        phone: Publisher's phone number
    """
    name = models.CharField(max_length=255, unique=True)
    address = models.CharField(max_length=255, blank=True, null=True)
    city = models.CharField(max_length=100, blank=True, null=True)
    country = models.CharField(max_length=100, blank=True, null=True)
    website = models.URLField(blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    phone = models.CharField(max_length=20, blank=True, null=True)
    founded_year = models.PositiveIntegerField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'store_publisher'
        verbose_name = 'Publisher'
        verbose_name_plural = 'Publishers'
        ordering = ['name']

    def __str__(self):
        return self.name

    def get_books_count(self):
        """Return the number of books from this publisher."""
        return self.books.count()
