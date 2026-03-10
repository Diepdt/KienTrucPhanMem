from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator

class Review(models.Model):
    customer_id = models.IntegerField()
    book_id = models.IntegerField()
    rating = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)])
    comment = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ['customer_id', 'book_id']

    def __str__(self):
        return f"Review by customer#{self.customer_id} for book#{self.book_id} - {self.rating}★"
