from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator


class Rating(models.Model):
    """
    Rating Model - Represents a customer's rating for a book.
    Used for recommendation logic.
    
    Attributes:
        customer: Foreign key to Customer
        book: Foreign key to Book
        score: Rating score (1-5)
    """
    customer = models.ForeignKey(
        'store.Customer',
        on_delete=models.CASCADE,
        related_name='ratings'
    )
    book = models.ForeignKey(
        'store.Book',
        on_delete=models.CASCADE,
        related_name='ratings'
    )
    score = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        help_text="Rating score from 1 to 5"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'store_rating'
        verbose_name = 'Rating'
        verbose_name_plural = 'Ratings'
        unique_together = ['customer', 'book']  # One rating per customer per book

    def __str__(self):
        return f"{self.customer.name} rated {self.book.title}: {self.score}/5"
