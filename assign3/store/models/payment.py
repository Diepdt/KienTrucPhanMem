"""
Payment Models - All payment and shipping related models.
Contains: Payment, PaymentMethod, ShippingMethod, Shipment, RefundRequest
"""
from django.db import models
from store.models.base import TimeStampedModel


class PaymentMethod(TimeStampedModel):
    """
    Payment Method Model - Defines available payment methods.
    """
    METHOD_CHOICES = [
        ('cod', 'Cash on Delivery'),
        ('credit_card', 'Credit Card'),
        ('debit_card', 'Debit Card'),
        ('bank_transfer', 'Bank Transfer'),
        ('e_wallet', 'E-Wallet'),
        ('momo', 'MoMo'),
        ('zalopay', 'ZaloPay'),
        ('vnpay', 'VNPay'),
    ]

    name = models.CharField(max_length=50, choices=METHOD_CHOICES, unique=True)
    display_name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    icon = models.ImageField(upload_to='payment_methods/', blank=True, null=True)
    is_active = models.BooleanField(default=True)
    processing_fee = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    min_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    max_amount = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)

    class Meta:
        db_table = 'store_payment_method'
        verbose_name = 'Payment Method'
        verbose_name_plural = 'Payment Methods'
        ordering = ['name']

    def __str__(self):
        return self.display_name


class Payment(TimeStampedModel):
    """
    Payment Model - Represents payment transactions.
    """
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('cancelled', 'Cancelled'),
        ('refunded', 'Refunded'),
    ]

    order = models.OneToOneField(
        'store.Order',
        on_delete=models.CASCADE,
        related_name='payment'
    )
    payment_method = models.ForeignKey(
        PaymentMethod,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='payments'
    )
    transaction_id = models.CharField(max_length=100, unique=True, blank=True, null=True)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    processing_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    paid_at = models.DateTimeField(blank=True, null=True)
    payment_details = models.JSONField(blank=True, null=True)  # Store additional payment info
    notes = models.TextField(blank=True, null=True)

    class Meta:
        db_table = 'store_payment'
        verbose_name = 'Payment'
        verbose_name_plural = 'Payments'
        ordering = ['-created_at']

    def __str__(self):
        return f"Payment for Order #{self.order.order_number}"

    def mark_as_completed(self):
        """Mark payment as completed."""
        from django.utils import timezone
        self.status = 'completed'
        self.paid_at = timezone.now()
        self.save()


class ShippingMethod(TimeStampedModel):
    """
    Shipping Method Model - Defines available shipping methods.
    """
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=50, unique=True)
    description = models.TextField(blank=True, null=True)
    carrier = models.CharField(max_length=100, blank=True, null=True)
    base_cost = models.DecimalField(max_digits=10, decimal_places=2)
    cost_per_kg = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    estimated_days_min = models.IntegerField(default=1)
    estimated_days_max = models.IntegerField(default=7)
    is_active = models.BooleanField(default=True)
    max_weight = models.DecimalField(max_digits=8, decimal_places=2, blank=True, null=True)  # in kg
    tracking_available = models.BooleanField(default=True)

    class Meta:
        db_table = 'store_shipping_method'
        verbose_name = 'Shipping Method'
        verbose_name_plural = 'Shipping Methods'
        ordering = ['base_cost']

    def __str__(self):
        return self.name

    def calculate_cost(self, weight):
        """Calculate shipping cost based on weight."""
        return self.base_cost + (self.cost_per_kg * weight)


class Shipment(TimeStampedModel):
    """
    Shipment Model - Tracks delivery of orders.
    """
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('picked_up', 'Picked Up'),
        ('in_transit', 'In Transit'),
        ('out_for_delivery', 'Out for Delivery'),
        ('delivered', 'Delivered'),
        ('failed', 'Delivery Failed'),
        ('returned', 'Returned'),
    ]

    order = models.OneToOneField(
        'store.Order',
        on_delete=models.CASCADE,
        related_name='shipment'
    )
    shipping_method = models.ForeignKey(
        ShippingMethod,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='shipments'
    )
    shipper = models.ForeignKey(
        'store.Shipper',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='shipments'
    )
    tracking_number = models.CharField(max_length=100, unique=True, blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    weight = models.DecimalField(max_digits=8, decimal_places=2, blank=True, null=True)
    shipping_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    shipped_at = models.DateTimeField(blank=True, null=True)
    estimated_delivery = models.DateTimeField(blank=True, null=True)
    delivered_at = models.DateTimeField(blank=True, null=True)
    recipient_name = models.CharField(max_length=255, blank=True, null=True)
    delivery_notes = models.TextField(blank=True, null=True)
    signature = models.ImageField(upload_to='signatures/', blank=True, null=True)

    class Meta:
        db_table = 'store_shipment'
        verbose_name = 'Shipment'
        verbose_name_plural = 'Shipments'
        ordering = ['-created_at']

    def __str__(self):
        return f"Shipment for Order #{self.order.order_number}"

    def mark_as_delivered(self):
        """Mark shipment as delivered."""
        from django.utils import timezone
        self.status = 'delivered'
        self.delivered_at = timezone.now()
        self.save()


class RefundRequest(TimeStampedModel):
    """
    Refund Request Model - Customer refund requests.
    """
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('rejected', 'Rejected'),
    ]

    REASON_CHOICES = [
        ('damaged', 'Product Damaged'),
        ('wrong_item', 'Wrong Item Received'),
        ('not_as_described', 'Not as Described'),
        ('change_of_mind', 'Change of Mind'),
        ('defective', 'Defective Product'),
        ('late_delivery', 'Late Delivery'),
        ('other', 'Other'),
    ]

    order = models.ForeignKey(
        'store.Order',
        on_delete=models.CASCADE,
        related_name='refund_requests'
    )
    customer = models.ForeignKey(
        'store.Customer',
        on_delete=models.CASCADE,
        related_name='refund_requests'
    )
    order_item = models.ForeignKey(
        'store.OrderItem',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='refund_requests'
    )
    request_number = models.CharField(max_length=50, unique=True)
    reason = models.CharField(max_length=20, choices=REASON_CHOICES)
    reason_detail = models.TextField(blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    refund_amount = models.DecimalField(max_digits=12, decimal_places=2)
    approved_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    processed_by = models.ForeignKey(
        'store.Staff',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='processed_refunds'
    )
    approved_at = models.DateTimeField(blank=True, null=True)
    completed_at = models.DateTimeField(blank=True, null=True)
    admin_notes = models.TextField(blank=True, null=True)
    evidence_images = models.JSONField(blank=True, null=True)  # Store list of image URLs

    class Meta:
        db_table = 'store_refund_request'
        verbose_name = 'Refund Request'
        verbose_name_plural = 'Refund Requests'
        ordering = ['-created_at']

    def __str__(self):
        return f"Refund #{self.request_number}"

    def approve(self, staff, amount):
        """Approve refund request."""
        from django.utils import timezone
        self.status = 'approved'
        self.processed_by = staff
        self.approved_amount = amount
        self.approved_at = timezone.now()
        self.save()
