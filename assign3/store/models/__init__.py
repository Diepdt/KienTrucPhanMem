"""
Models Package - Aggregates all domain models for the bookstore application.
Total: 52 Models for Assignment 03 Analysis Class Diagram

Import all models from domain packages to make them available at store.models level
"""

# ============================================================
# 1. Abstract Models (2 classes) - base.py
# ============================================================
from store.models.base import (
    TimeStampedModel,
    Person,
)

# ============================================================
# 2. Users & Roles (11 classes) - user.py
# ============================================================
from store.models.user import (
    UserAccount,
    Customer,
    CustomerProfile,
    MemberTier,
    Staff,
    Admin,
    SalesStaff,
    WarehouseStaff,
    Shipper,
    GuestSession,
    Address,
)

# ============================================================
# 3. Products (12 classes) - product.py
# ============================================================
from store.models.product import (
    Category,
    Book,
    BookDetail,
    BookImage,
    Author,
    Translator,
    Publisher,
    Language,
    BookFormat,
    Series,
    Tag,
    BookTag,
)

# ============================================================
# 4. Inventory & Supply Chain (7 classes) - inventory.py
# ============================================================
from store.models.inventory import (
    Supplier,
    Warehouse,
    Inventory,
    ImportOrder,
    ImportOrderItem,
    StockTransfer,
    ReturnRequestToSupplier,
)

# ============================================================
# 5. Sales & Orders (9 classes) - order.py
# ============================================================
from store.models.order import (
    Cart,
    CartItem,
    Order,
    OrderItem,
    OrderStatusHistory,
    Wishlist,
    WishlistItem,
    Review,
    Rating,
)

# ============================================================
# 6. Payment & Shipping (5 classes) - payment.py
# ============================================================
from store.models.payment import (
    Payment,
    PaymentMethod,
    ShippingMethod,
    Shipment,
    RefundRequest,
)

# ============================================================
# 7. Marketing & Content (6 classes) - marketing.py
# ============================================================
from store.models.marketing import (
    Promotion,
    Coupon,
    Notification,
    Banner,
    BlogPost,
    SystemConfig,
)

# ============================================================
# Export all 52 models
# ============================================================
__all__ = [
    # Abstract Models (2)
    'TimeStampedModel',
    'Person',
    
    # Users & Roles (11)
    'UserAccount',
    'Customer',
    'CustomerProfile',
    'MemberTier',
    'Staff',
    'Admin',
    'SalesStaff',
    'WarehouseStaff',
    'Shipper',
    'GuestSession',
    'Address',
    
    # Products (12)
    'Category',
    'Book',
    'BookDetail',
    'BookImage',
    'Author',
    'Translator',
    'Publisher',
    'Language',
    'BookFormat',
    'Series',
    'Tag',
    'BookTag',
    
    # Inventory & Supply Chain (7)
    'Supplier',
    'Warehouse',
    'Inventory',
    'ImportOrder',
    'ImportOrderItem',
    'StockTransfer',
    'ReturnRequestToSupplier',
    
    # Sales & Orders (9)
    'Cart',
    'CartItem',
    'Order',
    'OrderItem',
    'OrderStatusHistory',
    'Wishlist',
    'WishlistItem',
    'Review',
    'Rating',
    
    # Payment & Shipping (5)
    'Payment',
    'PaymentMethod',
    'ShippingMethod',
    'Shipment',
    'RefundRequest',
    
    # Marketing & Content (6)
    'Promotion',
    'Coupon',
    'Notification',
    'Banner',
    'BlogPost',
    'SystemConfig',
]

# Model count verification: 2 + 11 + 12 + 7 + 9 + 5 + 6 = 52 Models

