from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator


class Review(models.Model):
    """
    Review Model - Detailed book review by customer.
    
    Attributes:
        id: Auto-generated primary key
        customer: Foreign key to Customer
        book: Foreign key to Book
        title: Review title
        content: Review content
        rating: Rating score (1-5)
        is_verified_purchase: Whether customer purchased the book
        helpful_votes: Number of helpful votes
        is_approved: Whether review is approved for display
    """
    customer = models.ForeignKey(
        'store.Customer',
        on_delete=models.CASCADE,
        related_name='reviews'
    )
    book = models.ForeignKey(
        'store.Book',
        on_delete=models.CASCADE,
        related_name='reviews'
    )
    title = models.CharField(max_length=255)
    content = models.TextField()
    rating = models.PositiveIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    is_verified_purchase = models.BooleanField(default=False)
    helpful_votes = models.PositiveIntegerField(default=0)
    not_helpful_votes = models.PositiveIntegerField(default=0)
    is_approved = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'store_review'
        verbose_name = 'Review'
        verbose_name_plural = 'Reviews'
        ordering = ['-created_at']
        unique_together = ['customer', 'book']  # One review per book per customer

    def __str__(self):
        return f"Review by {self.customer.name} for {self.book.title}"

    def mark_helpful(self):
        """Mark this review as helpful."""
        self.helpful_votes += 1
        self.save()

    def mark_not_helpful(self):
        """Mark this review as not helpful."""
        self.not_helpful_votes += 1
        self.save()

    def get_helpfulness_ratio(self):
        """Calculate the helpfulness ratio."""
        total = self.helpful_votes + self.not_helpful_votes
        if total == 0:
            return 0
        return self.helpful_votes / total

    def verify_purchase(self):
        """Check if customer has purchased this book."""
        from store.models.order.order import OrderItem
        has_purchase = OrderItem.objects.filter(
            order__customer=self.customer,
            book=self.book,
            order__status='delivered'
        ).exists()
        self.is_verified_purchase = has_purchase
        self.save()
        return has_purchase
