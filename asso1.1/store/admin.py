from django.contrib import admin
from store.models import (
    Book, Category, Author, Publisher,
    Customer, Rating, Address, Review, Wishlist, WishlistItem,
    Staff,
    Cart, CartItem, Order, OrderItem, Shipping, Payment, OrderHistory, Refund,
    Promotion, Coupon,
    Inventory, InventoryLog,
    Notification
)


# ============== Book Domain ==============
@admin.register(Author)
class AuthorAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'email', 'birth_date', 'get_books_count')
    search_fields = ('name', 'email')
    ordering = ('name',)

    def get_books_count(self, obj):
        return obj.books.count()
    get_books_count.short_description = 'Books Count'


@admin.register(Publisher)
class PublisherAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'city', 'country', 'email', 'get_books_count')
    search_fields = ('name', 'city', 'country')
    list_filter = ('country',)
    ordering = ('name',)

    def get_books_count(self, obj):
        return obj.books.count()
    get_books_count.short_description = 'Books Count'


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'type', 'get_books_count')
    search_fields = ('type',)
    ordering = ('type',)
    
    def get_books_count(self, obj):
        return obj.books.count()
    get_books_count.short_description = 'Books Count'


@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'author', 'category', 'price', 'stock_quantity')
    list_filter = ('author', 'category')
    search_fields = ('title', 'author')
    ordering = ('title',)


@admin.register(Address)
class AddressAdmin(admin.ModelAdmin):
    list_display = ('id', 'customer', 'num', 'street', 'city')
    search_fields = ('customer__name', 'street', 'city')
    ordering = ('city', 'street')


@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'email')
    search_fields = ('name', 'email')
    ordering = ('name',)


@admin.register(Rating)
class RatingAdmin(admin.ModelAdmin):
    list_display = ('id', 'customer', 'book', 'score', 'comment', 'created_at')
    list_filter = ('score', 'created_at')
    search_fields = ('customer__name', 'book__title', 'comment')


@admin.register(Staff)
class StaffAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'email', 'role')
    list_filter = ('role',)
    search_fields = ('name', 'email')
    ordering = ('name',)


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ('id', 'customer', 'session_key', 'created_at', 'updated_at')
    list_filter = ('created_at',)
    search_fields = ('customer__name', 'session_key')


@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    list_display = ('id', 'cart', 'book', 'quantity', 'added_at')
    list_filter = ('added_at',)
    search_fields = ('book__title',)


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ('book', 'quantity', 'price')


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'customer', 'staff', 'status', 'total', 'created_at')
    list_filter = ('status', 'staff', 'created_at')
    search_fields = ('customer__name', 'staff__name')
    inlines = [OrderItemInline]
    ordering = ('-created_at',)


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ('id', 'order', 'book', 'quantity', 'price')
    list_filter = ('order__status',)
    search_fields = ('book__title', 'order__id')


@admin.register(Shipping)
class ShippingAdmin(admin.ModelAdmin):
    list_display = ('id', 'method', 'address', 'city', 'cost', 'created_at')
    list_filter = ('method', 'country')
    search_fields = ('address', 'city')


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('id', 'method', 'amount', 'status', 'transaction_id', 'created_at')
    list_filter = ('method', 'status', 'created_at')
    search_fields = ('transaction_id',)


# ============== New Domain Models ==============

@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('id', 'customer', 'book', 'rating', 'title', 'is_verified_purchase', 'is_approved', 'created_at')
    list_filter = ('rating', 'is_verified_purchase', 'is_approved', 'created_at')
    search_fields = ('customer__name', 'book__title', 'title', 'content')
    ordering = ('-created_at',)


@admin.register(Wishlist)
class WishlistAdmin(admin.ModelAdmin):
    list_display = ('id', 'customer', 'name', 'is_public', 'get_items_count', 'created_at')
    search_fields = ('customer__name', 'name')
    list_filter = ('is_public',)


@admin.register(WishlistItem)
class WishlistItemAdmin(admin.ModelAdmin):
    list_display = ('id', 'wishlist', 'book', 'priority', 'added_at')
    list_filter = ('priority',)
    search_fields = ('book__title', 'wishlist__customer__name')


@admin.register(Promotion)
class PromotionAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'discount_type', 'discount_percent', 'discount_amount', 'start_date', 'end_date', 'is_active')
    list_filter = ('discount_type', 'is_active', 'start_date', 'end_date')
    search_fields = ('name', 'description')
    ordering = ('-start_date',)


@admin.register(Coupon)
class CouponAdmin(admin.ModelAdmin):
    list_display = ('id', 'code', 'discount_type', 'discount_percent', 'discount_amount', 'valid_from', 'valid_to', 'current_uses', 'max_uses', 'is_active')
    list_filter = ('discount_type', 'is_active', 'valid_from', 'valid_to')
    search_fields = ('code', 'description')
    ordering = ('-created_at',)


@admin.register(Inventory)
class InventoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'book', 'quantity', 'reorder_level', 'location', 'needs_reorder', 'last_restocked')
    list_filter = ('location',)
    search_fields = ('book__title',)

    def needs_reorder(self, obj):
        return obj.needs_reorder()
    needs_reorder.boolean = True
    needs_reorder.short_description = 'Needs Reorder'


@admin.register(InventoryLog)
class InventoryLogAdmin(admin.ModelAdmin):
    list_display = ('id', 'inventory', 'action', 'quantity', 'performed_by', 'created_at')
    list_filter = ('action', 'created_at')
    search_fields = ('inventory__book__title', 'notes')
    ordering = ('-created_at',)


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('id', 'recipient_type', 'customer', 'staff', 'notification_type', 'title', 'is_read', 'created_at')
    list_filter = ('recipient_type', 'notification_type', 'is_read', 'created_at')
    search_fields = ('title', 'message', 'customer__name', 'staff__name')
    ordering = ('-created_at',)


@admin.register(OrderHistory)
class OrderHistoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'order', 'old_status', 'new_status', 'changed_by', 'created_at')
    list_filter = ('new_status', 'created_at')
    search_fields = ('order__id', 'notes')
    ordering = ('-created_at',)


@admin.register(Refund)
class RefundAdmin(admin.ModelAdmin):
    list_display = ('id', 'order', 'amount', 'reason', 'status', 'processed_by', 'created_at')
    list_filter = ('status', 'reason', 'created_at')
    search_fields = ('order__id', 'reason_details')
    ordering = ('-created_at',)
