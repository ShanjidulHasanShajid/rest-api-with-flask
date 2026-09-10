from dataclasses import dataclass
from typing import Optional


@dataclass
class Author:
    id: Optional[int]
    name: str
    country: Optional[str] = None

    @classmethod
    def from_row(cls, row: dict) -> "Author":
        return cls(id=row["id"], name=row["name"], country=row.get("country"))

    def to_dict(self) -> dict:
        return {"id": self.id, "name": self.name, "country": self.country}