"""
User Models - All user-related models for the bookstore application.
Contains: UserAccount, Customer, CustomerProfile, MemberTier, Staff, Admin, 
         SalesStaff, WarehouseStaff, Shipper, GuestSession, Address
"""
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.hashers import make_password, check_password
from store.models.base import TimeStampedModel, Person


class UserAccount(AbstractUser):
    """
    Custom User Account that extends Django's AbstractUser.
    Used for authentication across the system.
    """
    phone = models.CharField(max_length=20, blank=True, null=True)
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)
    is_customer = models.BooleanField(default=False)
    is_staff_member = models.BooleanField(default=False)

    class Meta:
        db_table = 'store_user_account'
        verbose_name = 'User Account'
        verbose_name_plural = 'User Accounts'

    def __str__(self):
        return self.username


class MemberTier(TimeStampedModel):
    """
    Member Tier Model - Represents membership levels (Gold, Silver, etc.).
    Defines benefits and discount percentages for each tier.
    """
    TIER_CHOICES = [
        ('bronze', 'Bronze'),
        ('silver', 'Silver'),
        ('gold', 'Gold'),
        ('platinum', 'Platinum'),
    ]

    name = models.CharField(max_length=50, choices=TIER_CHOICES, unique=True)
    min_points = models.IntegerField(default=0)
    discount_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    description = models.TextField(blank=True, null=True)
    benefits = models.TextField(blank=True, null=True)

    class Meta:
        db_table = 'store_member_tier'
        verbose_name = 'Member Tier'
        verbose_name_plural = 'Member Tiers'
        ordering = ['min_points']

    def __str__(self):
        return self.get_name_display()


class Customer(Person, TimeStampedModel):
    """
    Customer Model - Represents a customer of the bookstore.
    Inherits from Person abstract model.
    """
    user = models.OneToOneField(
        'store.UserAccount',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='customer'
    )
    password = models.CharField(max_length=255, blank=True, null=True)
    date_of_birth = models.DateField(blank=True, null=True)
    loyalty_points = models.IntegerField(default=0)
    member_tier = models.ForeignKey(
        MemberTier,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='customers'
    )
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = 'store_customer'
        verbose_name = 'Customer'
        verbose_name_plural = 'Customers'

    def __str__(self):
        return self.name

    def set_password(self, raw_password):
        """Hash and set the customer's password."""
        self.password = make_password(raw_password)

    def verify_password(self, raw_password):
        """Verify the customer's password."""
        return check_password(raw_password, self.password)

    def add_loyalty_points(self, points):
        """Add loyalty points to customer account."""
        self.loyalty_points += points
        self.save()


class CustomerProfile(TimeStampedModel):
    """
    Customer Profile - Extended information for customers (OneToOne with Customer).
    """
    customer = models.OneToOneField(
        Customer,
        on_delete=models.CASCADE,
        related_name='profile'
    )
    bio = models.TextField(blank=True, null=True)
    avatar = models.ImageField(upload_to='customer_avatars/', blank=True, null=True)
    preferred_language = models.CharField(max_length=10, default='en')
    preferred_currency = models.CharField(max_length=10, default='USD')
    newsletter_subscribed = models.BooleanField(default=False)
    marketing_consent = models.BooleanField(default=False)

    class Meta:
        db_table = 'store_customer_profile'
        verbose_name = 'Customer Profile'
        verbose_name_plural = 'Customer Profiles'

    def __str__(self):
        return f"Profile of {self.customer.name}"


class Staff(Person, TimeStampedModel):
    """
    Staff Model - Base model for all staff members.
    Inherits from Person abstract model.
    """
    user = models.OneToOneField(
        'store.UserAccount',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='staff'
    )
    password = models.CharField(max_length=255, blank=True, null=True)
    employee_id = models.CharField(max_length=50, unique=True)
    hire_date = models.DateField(blank=True, null=True)
    salary = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = 'store_staff'
        verbose_name = 'Staff'
        verbose_name_plural = 'Staff Members'

    def __str__(self):
        return f"{self.name} ({self.employee_id})"

    def set_password(self, raw_password):
        """Hash and set the staff's password."""
        self.password = make_password(raw_password)

    def verify_password(self, raw_password):
        """Verify the staff's password."""
        return check_password(raw_password, self.password)


