"""
Store Admin - Django Admin configuration for all 52 models.
"""
from django.contrib import admin
from store.models import (
    # Users & Roles
    UserAccount, Customer, CustomerProfile, MemberTier,
    Staff, Admin as AdminModel, SalesStaff, WarehouseStaff, Shipper,
    GuestSession, Address,
    
    # Products
    Category, Book, BookDetail, BookImage,
    Author, Translator, Publisher, Language, BookFormat, Series, Tag, BookTag,
    
    # Inventory & Supply Chain
    Supplier, Warehouse, Inventory,
    ImportOrder, ImportOrderItem, StockTransfer, ReturnRequestToSupplier,
    
    # Sales & Orders
    Cart, CartItem, Order, OrderItem, OrderStatusHistory,
    Wishlist, WishlistItem, Review, Rating,
    
    # Payment & Shipping
    Payment, PaymentMethod, ShippingMethod, Shipment, RefundRequest,
    
    # Marketing & Content
    Promotion, Coupon, Notification, Banner, BlogPost, SystemConfig,
)


# ============================================================
# Users & Roles Admin
# ============================================================

@admin.register(UserAccount)
class UserAccountAdmin(admin.ModelAdmin):
    list_display = ('id', 'username', 'email', 'is_customer', 'is_staff_member', 'is_active')
    list_filter = ('is_customer', 'is_staff_member', 'is_active')
    search_fields = ('username', 'email')
    ordering = ('username',)


@admin.register(MemberTier)
class MemberTierAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'min_points', 'discount_percentage')
    ordering = ('min_points',)


@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'email', 'phone', 'loyalty_points', 'member_tier', 'is_active')
    list_filter = ('member_tier', 'is_active')
    search_fields = ('name', 'email')
    ordering = ('name',)


@admin.register(CustomerProfile)
class CustomerProfileAdmin(admin.ModelAdmin):
    list_display = ('id', 'customer', 'preferred_language', 'newsletter_subscribed')
    list_filter = ('preferred_language', 'newsletter_subscribed')
    search_fields = ('customer__name',)


@admin.register(Staff)
class StaffAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'email', 'employee_id', 'is_active')
    list_filter = ('is_active',)
    search_fields = ('name', 'email', 'employee_id')
    ordering = ('name',)


@admin.register(AdminModel)
class AdminModelAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'email', 'access_level', 'can_manage_staff')
    list_filter = ('access_level',)
    search_fields = ('name', 'email')


@admin.register(SalesStaff)
class SalesStaffAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'email', 'commission_rate', 'total_sales')
    search_fields = ('name', 'email')


@admin.register(WarehouseStaff)
class WarehouseStaffAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'email', 'warehouse', 'can_approve_transfers')
    list_filter = ('warehouse', 'can_approve_transfers')
    search_fields = ('name', 'email')


@admin.register(Shipper)
class ShipperAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'email', 'vehicle_type', 'delivery_zone', 'current_status')
    list_filter = ('current_status', 'delivery_zone')
    search_fields = ('name', 'email')


@admin.register(GuestSession)
class GuestSessionAdmin(admin.ModelAdmin):
    list_display = ('id', 'session_key', 'ip_address', 'expires_at', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('session_key', 'ip_address')


@admin.register(Address)
class AddressAdmin(admin.ModelAdmin):
    list_display = ('id', 'customer', 'address_type', 'city', 'country', 'is_default')
    list_filter = ('address_type', 'country', 'is_default')
    search_fields = ('customer__name', 'street_address', 'city')


# ============================================================
# Products Admin
# ============================================================

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'slug', 'parent', 'is_active', 'display_order')
    list_filter = ('is_active', 'parent')
    search_fields = ('name', 'slug')
    prepopulated_fields = {'slug': ('name',)}
    ordering = ('display_order', 'name')


@admin.register(Author)
class AuthorAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'nationality', 'birth_date')
    search_fields = ('name', 'nationality')
    ordering = ('name',)


@admin.register(Translator)
class TranslatorAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'languages')
    search_fields = ('name',)
    ordering = ('name',)


@admin.register(Publisher)
class PublisherAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'email', 'phone')
    search_fields = ('name', 'email')
    ordering = ('name',)


@admin.register(Language)
class LanguageAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'code')
    search_fields = ('name', 'code')
    ordering = ('name',)


