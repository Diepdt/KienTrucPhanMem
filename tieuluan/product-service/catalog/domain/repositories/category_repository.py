from abc import ABC, abstractmethod


class CategoryRepository(ABC):
    @abstractmethod
    def list_root(self, product_type: str = ''):
        raise NotImplementedError

    @abstractmethod
    def get_by_id(self, category_id: int):
        raise NotImplementedError

    @abstractmethod
    def create(self, entity):
        raise NotImplementedError

    @abstractmethod
    def update(self, category, entity):
        raise NotImplementedError

    @abstractmethod
    def delete(self, category):
        raise NotImplementedError
