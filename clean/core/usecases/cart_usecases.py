from clean.core.domain.entities import Cart, Book
from clean.core.interfaces.repositories import ICartRepository, IBookRepository, ICustomerRepository

class AddBookToCartUseCase:
    def __init__(self, cart_repository: ICartRepository, book_repository: IBookRepository, customer_repository: ICustomerRepository):
        self.cart_repo = cart_repository
        self.book_repo = book_repository
        self.customer_repo = customer_repository
    
    def execute(self, customer_id: int, book_id: int, quantity: int = 1) -> dict:
        customer = self.customer_repo.get_by_id(customer_id)
        if not customer:
            return {"success": False, "error": "Customer không tồn tại"}
        
        book = self.book_repo.get_by_id(book_id)
        if not book:
            return {"success": False, "error": "Sách không tồn tại"}
        
        if book.stock < quantity:
            return {"success": False, "error": "Không đủ hàng"}
        
        cart = self.cart_repo.get_by_customer(customer_id)
        if not cart:
            cart = self.cart_repo.create_empty_cart(customer_id)
        
        cart.add_item(book, quantity)
        saved_cart = self.cart_repo.save(cart)
        
        return {"success": True, "message": f"Đã thêm vào giỏ", "cart": saved_cart}

class ListBooksUseCase:
    def __init__(self, book_repository: IBookRepository):
        self.book_repo = book_repository
    
    def execute(self) -> list:
        return self.book_repo.list_all()

class LoginUseCase:
    def __init__(self, customer_repository: ICustomerRepository):
        self.customer_repo = customer_repository
    
    def execute(self, email: str, password: str) -> dict:
        customer = self.customer_repo.get_by_email(email)
        if not customer:
            return {"success": False, "error": "Email không tồn tại"}
        if customer.password != password:
            return {"success": False, "error": "Mật khẩu sai"}
        return {"success": True, "customer": customer}

class GetCartUseCase:
    def __init__(self, cart_repository: ICartRepository):
        self.cart_repo = cart_repository
    
    def execute(self, customer_id: int) -> dict:
        cart = self.cart_repo.get_by_customer(customer_id)
        if not cart:
            return {"success": False, "error": "Giỏ hàng không tồn tại"}
        return {"success": True, "cart": cart, "total": cart.get_total_price()}

class RemoveFromCartUseCase:
    def __init__(self, cart_repository: ICartRepository):
        self.cart_repo = cart_repository
    
    def execute(self, customer_id: int, book_id: int) -> dict:
        cart = self.cart_repo.get_by_customer(customer_id)
        if not cart:
            return {"success": False, "error": "Giỏ hàng không tồn tại"}
        cart.remove_item(book_id)
        self.cart_repo.save(cart)
        return {"success": True, "message": "Đã xóa sản phẩm"}

class UpdateCartQuantityUseCase:
    def __init__(self, cart_repository: ICartRepository):
        self.cart_repo = cart_repository
    
    def execute(self, customer_id: int, book_id: int, quantity: int) -> dict:
        cart = self.cart_repo.get_by_customer(customer_id)
        if not cart:
            return {"success": False, "error": "Giỏ hàng không tồn tại"}
        cart.update_quantity(book_id, quantity)
        self.cart_repo.save(cart)
        return {"success": True, "message": "Cập nhật thành công"}
