from typing import List, Optional
from core.domain.entities import Customer, Book, Cart, CartItem
from core.interfaces.repositories import ICustomerRepository, IBookRepository, ICartRepository
from monolith.accounts.models import Customer as CustomerModel
from monolith.books.models import Book as BookModel
from monolith.cart.models import Cart as CartModel, CartItem as CartItemModel

class DjangoCustomerRepository(ICustomerRepository):
    """Django Implementation của ICustomerRepository"""
    
    def get_by_id(self, customer_id: int) -> Optional[Customer]:
        """Lấy customer theo ID"""
        try:
            model = CustomerModel.objects.get(id=customer_id)
            return self._model_to_entity(model)
        except CustomerModel.DoesNotExist:
            return None
    
    def get_by_email(self, email: str) -> Optional[Customer]:
        """Lấy customer theo email"""
        try:
            model = CustomerModel.objects.get(email=email)
            return self._model_to_entity(model)
        except CustomerModel.DoesNotExist:
            return None
    
    @staticmethod
    def _model_to_entity(model: CustomerModel) -> Customer:
        """Chuyển Django Model thành Domain Entity"""
        return Customer(
            id=model.id,
            name=model.name,
            email=model.email,
            password=model.password
        )

class DjangoBookRepository(IBookRepository):
    """Django Implementation của IBookRepository"""
    
    def get_by_id(self, book_id: int) -> Optional[Book]:
        """Lấy sách theo ID"""
        try:
            model = BookModel.objects.get(id=book_id)
            return self._model_to_entity(model)
        except BookModel.DoesNotExist:
            return None
    
    def list_all(self) -> List[Book]:
        """Lấy tất cả sách"""
        models = BookModel.objects.all()
        return [self._model_to_entity(model) for model in models]
    
    @staticmethod
    def _model_to_entity(model: BookModel) -> Book:
        """Chuyển Django Model thành Domain Entity"""
        return Book(
            id=model.id,
            title=model.title,
            author=model.author,
            price=float(model.price),
            stock=model.stock
        )

class DjangoCartRepository(ICartRepository):
    """Django Implementation của ICartRepository"""
    
    def get_by_customer(self, customer_id: int) -> Optional[Cart]:
        """Lấy giỏ hàng của customer"""
        try:
            model = CartModel.objects.get(customer_id=customer_id)
            return self._model_to_entity(model)
        except CartModel.DoesNotExist:
            return None
    
    def save(self, cart: Cart) -> Cart:
        """Lưu giỏ hàng"""
        try:
            cart_model = CartModel.objects.get(id=cart.id)
        except CartModel.DoesNotExist:
            cart_model = CartModel.objects.create(customer_id=cart.customer_id)
        
        # Xóa items cũ
        CartItemModel.objects.filter(cart=cart_model).delete()
        
        # Tạo items mới
        for item in cart.items:
            CartItemModel.objects.create(
                cart=cart_model,
                book_id=item.book_id,
                quantity=item.quantity
            )
        
        return self._model_to_entity(cart_model)
    
    def create_empty_cart(self, customer_id: int) -> Cart:
        """Tạo giỏ hàng trống mới"""
        cart_model = CartModel.objects.create(customer_id=customer_id)
        return self._model_to_entity(cart_model)
    
    @staticmethod
    def _model_to_entity(model: CartModel) -> Cart:
        """Chuyển Django Model thành Domain Entity"""
        items = []
        for item_model in model.cartitem_set.all():
            book_model = item_model.book
            book = Book(
                id=book_model.id,
                title=book_model.title,
                author=book_model.author,
                price=float(book_model.price),
                stock=book_model.stock
            )
            item = CartItem(
                book_id=item_model.book_id,
                quantity=item_model.quantity,
                book=book
            )
            items.append(item)
        
        return Cart(
            id=model.id,
            customer_id=model.customer_id,
            items=items
        )
