"""
Marketing Models - All marketing and content related models.
Contains: Promotion, Coupon, Notification, Banner, BlogPost, SystemConfig
"""
from django.db import models
from decimal import Decimal
from store.models.base import TimeStampedModel


class Promotion(TimeStampedModel):
    """
    Promotion Model - Marketing promotions and campaigns.
    """
    TYPE_CHOICES = [
        ('percentage', 'Percentage Discount'),
        ('fixed', 'Fixed Amount Discount'),
        ('buy_x_get_y', 'Buy X Get Y'),
        ('free_shipping', 'Free Shipping'),
        ('bundle', 'Bundle Deal'),
    ]

    name = models.CharField(max_length=255)
    code = models.CharField(max_length=50, unique=True)
    description = models.TextField(blank=True, null=True)
    promotion_type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    discount_value = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    min_purchase_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    max_discount_amount = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    is_active = models.BooleanField(default=True)
    usage_limit = models.IntegerField(blank=True, null=True)
    used_count = models.IntegerField(default=0)
    applicable_categories = models.ManyToManyField(
        'store.Category',
        blank=True,
        related_name='promotions'
    )
    applicable_books = models.ManyToManyField(
        'store.Book',
        blank=True,
        related_name='promotions'
    )
    banner_image = models.ImageField(upload_to='promotions/', blank=True, null=True)

    class Meta:
        db_table = 'store_promotion'
        verbose_name = 'Promotion'
        verbose_name_plural = 'Promotions'
        ordering = ['-start_date']

    def __str__(self):
        return self.name

    def is_valid(self):
        """Check if promotion is currently valid."""
        from django.utils import timezone
        now = timezone.now()
        return (
            self.is_active and
            self.start_date <= now <= self.end_date and
            (self.usage_limit is None or self.used_count < self.usage_limit)
        )


class Coupon(TimeStampedModel):
    """
    Coupon Model - Discount coupons for customers.
    """
    TYPE_CHOICES = [
        ('percentage', 'Percentage Discount'),
        ('fixed', 'Fixed Amount Discount'),
    ]

    code = models.CharField(max_length=50, unique=True)
    description = models.TextField(blank=True, null=True)
    coupon_type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    discount_value = models.DecimalField(max_digits=10, decimal_places=2)
    min_purchase_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    max_discount_amount = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    is_active = models.BooleanField(default=True)
    usage_limit = models.IntegerField(blank=True, null=True)
    usage_limit_per_user = models.IntegerField(default=1)
    used_count = models.IntegerField(default=0)
    applicable_to_all = models.BooleanField(default=True)
    applicable_categories = models.ManyToManyField(
        'store.Category',
        blank=True,
        related_name='coupons'
    )
    applicable_customers = models.ManyToManyField(
        'store.Customer',
        blank=True,
        related_name='available_coupons'
    )

    class Meta:
        db_table = 'store_coupon'
        verbose_name = 'Coupon'
        verbose_name_plural = 'Coupons'
        ordering = ['-created_at']

    def __str__(self):
        return self.code

    def is_valid(self):
        """Check if coupon is currently valid."""
        from django.utils import timezone
        now = timezone.now()
        return (
            self.is_active and
            self.start_date <= now <= self.end_date and
            (self.usage_limit is None or self.used_count < self.usage_limit)
        )

    def calculate_discount(self, subtotal):
        """Calculate discount amount for given subtotal."""
        if subtotal < self.min_purchase_amount:
            return Decimal('0')
        
        if self.coupon_type == 'percentage':
            discount = subtotal * (self.discount_value / 100)
        else:
            discount = self.discount_value
        
        if self.max_discount_amount:
            discount = min(discount, self.max_discount_amount)
        
        return discount


class Notification(TimeStampedModel):
    """
    Notification Model - System notifications for users.
    """
    TYPE_CHOICES = [
        ('order', 'Order Update'),
        ('promotion', 'Promotion'),
        ('system', 'System'),
        ('reminder', 'Reminder'),
        ('news', 'News'),
    ]

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
    notification_type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    is_read = models.BooleanField(default=False)
    read_at = models.DateTimeField(blank=True, null=True)
    link = models.URLField(blank=True, null=True)
    data = models.JSONField(blank=True, null=True)  # Additional notification data

    class Meta:
        db_table = 'store_notification'
        verbose_name = 'Notification'
        verbose_name_plural = 'Notifications'
        ordering = ['-created_at']

    def __str__(self):
        return self.title

    def mark_as_read(self):
        """Mark notification as read."""
        from django.utils import timezone
        self.is_read = True
        self.read_at = timezone.now()
        self.save()


