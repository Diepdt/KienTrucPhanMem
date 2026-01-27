from django.db import models
from django.utils import timezone


class Inventory(models.Model):
    """
    Inventory Model - Tracks book inventory and stock movements.
    
    Attributes:
        id: Auto-generated primary key
        book: Foreign key to Book
        quantity: Current stock quantity
        reorder_level: Minimum stock level before reorder
        reorder_quantity: Quantity to reorder
        location: Storage location
        last_restocked: Last restock date
    """
    book = models.OneToOneField(
        'store.Book',
        on_delete=models.CASCADE,
        related_name='inventory'
    )
    quantity = models.PositiveIntegerField(default=0)
    reorder_level = models.PositiveIntegerField(default=10)
    reorder_quantity = models.PositiveIntegerField(default=50)
    location = models.CharField(max_length=100, blank=True, null=True)
    last_restocked = models.DateTimeField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'store_inventory'
        verbose_name = 'Inventory'
        verbose_name_plural = 'Inventories'

    def __str__(self):
        return f"Inventory for {self.book.title}: {self.quantity} units"

    def needs_reorder(self):
        """Check if stock is below reorder level."""
        return self.quantity <= self.reorder_level

    def restock(self, quantity):
        """Add stock to inventory."""
        self.quantity += quantity
        self.last_restocked = timezone.now()
        self.save()
        # Create inventory log
        InventoryLog.objects.create(
            inventory=self,
            action='restock',
            quantity=quantity,
            notes=f"Restocked {quantity} units"
        )

    def reduce(self, quantity):
        """Reduce stock from inventory."""
        if quantity > self.quantity:
            raise ValueError("Insufficient stock")
        self.quantity -= quantity
        self.save()
        # Create inventory log
        InventoryLog.objects.create(
            inventory=self,
            action='sale',
            quantity=-quantity,
            notes=f"Reduced {quantity} units (sale)"
        )


class InventoryLog(models.Model):
    """
    InventoryLog Model - Logs all inventory movements.
    
    Attributes:
        id: Auto-generated primary key
        inventory: Foreign key to Inventory
        action: Type of action (restock, sale, adjustment, return)
        quantity: Quantity changed (positive or negative)
        notes: Additional notes
    """
    ACTION_CHOICES = [
        ('restock', 'Restock'),
        ('sale', 'Sale'),
        ('adjustment', 'Adjustment'),
        ('return', 'Return'),
        ('damaged', 'Damaged'),
    ]

    inventory = models.ForeignKey(
        Inventory,
        on_delete=models.CASCADE,
        related_name='logs'
    )
    action = models.CharField(max_length=20, choices=ACTION_CHOICES)
    quantity = models.IntegerField()  # Can be negative
    notes = models.TextField(blank=True, null=True)
    performed_by = models.ForeignKey(
        'store.Staff',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='inventory_actions'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'store_inventory_log'
        verbose_name = 'Inventory Log'
        verbose_name_plural = 'Inventory Logs'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.action}: {self.quantity} units for {self.inventory.book.title}"
