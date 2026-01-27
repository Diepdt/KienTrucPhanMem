from django.db import models


class Notification(models.Model):
    """
    Notification Model - System notifications for customers and staff.
    
    Attributes:
        id: Auto-generated primary key
        recipient_type: Type of recipient (customer/staff)
        customer: Foreign key to Customer (if recipient is customer)
        staff: Foreign key to Staff (if recipient is staff)
        title: Notification title
        message: Notification message
        notification_type: Type of notification
        is_read: Whether notification has been read
    """
    RECIPIENT_TYPE_CHOICES = [
        ('customer', 'Customer'),
        ('staff', 'Staff'),
    ]

    NOTIFICATION_TYPE_CHOICES = [
        ('order_placed', 'Order Placed'),
        ('order_shipped', 'Order Shipped'),
        ('order_delivered', 'Order Delivered'),
        ('order_cancelled', 'Order Cancelled'),
        ('promotion', 'Promotion'),
        ('price_drop', 'Price Drop'),
        ('back_in_stock', 'Back in Stock'),
        ('review_approved', 'Review Approved'),
        ('system', 'System'),
    ]

    recipient_type = models.CharField(max_length=10, choices=RECIPIENT_TYPE_CHOICES)
    customer = models.ForeignKey(
        'store.Customer',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='notifications'
    )
    staff = models.ForeignKey(
        'store.Staff',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='notifications'
    )
    title = models.CharField(max_length=255)
    message = models.TextField()
    notification_type = models.CharField(max_length=20, choices=NOTIFICATION_TYPE_CHOICES, default='system')
    is_read = models.BooleanField(default=False)
    related_order = models.ForeignKey(
        'store.Order',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='notifications'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'store_notification'
        verbose_name = 'Notification'
        verbose_name_plural = 'Notifications'
        ordering = ['-created_at']

    def __str__(self):
        recipient = self.customer.name if self.customer else self.staff.name
        return f"Notification to {recipient}: {self.title}"

    def mark_as_read(self):
        """Mark notification as read."""
        self.is_read = True
        self.save()

    @classmethod
    def send_to_customer(cls, customer, title, message, notification_type='system', related_order=None):
        """Send notification to a customer."""
        return cls.objects.create(
            recipient_type='customer',
            customer=customer,
            title=title,
            message=message,
            notification_type=notification_type,
            related_order=related_order
        )

    @classmethod
    def send_to_staff(cls, staff, title, message, notification_type='system', related_order=None):
        """Send notification to a staff member."""
        return cls.objects.create(
            recipient_type='staff',
            staff=staff,
            title=title,
            message=message,
            notification_type=notification_type,
            related_order=related_order
        )
