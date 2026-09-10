from typing import List, Optional
from models.book import Book

BOOK_QUERY = """
    SELECT books.id, books.title, books.published_year, books.author_id,
           authors.name AS author_name
    FROM books
    JOIN authors ON authors.id = books.author_id
"""


class BookRepository:
    def __init__(self, connection):
        self.connection = connection

    def find_all(self) -> List[Book]:
        cursor = self.connection.cursor(dictionary=True, buffered=True)
        try:
            cursor.execute(BOOK_QUERY + " ORDER BY books.id")
            return [Book.from_row(row) for row in cursor.fetchall()]
        finally:
            cursor.close()

    def find_by_id(self, book_id: int) -> Optional[Book]:
        cursor = self.connection.cursor(dictionary=True, buffered=True)
        try:
            cursor.execute(BOOK_QUERY + " WHERE books.id = %s", (book_id,))
            row = cursor.fetchone()
            return Book.from_row(row) if row else None
        finally:
            cursor.close()

    def create(self, title: str, published_year: Optional[int], author_id: int) -> Book:
        cursor = self.connection.cursor(dictionary=True, buffered=True)
        try:
            cursor.execute(
                "INSERT INTO books (title, published_year, author_id) VALUES (%s, %s, %s)",
                (title, published_year, author_id),
            )
            self.connection.commit()
            return self.find_by_id(cursor.lastrowid)
        finally:
            cursor.close()

    def update(self, book_id: int, title: str, published_year: Optional[int], author_id: int) -> Book:
        cursor = self.connection.cursor(dictionary=True, buffered=True)
        try:
            cursor.execute(
                """UPDATE books SET title = %s, published_year = %s, author_id = %s
                   WHERE id = %s""",
                (title, published_year, author_id, book_id),
            )
            self.connection.commit()
            return self.find_by_id(book_id)
        finally:
            cursor.close()

    def delete(self, book_id: int) -> bool:
        cursor = self.connection.cursor(dictionary=True, buffered=True)
        try:
            cursor.execute("DELETE FROM books WHERE id = %s", (book_id,))
            self.connection.commit()
            return cursor.rowcount > 0
        finally:
            cursor.close()