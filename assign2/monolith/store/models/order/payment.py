from django.db import models
from decimal import Decimal


class Payment(models.Model):
    """
    Payment Model - Represents payment information for an order.
    
    Attributes:
        method: Payment method type
        amount: Payment amount
        status: Payment status
        transaction_id: External transaction reference
    """
    METHOD_CHOICES = [
        ('credit_card', 'Credit Card'),
        ('debit_card', 'Debit Card'),
        ('paypal', 'PayPal'),
        ('bank_transfer', 'Bank Transfer'),
        ('cod', 'Cash on Delivery'),
    ]

    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('refunded', 'Refunded'),
    ]

    method = models.CharField(max_length=20, choices=METHOD_CHOICES, default='credit_card')
    amount = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    transaction_id = models.CharField(max_length=255, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'store_payment'
        verbose_name = 'Payment'
        verbose_name_plural = 'Payments'

    def __str__(self):
        return f"{self.get_method_display()} - ${self.amount} ({self.get_status_display()})"

    def mark_as_completed(self, transaction_id=None):
        """Mark payment as completed."""
        self.status = 'completed'
        if transaction_id:
            self.transaction_id = transaction_id
        self.save()

    def mark_as_failed(self):
        """Mark payment as failed."""
        self.status = 'failed'
        self.save()

    def refund(self):
        """Process refund for the payment."""
        if self.status == 'completed':
            self.status = 'refunded'
            self.save()
            return True
        return False
