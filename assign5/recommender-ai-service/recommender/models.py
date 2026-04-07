from django.db import models

class Recommendation(models.Model):
    """Cache bảng gợi ý - để tránh tính toán lại mỗi lần."""
    customer_id = models.IntegerField()
    service_type = models.CharField(max_length=50, default='book')
    product_id = models.IntegerField()
    score = models.FloatField(default=0.0)
    reason = models.CharField(max_length=255, blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ['customer_id', 'service_type', 'product_id']
        ordering = ['-score']

    def __str__(self):
        return f"Recommend {self.service_type}#{self.product_id} to customer#{self.customer_id} (score={self.score})"
