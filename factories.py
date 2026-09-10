from db import get_connection
from repositories.author_repository import AuthorRepository
from repositories.book_repository import BookRepository
from services.author_service import AuthorService
from services.book_service import BookService


def make_author_service():
    connection = get_connection()
    repository = AuthorRepository(connection)
    return AuthorService(repository), connection


def make_book_service():
    connection = get_connection()
    book_repository = BookRepository(connection)
    author_repository = AuthorRepository(connection)
    return BookService(book_repository, author_repository), connection