from django.db import models
from django.utils import timezone


class Promotion(models.Model):
    """
    Promotion Model - Represents a promotional campaign.
    
    Attributes:
        id: Auto-generated primary key
        name: Promotion name
        description: Promotion description
        discount_percent: Discount percentage (0-100)
        discount_amount: Fixed discount amount
        start_date: Promotion start date
        end_date: Promotion end date
        is_active: Whether promotion is active
        min_order_amount: Minimum order amount to apply promotion
    """
    DISCOUNT_TYPE_CHOICES = [
        ('percent', 'Percentage'),
        ('fixed', 'Fixed Amount'),
    ]

    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    discount_type = models.CharField(max_length=10, choices=DISCOUNT_TYPE_CHOICES, default='percent')
    discount_percent = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    discount_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    is_active = models.BooleanField(default=True)
    min_order_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    max_uses = models.PositiveIntegerField(default=0, help_text="0 for unlimited")
    current_uses = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'store_promotion'
        verbose_name = 'Promotion'
        verbose_name_plural = 'Promotions'
        ordering = ['-start_date']

    def __str__(self):
        return f"{self.name} ({self.discount_percent}%)" if self.discount_type == 'percent' else f"{self.name} (-${self.discount_amount})"

    def is_valid(self):
        """Check if promotion is currently valid."""
        now = timezone.now()
        return (
            self.is_active and 
            self.start_date <= now <= self.end_date and
            (self.max_uses == 0 or self.current_uses < self.max_uses)
        )

    def calculate_discount(self, order_total):
        """Calculate discount amount for given order total."""
        if not self.is_valid() or order_total < self.min_order_amount:
            return 0
        if self.discount_type == 'percent':
            return order_total * (self.discount_percent / 100)
        return min(self.discount_amount, order_total)

    def apply(self):
        """Increment usage counter when promotion is applied."""
        self.current_uses += 1
        self.save()
