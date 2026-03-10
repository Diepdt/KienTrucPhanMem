from django.db import models

class Recommendation(models.Model):
    """Cache bảng gợi ý - để tránh tính toán lại mỗi lần."""
    customer_id = models.IntegerField()
    book_id = models.IntegerField()
    score = models.FloatField(default=0.0)
    reason = models.CharField(max_length=255, blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ['customer_id', 'book_id']
        ordering = ['-score']

    def __str__(self):
        return f"Recommend book#{self.book_id} to customer#{self.customer_id} (score={self.score})"
