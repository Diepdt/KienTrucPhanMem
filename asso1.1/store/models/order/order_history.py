from django.db import models


class OrderHistory(models.Model):
    """
    OrderHistory Model - Tracks order status changes history.
    
    Attributes:
        id: Auto-generated primary key
        order: Foreign key to Order
        old_status: Previous order status
        new_status: New order status
        changed_by: Staff who made the change
        notes: Additional notes
    """
    order = models.ForeignKey(
        'store.Order',
        on_delete=models.CASCADE,
        related_name='history'
    )
    old_status = models.CharField(max_length=50, blank=True, null=True)
    new_status = models.CharField(max_length=50)
    changed_by = models.ForeignKey(
        'store.Staff',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='order_status_changes'
    )
    notes = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'store_order_history'
        verbose_name = 'Order History'
        verbose_name_plural = 'Order Histories'
        ordering = ['-created_at']

    def __str__(self):
        return f"Order #{self.order.id}: {self.old_status} → {self.new_status}"

    @classmethod
    def log_status_change(cls, order, old_status, new_status, staff=None, notes=None):
        """Create a history entry for status change."""
        return cls.objects.create(
            order=order,
            old_status=old_status,
            new_status=new_status,
            changed_by=staff,
            notes=notes
        )
