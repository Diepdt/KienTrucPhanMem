"""
Inventory Models - All inventory and supply chain related models.
Contains: Supplier, Warehouse, Inventory, ImportOrder, ImportOrderItem, 
         StockTransfer, ReturnRequestToSupplier
"""
from django.db import models
from store.models.base import TimeStampedModel


class Supplier(TimeStampedModel):
    """
    Supplier Model - Represents book suppliers/distributors.
    """
    name = models.CharField(max_length=255)
    code = models.CharField(max_length=50, unique=True)
    contact_person = models.CharField(max_length=255, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    phone = models.CharField(max_length=20, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    city = models.CharField(max_length=100, blank=True, null=True)
    country = models.CharField(max_length=100, default='Vietnam')
    tax_id = models.CharField(max_length=50, blank=True, null=True)
    payment_terms = models.TextField(blank=True, null=True)
    lead_time_days = models.IntegerField(default=7)
    is_active = models.BooleanField(default=True)
    rating = models.DecimalField(max_digits=3, decimal_places=2, default=0)
    notes = models.TextField(blank=True, null=True)

    class Meta:
        db_table = 'store_supplier'
        verbose_name = 'Supplier'
        verbose_name_plural = 'Suppliers'
        ordering = ['name']

    def __str__(self):
        return self.name


class Warehouse(TimeStampedModel):
    """
    Warehouse Model - Represents physical warehouse locations.
    """
    name = models.CharField(max_length=255)
    code = models.CharField(max_length=50, unique=True)
    address = models.TextField()
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100, blank=True, null=True)
    postal_code = models.CharField(max_length=20, blank=True, null=True)
    country = models.CharField(max_length=100, default='Vietnam')
    phone = models.CharField(max_length=20, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    manager_name = models.CharField(max_length=255, blank=True, null=True)
    capacity = models.IntegerField(default=0)  # Total capacity
    current_stock = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)
    is_primary = models.BooleanField(default=False)

    class Meta:
        db_table = 'store_warehouse'
        verbose_name = 'Warehouse'
        verbose_name_plural = 'Warehouses'
        ordering = ['name']

    def __str__(self):
        return f"{self.name} ({self.code})"

    def get_available_capacity(self):
        """Calculate available warehouse capacity."""
        return self.capacity - self.current_stock


class Inventory(TimeStampedModel):
    """
    Inventory Model - Links Books and Warehouses, tracks stock levels.
    """
    book = models.ForeignKey(
        'store.Book',
        on_delete=models.CASCADE,
        related_name='inventory_records'
    )
    warehouse = models.ForeignKey(
        Warehouse,
        on_delete=models.CASCADE,
        related_name='inventory_records'
    )
    quantity = models.IntegerField(default=0)
    min_stock_level = models.IntegerField(default=10)
    max_stock_level = models.IntegerField(default=1000)
    reorder_point = models.IntegerField(default=20)
    last_restocked = models.DateTimeField(blank=True, null=True)
    shelf_location = models.CharField(max_length=100, blank=True, null=True)

    class Meta:
        db_table = 'store_inventory'
        verbose_name = 'Inventory'
        verbose_name_plural = 'Inventory Records'
        unique_together = ['book', 'warehouse']

    def __str__(self):
        return f"{self.book.title} at {self.warehouse.name}: {self.quantity}"

    def needs_reorder(self):
        """Check if inventory needs reordering."""
        return self.quantity <= self.reorder_point

    def is_low_stock(self):
        """Check if inventory is below minimum level."""
        return self.quantity < self.min_stock_level


class ImportOrder(TimeStampedModel):
    """
    Import Order Model - Represents orders from suppliers.
    """
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('submitted', 'Submitted'),
        ('confirmed', 'Confirmed'),
        ('shipped', 'Shipped'),
        ('received', 'Received'),
        ('cancelled', 'Cancelled'),
    ]

    order_number = models.CharField(max_length=50, unique=True)
    supplier = models.ForeignKey(
        Supplier,
        on_delete=models.CASCADE,
        related_name='import_orders'
    )
    warehouse = models.ForeignKey(
        Warehouse,
        on_delete=models.CASCADE,
        related_name='import_orders'
    )
    created_by = models.ForeignKey(
        'store.Staff',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='created_import_orders'
    )
    approved_by = models.ForeignKey(
        'store.Staff',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='approved_import_orders'
    )
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    order_date = models.DateField()
    expected_delivery_date = models.DateField(blank=True, null=True)
    actual_delivery_date = models.DateField(blank=True, null=True)
    subtotal = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    tax_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    shipping_cost = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    total_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    notes = models.TextField(blank=True, null=True)

    class Meta:
        db_table = 'store_import_order'
        verbose_name = 'Import Order'
        verbose_name_plural = 'Import Orders'
        ordering = ['-created_at']

    def __str__(self):
        return f"Import #{self.order_number}"

    def calculate_total(self):
        """Calculate total order amount."""
        self.subtotal = sum(item.get_subtotal() for item in self.items.all())
        self.total_amount = self.subtotal + self.tax_amount + self.shipping_cost
        self.save()
        return self.total_amount


