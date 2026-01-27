from django.db import models


class Author(models.Model):
    """
    Author Model - Represents a book author.
    
    Attributes:
        id: Auto-generated primary key
        name: Author's full name
        biography: Author's biography
        birth_date: Author's birth date
        email: Author's contact email
        website: Author's website URL
    """
    name = models.CharField(max_length=255)
    biography = models.TextField(blank=True, null=True)
    birth_date = models.DateField(blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    website = models.URLField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'store_author'
        verbose_name = 'Author'
        verbose_name_plural = 'Authors'
        ordering = ['name']

    def __str__(self):
        return self.name

    def get_books_count(self):
        """Return the number of books by this author."""
        return self.books.count()

    def get_total_sales(self):
        """Calculate total sales across all books by this author."""
        from store.models.order.order import OrderItem
        total = OrderItem.objects.filter(book__author_obj=self).aggregate(
            total=models.Sum('quantity')
        )['total']
        return total or 0