class Banner(TimeStampedModel):
    """
    Banner Model - Homepage banners and advertisements.
    """
    POSITION_CHOICES = [
        ('homepage_main', 'Homepage Main'),
        ('homepage_side', 'Homepage Side'),
        ('category_top', 'Category Page Top'),
        ('product_side', 'Product Page Side'),
    ]

    title = models.CharField(max_length=255)
    subtitle = models.CharField(max_length=255, blank=True, null=True)
    image = models.ImageField(upload_to='banners/')
    image_mobile = models.ImageField(upload_to='banners/mobile/', blank=True, null=True)
    link = models.URLField(blank=True, null=True)
    position = models.CharField(max_length=30, choices=POSITION_CHOICES)
    is_active = models.BooleanField(default=True)
    display_order = models.IntegerField(default=0)
    start_date = models.DateTimeField(blank=True, null=True)
    end_date = models.DateTimeField(blank=True, null=True)
    click_count = models.IntegerField(default=0)
    view_count = models.IntegerField(default=0)

    class Meta:
        db_table = 'store_banner'
        verbose_name = 'Banner'
        verbose_name_plural = 'Banners'
        ordering = ['display_order', '-created_at']

    def __str__(self):
        return self.title

    def increment_click(self):
        """Increment click count."""
        self.click_count += 1
        self.save()

    def increment_view(self):
        """Increment view count."""
        self.view_count += 1
        self.save()


class BlogPost(TimeStampedModel):
    """
    Blog Post Model - Blog articles and content.
    """
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('published', 'Published'),
        ('archived', 'Archived'),
    ]

    title = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, unique=True)
    excerpt = models.TextField(blank=True, null=True)
    content = models.TextField()
    featured_image = models.ImageField(upload_to='blog/', blank=True, null=True)
    author = models.ForeignKey(
        'store.Staff',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='blog_posts'
    )
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    published_at = models.DateTimeField(blank=True, null=True)
    view_count = models.IntegerField(default=0)
    is_featured = models.BooleanField(default=False)
    meta_title = models.CharField(max_length=255, blank=True, null=True)
    meta_description = models.TextField(blank=True, null=True)
    tags = models.ManyToManyField(
        'store.Tag',
        blank=True,
        related_name='blog_posts'
    )
    related_books = models.ManyToManyField(
        'store.Book',
        blank=True,
        related_name='blog_posts'
    )

    class Meta:
        db_table = 'store_blog_post'
        verbose_name = 'Blog Post'
        verbose_name_plural = 'Blog Posts'
        ordering = ['-published_at']

    def __str__(self):
        return self.title

    def publish(self):
        """Publish the blog post."""
        from django.utils import timezone
        self.status = 'published'
        self.published_at = timezone.now()
        self.save()


class SystemConfig(TimeStampedModel):
    """
    System Config Model - System-wide configuration settings.
    """
    key = models.CharField(max_length=100, unique=True)
    value = models.TextField()
    description = models.TextField(blank=True, null=True)
    value_type = models.CharField(
        max_length=20,
        choices=[
            ('string', 'String'),
            ('integer', 'Integer'),
            ('decimal', 'Decimal'),
            ('boolean', 'Boolean'),
            ('json', 'JSON'),
        ],
        default='string'
    )
    is_public = models.BooleanField(default=False)  # Can be exposed to frontend
    category = models.CharField(max_length=100, blank=True, null=True)

    class Meta:
        db_table = 'store_system_config'
        verbose_name = 'System Config'
        verbose_name_plural = 'System Configs'
        ordering = ['category', 'key']

    def __str__(self):
        return f"{self.key}: {self.value[:50]}"

    def get_typed_value(self):
        """Return value converted to appropriate type."""
        import json
        if self.value_type == 'integer':
            return int(self.value)
        elif self.value_type == 'decimal':
            return Decimal(self.value)
        elif self.value_type == 'boolean':
            return self.value.lower() in ('true', '1', 'yes')
        elif self.value_type == 'json':
            return json.loads(self.value)
        return self.value

    @classmethod
    def get_value(cls, key, default=None):
        """Get config value by key."""
        try:
            config = cls.objects.get(key=key)
            return config.get_typed_value()
        except cls.DoesNotExist:
            return default
