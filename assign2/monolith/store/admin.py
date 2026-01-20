from django.contrib import admin
from store.models import (
    Book, Customer, Rating, Staff,
    Cart, CartItem, Order, OrderItem,
    Shipping, Payment
)


@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'author', 'price', 'stock_quantity')
    list_filter = ('author',)
    search_fields = ('title', 'author')
    ordering = ('title',)


@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'email')
    search_fields = ('name', 'email')
    ordering = ('name',)


@admin.register(Rating)
class RatingAdmin(admin.ModelAdmin):
    list_display = ('id', 'customer', 'book', 'score', 'created_at')
    list_filter = ('score', 'created_at')
    search_fields = ('customer__name', 'book__title')


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
    list_display = ('id', 'customer', 'status', 'total_amount', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('customer__name',)
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
