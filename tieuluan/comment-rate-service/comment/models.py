from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator

class Review(models.Model):
    customer_id = models.IntegerField()
    product_type = models.CharField(max_length=20, default='book')
    product_id = models.IntegerField()
    rating = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)])
    comment = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ['customer_id', 'product_type', 'product_id']

    def __str__(self):
        return f"Review by customer#{self.customer_id} for {self.product_type}#{self.product_id} - {self.rating}★"
