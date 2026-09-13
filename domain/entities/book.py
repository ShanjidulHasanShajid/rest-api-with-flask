from dataclasses import dataclass
from typing import Optional


@dataclass
class Book:
    id: Optional[int]
    title: str
    author_id: int
    published_year: Optional[int] = None
    author_name: Optional[str] = None

    @classmethod
    def from_row(cls, row: dict) -> "Book":
        return cls(
            id=row["id"],
            title=row["title"],
            author_id=row["author_id"],
            published_year=row.get("published_year"),
            author_name=row.get("author_name"),
        )

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "title": self.title,
            "author_id": self.author_id,
            "published_year": self.published_year,
            "author_name": self.author_name,
        }
