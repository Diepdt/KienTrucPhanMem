# Models Package - Aggregates all domain models
# Import all models from domain packages to make them available at store.models level

# Book domain
from store.models.book.book import Book
from store.models.book.category import Category
from store.models.book.author import Author
from store.models.book.publisher import Publisher

# Customer domain
from store.models.customer.customer import Customer
from store.models.customer.rating import Rating
from store.models.customer.address import Address
from store.models.customer.review import Review
from store.models.customer.wishlist import Wishlist, WishlistItem

# Staff domain
from store.models.staff.staff import Staff

# Order domain
from store.models.order.cart import Cart
from store.models.order.cart_item import CartItem
from store.models.order.order import Order, OrderItem
from store.models.order.shipping import Shipping
from store.models.order.payment import Payment
from store.models.order.order_history import OrderHistory
from store.models.order.refund import Refund

# Promotion domain
from store.models.promotion.promotion import Promotion
from store.models.promotion.coupon import Coupon

# Inventory domain
from store.models.inventory.inventory import Inventory, InventoryLog

# Notification domain
from store.models.notification.notification import Notification

__all__ = [
    # Book domain (4 classes)
    'Book',
    'Category',
    'Author',
    'Publisher',
    
    # Customer domain (5 classes)
    'Customer',
    'Rating',
    'Address',
    'Review',
    'Wishlist',
    'WishlistItem',
    
    # Staff domain (1 class)
    'Staff',
    
    # Order domain (8 classes)
    'Cart',
    'CartItem',
    'Order',
    'OrderItem',
    'Shipping',
    'Payment',
    'OrderHistory',
    'Refund',
    
    # Promotion domain (2 classes)
    'Promotion',
    'Coupon',
    
    # Inventory domain (2 classes)
    'Inventory',
    'InventoryLog',
    
    # Notification domain (1 class)
    'Notification',
]
