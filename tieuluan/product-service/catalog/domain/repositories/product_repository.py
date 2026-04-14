from abc import ABC, abstractmethod
from typing import Dict, List


class ProductRepository(ABC):
    @abstractmethod
    def list(self, filters: dict):
        raise NotImplementedError

    @abstractmethod
    def get_by_id(self, product_id: int):
        raise NotImplementedError

    @abstractmethod
    def create(self, entity):
        raise NotImplementedError

    @abstractmethod
    def update(self, product, entity):
        raise NotImplementedError

    @abstractmethod
    def delete(self, product):
        raise NotImplementedError

    @abstractmethod
    def update_inventory(self, items: List[Dict]):
        raise NotImplementedError
