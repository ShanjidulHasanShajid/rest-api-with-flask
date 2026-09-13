"""Port the application layer codes against. Infrastructure supplies the adapter."""

from abc import ABC, abstractmethod
from typing import List, Optional

from domain.entities import Book


class BookRepository(ABC):
    @abstractmethod
    def find_all(self) -> List[Book]: ...

    @abstractmethod
    def find_by_id(self, book_id: int) -> Optional[Book]: ...

    @abstractmethod
    def create(self, title: str, published_year: Optional[int], author_id: int) -> Book: ...

    @abstractmethod
    def update(
        self, book_id: int, title: str, published_year: Optional[int], author_id: int
    ) -> Book: ...

    @abstractmethod
    def delete(self, book_id: int) -> bool: ...
