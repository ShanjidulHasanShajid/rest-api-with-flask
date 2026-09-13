from domain.exceptions import NotFoundError, ValidationError
from domain.repositories import AuthorRepository, BookRepository


class BookService:
    def __init__(self, book_repository: BookRepository, author_repository: AuthorRepository):
        self.books = book_repository
        self.authors = author_repository

    def list_books(self):
        return self.books.find_all()

    def get_book(self, book_id: int):
        book = self.books.find_by_id(book_id)
        if book is None:
            raise NotFoundError("book", book_id)
        return book

    def _require_author(self, author_id: int):
        if not self.authors.exists(author_id):
            raise ValidationError(
                "Some fields are invalid.",
                fields={"author_id": f"No author with id {author_id}."},
            )

    def create_book(self, title: str, published_year, author_id: int):
        self._require_author(author_id)
        return self.books.create(title, published_year, author_id)

    def update_book(self, book_id: int, title: str, published_year, author_id: int):
        self.get_book(book_id)                   # 404 if the book doesn't exist
        self._require_author(author_id)          # 422 if the author doesn't
        return self.books.update(book_id, title, published_year, author_id)

    def delete_book(self, book_id: int):
        deleted = self.books.delete(book_id)
        if not deleted:
            raise NotFoundError("book", book_id)
