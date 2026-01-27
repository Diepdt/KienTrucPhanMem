from django.db import models
from django.utils import timezone
import secrets
import string


class Coupon(models.Model):
    """
    Coupon Model - Represents a discount coupon code.
    
    Attributes:
        id: Auto-generated primary key
        code: Unique coupon code
        discount_percent: Discount percentage
        discount_amount: Fixed discount amount
        valid_from: Coupon validity start date
        valid_to: Coupon validity end date
        max_uses: Maximum number of times coupon can be used
        is_active: Whether coupon is active
    """
    DISCOUNT_TYPE_CHOICES = [
        ('percent', 'Percentage'),
        ('fixed', 'Fixed Amount'),
    ]

    code = models.CharField(max_length=50, unique=True)
    description = models.TextField(blank=True, null=True)
    discount_type = models.CharField(max_length=10, choices=DISCOUNT_TYPE_CHOICES, default='percent')
    discount_percent = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    discount_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    valid_from = models.DateTimeField()
    valid_to = models.DateTimeField()
    max_uses = models.PositiveIntegerField(default=1)
    current_uses = models.PositiveIntegerField(default=0)
    min_order_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'store_coupon'
        verbose_name = 'Coupon'
        verbose_name_plural = 'Coupons'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.code} - {self.discount_percent}%" if self.discount_type == 'percent' else f"{self.code} - ${self.discount_amount}"

    @classmethod
    def generate_code(cls, length=8):
        """Generate a random coupon code."""
        characters = string.ascii_uppercase + string.digits
        while True:
            code = ''.join(secrets.choice(characters) for _ in range(length))
            if not cls.objects.filter(code=code).exists():
                return code

    def is_valid(self):
        """Check if coupon is currently valid."""
        now = timezone.now()
        return (
            self.is_active and
            self.valid_from <= now <= self.valid_to and
            self.current_uses < self.max_uses
        )

    def calculate_discount(self, order_total):
        """Calculate discount amount for given order total."""
        if not self.is_valid() or order_total < self.min_order_amount:
            return 0
        if self.discount_type == 'percent':
            return order_total * (self.discount_percent / 100)
        return min(self.discount_amount, order_total)

    def redeem(self):
        """Redeem the coupon (increment usage counter)."""
        if self.is_valid():
            self.current_uses += 1
            self.save()
            return True
        return False
