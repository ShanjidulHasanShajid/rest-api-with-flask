"""Port the application layer codes against. Infrastructure supplies the adapter."""

from abc import ABC, abstractmethod
from typing import List, Optional

from domain.entities import Author


class AuthorRepository(ABC):
    @abstractmethod
    def find_all(self) -> List[Author]: ...

    @abstractmethod
    def find_by_id(self, author_id: int) -> Optional[Author]: ...

    @abstractmethod
    def exists(self, author_id: int) -> bool: ...

    @abstractmethod
    def create(self, name: str, country: Optional[str]) -> Author: ...

    @abstractmethod
    def update(self, author_id: int, name: str, country: Optional[str]) -> Author: ...

    @abstractmethod
    def delete(self, author_id: int) -> bool: ...
