# from models.author import Author
# from models.book import Book

# a = Author.from_row({"id": 1, "name": "Chinua Achebe", "country": "Nigeria"})
# print(a)                 # Author(id=1, name='Chinua Achebe', country='Nigeria')
# print(a.to_dict())       # {'id': 1, 'name': 'Chinua Achebe', 'country': 'Nigeria'}

# b = Book.from_row({
#     "id": 1, "title": "Things Fall Apart", "author_id": 1,
#     "published_year": 1958, "author_name": "Chinua Achebe",
# })
# print(b)
# print(b.to_dict())



# from db import get_connection
# from repositories.author_repository import AuthorRepository

# conn = get_connection()
# repo = AuthorRepository(conn)

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


# from db import get_connection
# from repositories.author_repository import AuthorRepository
# from repositories.book_repository import BookRepository
# from services.book_service import BookService
# from errors import ApiError

# conn = get_connection()
# service = BookService(BookRepository(conn), AuthorRepository(conn))

# print(service.list_books())

# try:
#     service.create_book("Bad Book", 2000, 9999)   # no such author
# except ApiError as err:
#     print(err.status, err.message, err.fields)    # 422 ... {'author_id': '...'}

# book = service.create_book("Arrow of God", 1964, 1)
# print(book)
# conn.close()