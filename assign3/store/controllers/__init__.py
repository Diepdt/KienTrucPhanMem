# Controllers Package - Aggregates all domain controllers
# Note: In Django, controllers are equivalent to views

from store.controllers.bookController import views as book_views
from store.controllers.customerController import views as customer_views
from store.controllers.staffController import views as staff_views
from store.controllers.orderController import views as order_views
