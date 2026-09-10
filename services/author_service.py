from errors import ApiError
from repositories.author_repository import AuthorRepository


class AuthorService:
    def __init__(self, repository: AuthorRepository):
        self.repository = repository

    def list_authors(self):
        return self.repository.find_all()

    def get_author(self, author_id: int):
        author = self.repository.find_by_id(author_id)
        if author is None:
            raise ApiError(404, f"No author with id {author_id}.")
        return author

    def create_author(self, name: str, country):
        return self.repository.create(name, country)

    def update_author(self, author_id: int, name: str, country):
        self.get_author(author_id)              # 404 if missing — reuses the check above
        return self.repository.update(author_id, name, country)

    def delete_author(self, author_id: int):
        deleted = self.repository.delete(author_id)
        if not deleted:
            raise ApiError(404, f"No author with id {author_id}.")