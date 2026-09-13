"""Composition root — the one place that knows both the abstractions and their
concrete infrastructure implementations, and wires them together."""

from application.services.author_service import AuthorService
from application.services.book_service import BookService
from infrastructure.database import get_connection
from infrastructure.repositories.author_repository import MySQLAuthorRepository
from infrastructure.repositories.book_repository import MySQLBookRepository


def make_author_service():
    connection = get_connection()
    repository = MySQLAuthorRepository(connection)
    return AuthorService(repository), connection


def make_book_service():
    connection = get_connection()
    book_repository = MySQLBookRepository(connection)
    author_repository = MySQLAuthorRepository(connection)
    return BookService(book_repository, author_repository), connection
