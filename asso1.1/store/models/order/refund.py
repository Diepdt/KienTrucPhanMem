from django.db import models


class Refund(models.Model):
    """
    Refund Model - Represents a refund request for an order.
    
    Attributes:
        id: Auto-generated primary key
        order: Foreign key to Order
        amount: Refund amount
        reason: Reason for refund
        status: Refund status
        processed_by: Staff who processed the refund
    """
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('processed', 'Processed'),
    ]

    REASON_CHOICES = [
        ('damaged', 'Damaged Product'),
        ('wrong_item', 'Wrong Item Delivered'),
        ('not_as_described', 'Not As Described'),
        ('changed_mind', 'Changed Mind'),
        ('late_delivery', 'Late Delivery'),
        ('other', 'Other'),
    ]

    order = models.ForeignKey(
        'store.Order',
        on_delete=models.CASCADE,
        related_name='refunds'
    )
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    reason = models.CharField(max_length=20, choices=REASON_CHOICES)
    reason_details = models.TextField(blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    processed_by = models.ForeignKey(
        'store.Staff',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='processed_refunds'
    )
    processed_at = models.DateTimeField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'store_refund'
        verbose_name = 'Refund'
        verbose_name_plural = 'Refunds'
        ordering = ['-created_at']

    def __str__(self):
        return f"Refund #{self.id} for Order #{self.order.id} - ${self.amount}"

    def approve(self, staff):
        """Approve the refund request."""
        from django.utils import timezone
        self.status = 'approved'
        self.processed_by = staff
        self.processed_at = timezone.now()
        self.save()

    def reject(self, staff, reason=None):
        """Reject the refund request."""
        from django.utils import timezone
        self.status = 'rejected'
        self.processed_by = staff
        self.processed_at = timezone.now()
        if reason:
            self.reason_details = reason
        self.save()

    def process(self, staff):
        """Process the approved refund."""
        from django.utils import timezone
        if self.status == 'approved':
            self.status = 'processed'
            self.processed_by = staff
            self.processed_at = timezone.now()
            self.save()
            return True
        return False
