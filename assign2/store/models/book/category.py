from django.db import models


class Category(models.Model):
    """
    Category Model - Represents a book category/genre.
    One-to-Many relationship with Book (1 Category has many Books).
    
    Attributes:
        id: Auto-generated primary key
        type: Category type/name (e.g., Fiction, Science, History)
    """
    type = models.CharField(max_length=100, unique=True, verbose_name='Category Type')

    class Meta:
        db_table = 'store_category'
        verbose_name = 'Category'
        verbose_name_plural = 'Categories'
        ordering = ['type']

    def __str__(self):
        return self.type

    def get_books_count(self):
        """Return the number of books in this category."""
        return self.books.count()