class ImportOrderItem(TimeStampedModel):
    """
    Import Order Item Model - Individual items in an import order.
    """
    import_order = models.ForeignKey(
        ImportOrder,
        on_delete=models.CASCADE,
        related_name='items'
    )
    book = models.ForeignKey(
        'store.Book',
        on_delete=models.CASCADE,
        related_name='import_order_items'
    )
    quantity_ordered = models.IntegerField()
    quantity_received = models.IntegerField(default=0)
    unit_cost = models.DecimalField(max_digits=10, decimal_places=2)
    notes = models.TextField(blank=True, null=True)

    class Meta:
        db_table = 'store_import_order_item'
        verbose_name = 'Import Order Item'
        verbose_name_plural = 'Import Order Items'

    def __str__(self):
        return f"{self.book.title} x {self.quantity_ordered}"

    def get_subtotal(self):
        """Calculate item subtotal."""
        return self.quantity_ordered * self.unit_cost


class StockTransfer(TimeStampedModel):
    """
    Stock Transfer Model - Transfers between warehouses.
    """
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('in_transit', 'In Transit'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]

    transfer_number = models.CharField(max_length=50, unique=True)
    source_warehouse = models.ForeignKey(
        Warehouse,
        on_delete=models.CASCADE,
        related_name='outgoing_transfers'
    )
    destination_warehouse = models.ForeignKey(
        Warehouse,
        on_delete=models.CASCADE,
        related_name='incoming_transfers'
    )
    book = models.ForeignKey(
        'store.Book',
        on_delete=models.CASCADE,
        related_name='stock_transfers'
    )
    quantity = models.IntegerField()
    requested_by = models.ForeignKey(
        'store.Staff',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='requested_transfers'
    )
    approved_by = models.ForeignKey(
        'store.Staff',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='approved_transfers'
    )
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    transfer_date = models.DateField(blank=True, null=True)
    completion_date = models.DateField(blank=True, null=True)
    reason = models.TextField(blank=True, null=True)
    notes = models.TextField(blank=True, null=True)

    class Meta:
        db_table = 'store_stock_transfer'
        verbose_name = 'Stock Transfer'
        verbose_name_plural = 'Stock Transfers'
        ordering = ['-created_at']

    def __str__(self):
        return f"Transfer #{self.transfer_number}: {self.quantity} of {self.book.title}"


class ReturnRequestToSupplier(TimeStampedModel):
    """
    Return Request to Supplier Model - For returning defective/unwanted books.
    """
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('shipped', 'Shipped'),
        ('completed', 'Completed'),
        ('rejected', 'Rejected'),
    ]

    REASON_CHOICES = [
        ('defective', 'Defective'),
        ('damaged', 'Damaged'),
        ('wrong_item', 'Wrong Item'),
        ('overstock', 'Overstock'),
        ('other', 'Other'),
    ]

    request_number = models.CharField(max_length=50, unique=True)
    supplier = models.ForeignKey(
        Supplier,
        on_delete=models.CASCADE,
        related_name='return_requests'
    )
    import_order = models.ForeignKey(
        ImportOrder,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='return_requests'
    )
    book = models.ForeignKey(
        'store.Book',
        on_delete=models.CASCADE,
        related_name='supplier_return_requests'
    )
    quantity = models.IntegerField()
    reason = models.CharField(max_length=20, choices=REASON_CHOICES)
    reason_detail = models.TextField(blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    requested_by = models.ForeignKey(
        'store.Staff',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='supplier_return_requests'
    )
    request_date = models.DateField()
    response_date = models.DateField(blank=True, null=True)
    refund_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    notes = models.TextField(blank=True, null=True)

    class Meta:
        db_table = 'store_return_request_to_supplier'
        verbose_name = 'Return Request to Supplier'
        verbose_name_plural = 'Return Requests to Supplier'
        ordering = ['-created_at']

    def __str__(self):
        return f"Return #{self.request_number}"