@admin.register(BookFormat)
class BookFormatAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'description')
    ordering = ('name',)


@admin.register(Series)
class SeriesAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'total_books', 'is_complete')
    list_filter = ('is_complete',)
    search_fields = ('name',)


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'slug')
    search_fields = ('name', 'slug')
    prepopulated_fields = {'slug': ('name',)}


class BookImageInline(admin.TabularInline):
    model = BookImage
    extra = 1


class BookDetailInline(admin.StackedInline):
    model = BookDetail
    extra = 0


@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'category', 'price', 'stock_quantity', 'is_active', 'is_featured')
    list_filter = ('category', 'is_active', 'is_featured', 'language', 'book_format')
    search_fields = ('title', 'isbn')
    prepopulated_fields = {'slug': ('title',)}
    inlines = [BookDetailInline, BookImageInline]
    ordering = ('-created_at',)


@admin.register(BookDetail)
class BookDetailAdmin(admin.ModelAdmin):
    list_display = ('id', 'book', 'pages', 'edition')
    search_fields = ('book__title',)


@admin.register(BookImage)
class BookImageAdmin(admin.ModelAdmin):
    list_display = ('id', 'book', 'is_primary', 'display_order')
    list_filter = ('is_primary',)
    search_fields = ('book__title',)


@admin.register(BookTag)
class BookTagAdmin(admin.ModelAdmin):
    list_display = ('id', 'book', 'tag')
    search_fields = ('book__title', 'tag__name')


# ============================================================
# Inventory & Supply Chain Admin
# ============================================================

@admin.register(Supplier)
class SupplierAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'code', 'contact_person', 'email', 'is_active')
    list_filter = ('is_active', 'country')
    search_fields = ('name', 'code', 'email')
    ordering = ('name',)


@admin.register(Warehouse)
class WarehouseAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'code', 'city', 'is_active', 'is_primary')
    list_filter = ('is_active', 'is_primary', 'country')
    search_fields = ('name', 'code', 'city')


@admin.register(Inventory)
class InventoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'book', 'warehouse', 'quantity', 'min_stock_level', 'reorder_point')
    list_filter = ('warehouse',)
    search_fields = ('book__title', 'warehouse__name')


class ImportOrderItemInline(admin.TabularInline):
    model = ImportOrderItem
    extra = 1


@admin.register(ImportOrder)
class ImportOrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'order_number', 'supplier', 'warehouse', 'status', 'total_amount', 'order_date')
    list_filter = ('status', 'supplier', 'warehouse')
    search_fields = ('order_number',)
    inlines = [ImportOrderItemInline]
    ordering = ('-created_at',)


@admin.register(ImportOrderItem)
class ImportOrderItemAdmin(admin.ModelAdmin):
    list_display = ('id', 'import_order', 'book', 'quantity_ordered', 'quantity_received', 'unit_cost')
    search_fields = ('book__title', 'import_order__order_number')


@admin.register(StockTransfer)
class StockTransferAdmin(admin.ModelAdmin):
    list_display = ('id', 'transfer_number', 'source_warehouse', 'destination_warehouse', 'book', 'quantity', 'status')
    list_filter = ('status', 'source_warehouse', 'destination_warehouse')
    search_fields = ('transfer_number', 'book__title')


@admin.register(ReturnRequestToSupplier)
class ReturnRequestToSupplierAdmin(admin.ModelAdmin):
    list_display = ('id', 'request_number', 'supplier', 'book', 'quantity', 'reason', 'status')
    list_filter = ('status', 'reason', 'supplier')
    search_fields = ('request_number', 'book__title')


# ============================================================
# Sales & Orders Admin
# ============================================================

class CartItemInline(admin.TabularInline):
    model = CartItem
    extra = 0


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ('id', 'customer', 'guest_session', 'coupon', 'created_at')
    search_fields = ('customer__name',)
    inlines = [CartItemInline]


@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    list_display = ('id', 'cart', 'book', 'quantity', 'price_at_add')
    search_fields = ('book__title',)


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ('book', 'quantity', 'unit_price')


