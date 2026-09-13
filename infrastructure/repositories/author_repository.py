from typing import List, Optional

from domain.entities import Author
from domain.repositories import AuthorRepository

AUTHOR_COLUMNS = "id, name, country"


class MySQLAuthorRepository(AuthorRepository):
    def __init__(self, connection):
        self.connection = connection

    def find_all(self) -> List[Author]:
        cursor = self.connection.cursor(dictionary=True, buffered=True)
        try:
            cursor.execute(f"SELECT {AUTHOR_COLUMNS} FROM authors ORDER BY name")
            return [Author.from_row(row) for row in cursor.fetchall()]
        finally:
            cursor.close()

    def find_by_id(self, author_id: int) -> Optional[Author]:
        cursor = self.connection.cursor(dictionary=True, buffered=True)
        try:
            cursor.execute(f"SELECT {AUTHOR_COLUMNS} FROM authors WHERE id = %s", (author_id,))
            row = cursor.fetchone()
            return Author.from_row(row) if row else None
        finally:
            cursor.close()

    def exists(self, author_id: int) -> bool:
        cursor = self.connection.cursor(dictionary=True, buffered=True)
        try:
            cursor.execute("SELECT id FROM authors WHERE id = %s", (author_id,))
            return cursor.fetchone() is not None
        finally:
            cursor.close()

    def create(self, name: str, country: Optional[str]) -> Author:
        cursor = self.connection.cursor(dictionary=True, buffered=True)
        try:
            cursor.execute(
                "INSERT INTO authors (name, country) VALUES (%s, %s)",
                (name, country),
            )
            self.connection.commit()
            return self.find_by_id(cursor.lastrowid)
        finally:
            cursor.close()

    def update(self, author_id: int, name: str, country: Optional[str]) -> Author:
        cursor = self.connection.cursor(dictionary=True, buffered=True)
        try:
            cursor.execute(
                "UPDATE authors SET name = %s, country = %s WHERE id = %s",
                (name, country, author_id),
            )
            self.connection.commit()
            return self.find_by_id(author_id)
        finally:
            cursor.close()

    def delete(self, author_id: int) -> bool:
        """Returns True if a row was actually deleted."""
        cursor = self.connection.cursor(dictionary=True, buffered=True)
        try:
            cursor.execute("DELETE FROM authors WHERE id = %s", (author_id,))
            self.connection.commit()
            return cursor.rowcount > 0
        finally:
            cursor.close()
