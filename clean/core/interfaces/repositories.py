from abc import ABC, abstractmethod
from typing import List, Optional
from core.domain.entities import Customer, Book, Cart

class ICustomerRepository(ABC):
    """Interface: Repository cho Customer"""
    
    @abstractmethod
    def get_by_id(self, customer_id: int) -> Optional[Customer]:
        """Lấy customer theo ID"""
        pass
    
    @abstractmethod
    def get_by_email(self, email: str) -> Optional[Customer]:
        """Lấy customer theo email"""
        pass
    
    @abstractmethod
    def create(self, customer: Customer) -> Customer:
        """Tạo customer mới"""
        pass

    @abstractmethod
    def create(self, customer: Customer) -> Customer:
        """Tạo mới customer"""
        pass

class IBookRepository(ABC):
    """Interface: Repository cho Book"""
    
    @abstractmethod
    def get_by_id(self, book_id: int) -> Optional[Book]:
        """Lấy sách theo ID"""
        pass
    
    @abstractmethod
    def list_all(self) -> List[Book]:
        """Lấy tất cả sách"""
        pass

class ICartRepository(ABC):
    """Interface: Repository cho Cart"""
    
    @abstractmethod
    def get_by_customer(self, customer_id: int) -> Optional[Cart]:
        """Lấy giỏ hàng của customer"""
        pass
    
    @abstractmethod
    def save(self, cart: Cart) -> Cart:
        """Lưu giỏ hàng"""
        pass
    
    @abstractmethod
    def create_empty_cart(self, customer_id: int) -> Cart:
        """Tạo giỏ hàng trống mới"""
        pass