class OrderStatusHistoryInline(admin.TabularInline):
    model = OrderStatusHistory
    extra = 0
    readonly_fields = ('status', 'changed_by', 'created_at')


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'order_number', 'customer', 'status', 'total', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('order_number', 'customer__name')
    inlines = [OrderItemInline, OrderStatusHistoryInline]
    ordering = ('-created_at',)


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ('id', 'order', 'book', 'quantity', 'unit_price')
    search_fields = ('order__order_number', 'book__title')


@admin.register(OrderStatusHistory)
class OrderStatusHistoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'order', 'status', 'changed_by', 'created_at')
    list_filter = ('status',)
    search_fields = ('order__order_number',)


class WishlistItemInline(admin.TabularInline):
    model = WishlistItem
    extra = 0


@admin.register(Wishlist)
class WishlistAdmin(admin.ModelAdmin):
    list_display = ('id', 'customer', 'name', 'is_public')
    list_filter = ('is_public',)
    search_fields = ('customer__name', 'name')
    inlines = [WishlistItemInline]


@admin.register(WishlistItem)
class WishlistItemAdmin(admin.ModelAdmin):
    list_display = ('id', 'wishlist', 'book', 'priority', 'created_at')
    search_fields = ('book__title',)


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('id', 'customer', 'book', 'status', 'is_verified_purchase', 'helpful_votes', 'created_at')
    list_filter = ('status', 'is_verified_purchase')
    search_fields = ('customer__name', 'book__title', 'content')


@admin.register(Rating)
class RatingAdmin(admin.ModelAdmin):
    list_display = ('id', 'customer', 'book', 'score', 'created_at')
    list_filter = ('score',)
    search_fields = ('customer__name', 'book__title')


# ============================================================
# Payment & Shipping Admin
# ============================================================

@admin.register(PaymentMethod)
class PaymentMethodAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'display_name', 'processing_fee', 'is_active')
    list_filter = ('is_active',)
    ordering = ('name',)


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('id', 'order', 'payment_method', 'amount', 'status', 'paid_at')
    list_filter = ('status', 'payment_method')
    search_fields = ('order__order_number', 'transaction_id')


@admin.register(ShippingMethod)
class ShippingMethodAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'code', 'base_cost', 'estimated_days_min', 'estimated_days_max', 'is_active')
    list_filter = ('is_active',)
    ordering = ('base_cost',)


@admin.register(Shipment)
class ShipmentAdmin(admin.ModelAdmin):
    list_display = ('id', 'order', 'shipping_method', 'shipper', 'tracking_number', 'status', 'shipped_at')
    list_filter = ('status', 'shipping_method')
    search_fields = ('order__order_number', 'tracking_number')


@admin.register(RefundRequest)
class RefundRequestAdmin(admin.ModelAdmin):
    list_display = ('id', 'request_number', 'order', 'customer', 'reason', 'status', 'refund_amount')
    list_filter = ('status', 'reason')
    search_fields = ('request_number', 'order__order_number', 'customer__name')


# ============================================================
# Marketing & Content Admin
# ============================================================

@admin.register(Promotion)
class PromotionAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'code', 'promotion_type', 'discount_value', 'start_date', 'end_date', 'is_active')
    list_filter = ('promotion_type', 'is_active')
    search_fields = ('name', 'code')


@admin.register(Coupon)
class CouponAdmin(admin.ModelAdmin):
    list_display = ('id', 'code', 'coupon_type', 'discount_value', 'start_date', 'end_date', 'is_active', 'used_count')
    list_filter = ('coupon_type', 'is_active')
    search_fields = ('code',)


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'notification_type', 'customer', 'staff', 'is_read', 'created_at')
    list_filter = ('notification_type', 'is_read')
    search_fields = ('title', 'message')


@admin.register(Banner)
class BannerAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'position', 'is_active', 'display_order', 'click_count', 'view_count')
    list_filter = ('position', 'is_active')
    search_fields = ('title',)


@admin.register(BlogPost)
class BlogPostAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'author', 'status', 'published_at', 'view_count', 'is_featured')
    list_filter = ('status', 'is_featured', 'author')
    search_fields = ('title', 'content')
    prepopulated_fields = {'slug': ('title',)}


@admin.register(SystemConfig)
class SystemConfigAdmin(admin.ModelAdmin):
    list_display = ('id', 'key', 'value', 'value_type', 'category', 'is_public')
    list_filter = ('value_type', 'category', 'is_public')
    search_fields = ('key', 'description')