class Admin(Staff):
    """
    Admin Model - Administrator staff with full system access.
    Inherits from Staff.
    """
    access_level = models.CharField(max_length=50, default='full')
    can_manage_staff = models.BooleanField(default=True)
    can_manage_system = models.BooleanField(default=True)

    class Meta:
        db_table = 'store_admin'
        verbose_name = 'Admin'
        verbose_name_plural = 'Admins'

    def __str__(self):
        return f"Admin: {self.name}"


class SalesStaff(Staff):
    """
    Sales Staff Model - Staff responsible for sales operations.
    Inherits from Staff.
    """
    commission_rate = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    sales_target = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    total_sales = models.DecimalField(max_digits=12, decimal_places=2, default=0)

    class Meta:
        db_table = 'store_sales_staff'
        verbose_name = 'Sales Staff'
        verbose_name_plural = 'Sales Staff'

    def __str__(self):
        return f"Sales: {self.name}"

    def calculate_commission(self):
        """Calculate commission based on total sales."""
        return self.total_sales * (self.commission_rate / 100)


class WarehouseStaff(Staff):
    """
    Warehouse Staff Model - Staff responsible for inventory management.
    Inherits from Staff.
    """
    warehouse = models.ForeignKey(
        'store.Warehouse',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='staff_members'
    )
    can_approve_transfers = models.BooleanField(default=False)
    certifications = models.TextField(blank=True, null=True)

    class Meta:
        db_table = 'store_warehouse_staff'
        verbose_name = 'Warehouse Staff'
        verbose_name_plural = 'Warehouse Staff'

    def __str__(self):
        return f"Warehouse: {self.name}"


class Shipper(Staff):
    """
    Shipper Model - Staff responsible for delivering orders.
    Inherits from Staff.
    """
    vehicle_type = models.CharField(max_length=50, blank=True, null=True)
    license_number = models.CharField(max_length=50, blank=True, null=True)
    delivery_zone = models.CharField(max_length=100, blank=True, null=True)
    current_status = models.CharField(
        max_length=20,
        choices=[
            ('available', 'Available'),
            ('on_delivery', 'On Delivery'),
            ('off_duty', 'Off Duty'),
        ],
        default='available'
    )

    class Meta:
        db_table = 'store_shipper'
        verbose_name = 'Shipper'
        verbose_name_plural = 'Shippers'

    def __str__(self):
        return f"Shipper: {self.name}"


class GuestSession(TimeStampedModel):
    """
    Guest Session Model - Tracks anonymous/guest user sessions.
    """
    session_key = models.CharField(max_length=255, unique=True)
    ip_address = models.GenericIPAddressField(blank=True, null=True)
    user_agent = models.TextField(blank=True, null=True)
    expires_at = models.DateTimeField()
    converted_to_customer = models.ForeignKey(
        Customer,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='previous_sessions'
    )

    class Meta:
        db_table = 'store_guest_session'
        verbose_name = 'Guest Session'
        verbose_name_plural = 'Guest Sessions'

    def __str__(self):
        return f"Session: {self.session_key[:20]}..."


class Address(TimeStampedModel):
    """
    Address Model - Stores addresses for customers and orders.
    """
    ADDRESS_TYPE_CHOICES = [
        ('billing', 'Billing'),
        ('shipping', 'Shipping'),
        ('both', 'Both'),
    ]

    customer = models.ForeignKey(
        Customer,
        on_delete=models.CASCADE,
        related_name='addresses'
    )
    address_type = models.CharField(max_length=20, choices=ADDRESS_TYPE_CHOICES, default='shipping')
    full_name = models.CharField(max_length=255)
    phone = models.CharField(max_length=20)
    street_address = models.CharField(max_length=255)
    street_address_2 = models.CharField(max_length=255, blank=True, null=True)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    postal_code = models.CharField(max_length=20)
    country = models.CharField(max_length=100, default='Vietnam')
    is_default = models.BooleanField(default=False)

    class Meta:
        db_table = 'store_address'
        verbose_name = 'Address'
        verbose_name_plural = 'Addresses'

    def __str__(self):
        return f"{self.full_name}, {self.street_address}, {self.city}"

    def get_full_address(self):
        """Return formatted full address."""
        parts = [
            self.street_address,
            self.street_address_2,
            self.city,
            self.state,
            self.postal_code,
            self.country
        ]
        return ', '.join(filter(None, parts))
