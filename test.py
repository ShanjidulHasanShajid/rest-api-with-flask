# from domain.entities import Author, Book

# a = Author.from_row({"id": 1, "name": "Chinua Achebe", "country": "Nigeria"})
# print(a)                 # Author(id=1, name='Chinua Achebe', country='Nigeria')
# print(a.to_dict())       # {'id': 1, 'name': 'Chinua Achebe', 'country': 'Nigeria'}

# b = Book.from_row({
#     "id": 1, "title": "Things Fall Apart", "author_id": 1,
#     "published_year": 1958, "author_name": "Chinua Achebe",
# })
# print(b)
# print(b.to_dict())



# from infrastructure.database import get_connection
# from infrastructure.repositories.author_repository import MySQLAuthorRepository

# conn = get_connection()
# repo = MySQLAuthorRepository(conn)

# print(repo.find_all())
# print(repo.find_by_id(1))
# print(repo.find_by_id(9999))          # None
# print(repo.exists(1), repo.exists(9999))

# new = repo.create("Toni Morrison", "United States")
# print(new)
# print(repo.update(new.id, "Toni Morrison", "USA"))
# print(repo.delete(new.id))            # True
# print(repo.delete(new.id))            # False — already gone
# conn.close()
