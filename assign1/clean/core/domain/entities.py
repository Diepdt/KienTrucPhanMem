from typing import List
from dataclasses import dataclass, field

@dataclass
class Customer:
    """Domain Entity: Customer - không phụ thuộc Django"""
    id: int
    name: str
    email: str
    password: str

@dataclass
class Book:
    """Domain Entity: Book"""
    id: int
    title: str
    author: str
    price: float
    stock: int

@dataclass
class CartItem:
    """Domain Entity: CartItem"""
    book_id: int
    quantity: int
    book: Book = None  # Optional reference
    
    def get_total(self) -> float:
        """Tính tổng tiền của item"""
        if self.book:
            return float(self.book.price) * self.quantity
        return 0.0

@dataclass
class Cart:
    """Domain Entity: Cart - chứa business logic"""
    id: int
    customer_id: int
    items: List[CartItem] = field(default_factory=list)
    created_at: str = None
    
    def add_item(self, book: Book, quantity: int = 1) -> None:
        """Thêm sách vào giỏ hoặc tăng số lượng"""
        for item in self.items:
            if item.book_id == book.id:
                item.quantity += quantity
                return
        
        new_item = CartItem(book_id=book.id, quantity=quantity, book=book)
        self.items.append(new_item)
    
    def remove_item(self, book_id: int) -> None:
        """Xóa sách khỏi giỏ"""
        self.items = [item for item in self.items if item.book_id != book_id]
    
    def update_quantity(self, book_id: int, quantity: int) -> None:
        """Cập nhật số lượng"""
        for item in self.items:
            if item.book_id == book_id:
                if quantity > 0:
                    item.quantity = quantity
                else:
                    self.remove_item(book_id)
                return
    
    def get_total_price(self) -> float:
        """Tính tổng tiền toàn giỏ"""
        return sum(item.get_total() for item in self.items)
    
    def is_empty(self) -> bool:
        """Kiểm tra giỏ có trống không"""
        return len(self.items) == 0
