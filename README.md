# Bookshelf-API

A book-and-author CRUD JSON API built with Flask and MySQL — built to learn
how a backend is actually put together, and then rebuilt around Clean
Architecture once the plain version worked.

This README is my notes on **what I learnt** — why the code is split the way
it is, and what breaks if a layer reaches somewhere it shouldn't.

## Layout

Clean Architecture: dependencies point inward. `domain` knows nothing about
Flask or MySQL; `application` knows only `domain`; `infrastructure` and
`interfaces` are the swappable outer layers that implement/drive it.

```
app.py                                   entry point — builds the app and runs it
container.py                             composition root — wires infrastructure into application

domain/
  entities/author.py, entities/book.py   plain dataclasses, no framework code
  exceptions.py                          NotFoundError, ValidationError — framework-agnostic
  repositories/                          abstract repository interfaces (the ports)

application/
  services/author_service.py             use cases, depend only on domain interfaces
  services/book_service.py

infrastructure/
  config.py, database.py                 MySQL credentials + get_connection()
  repositories/                          MySQL implementations of the domain repository ports

interfaces/web/
  app.py                                 create_app() — registers blueprints + error handlers
  errors.py                              maps domain/web exceptions to JSON responses
  validators.py                          turns request JSON into clean values
  routes/authors.py, routes/books.py     JSON API: /api/authors, /api/books

schema.sql                               the two tables
```

## Run it

```bash
# MySQL running in XAMPP, copy and run schema.sql to create the database in phpMyAdmin, import bookshelf.sql to the database
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python app.py          # http://127.0.0.1:5000
```

Every route is under `/api` — this is a JSON API only, there's no HTML to
render.

---

## The dependency rule

The whole point of the split is: **inner layers never import outer ones.**
`domain` has no `import flask`, no `import mysql.connector` — nothing outside
the standard library. That's enforceable by eye: if a file under `domain/`
ever needs to import something from `infrastructure/` or `interfaces/`, the
boundary has been crossed the wrong way.

`domain/repositories/book_repository.py` declares the **port** — the shape a
book repository has to have, with no idea how it's implemented:

```python
class BookRepository(ABC):
    @abstractmethod
    def find_all(self) -> List[Book]: ...
    @abstractmethod
    def find_by_id(self, book_id: int) -> Optional[Book]: ...
    ...
```

`infrastructure/repositories/book_repository.py` is the **adapter** — the one
place that knows it's talking to MySQL:

```python
class MySQLBookRepository(BookRepository):
    def __init__(self, connection):
        self.connection = connection

    def find_all(self) -> List[Book]:
        cursor = self.connection.cursor(dictionary=True, buffered=True)
        ...
```

`application/services/book_service.py` only ever type-hints against
`BookRepository`, the abstract one. It never imports the MySQL class, so it
has no way to know or care that the data is coming from MySQL rather than a
fake used in a test. `container.py` is the one file that imports both sides
and wires them together:

```python
def make_book_service():
    connection = get_connection()
    book_repository = MySQLBookRepository(connection)
    author_repository = MySQLAuthorRepository(connection)
    return BookService(book_repository, author_repository), connection
```

That's the composition root — the only place in the whole app where an
abstraction and its concrete implementation are mentioned in the same
breath.

---

## A request end to end — `GET /api/books`

**1. The route** — `interfaces/web/routes/books.py`

```python
@books_bp.route("", methods=["GET"])
def list_books():
    service, connection = make_book_service()
    try:
        books = service.list_books()
        return jsonify([b.to_dict() for b in books]), 200
    finally:
        connection.close()
```

The route only does three things: ask the container for a wired-up service,
call one method on it, and serialize whatever comes back. No SQL, no
knowledge of tables or columns.

**2. The use case** — `application/services/book_service.py`

```python
def list_books(self):
    return self.books.find_all()
```

**3. The adapter** — `infrastructure/repositories/book_repository.py`

```python
def find_all(self) -> List[Book]:
    cursor = self.connection.cursor(dictionary=True, buffered=True)
    try:
        cursor.execute(BOOK_QUERY + " ORDER BY books.id")
        return [Book.from_row(row) for row in cursor.fetchall()]
    finally:
        cursor.close()
```

**4. The entity** — `domain/entities/book.py` turns a raw row into a typed
object, and back into a plain dict for `jsonify`:

```python
@dataclass
class Book:
    id: Optional[int]
    title: str
    author_id: int
    published_year: Optional[int] = None
    author_name: Optional[str] = None
```

`author_name` isn't a column on `books` — it comes from the `JOIN` in
`BOOK_QUERY`. The repository is the only layer that knows that; by the time
the data reaches the entity it's just a field.

---

## Validation and errors

Two different kinds of "this request is bad," handled in two different
places, on purpose:

**Malformed input** (`interfaces/web/validators.py`) is a web-layer concern —
missing fields, wrong types, unknown keys. It's caught before a service ever
runs:

```python
def book_payload():
    data = json_body()
    fields = {}
    _reject_unknown(data, {"title", "author_id", "published_year"}, fields)
    title = _text(data, "title", fields, max_length=MAX_TITLE)
    author_id = _int(data, "author_id", fields, minimum=1)
    ...
    if fields:
        raise WebError(422, "Some fields are invalid.", fields=fields)
    return title, year, author_id
```

**Business-rule failures** (`domain/exceptions.py`) are things only the
application layer can know — a book referencing an author that doesn't
exist, a record that's missing by id. These are framework-agnostic on
purpose, so a service never has to import Flask just to fail:

```python
def _require_author(self, author_id: int):
    if not self.authors.exists(author_id):
        raise ValidationError(
            "Some fields are invalid.",
            fields={"author_id": f"No author with id {author_id}."},
        )
```

Both kinds land in the same place — `interfaces/web/errors.py` — which is
the only file that knows how to turn an exception into an HTTP status code:

```python
@app.errorhandler(WebError)
def handle_web_error(err):
    return err.to_response()

@app.errorhandler(NotFoundError)
def handle_not_found(err):
    return json_error(404, str(err))

@app.errorhandler(ValidationError)
def handle_validation(err):
    return json_error(422, err.message, fields=err.fields)
```

So every failure — malformed JSON, a missing author, MySQL rejecting an
insert — ends up as the same JSON shape:

```json
{ "error": "Some fields are invalid.", "code": "VALIDATION_FAILED",
  "fields": { "author_id": "No author with id 999." } }
```

---

## What I took away

- The Dependency Rule is the whole architecture. Everything else — the
  folder names, the abstract classes — exists to make "inner layers can't see
  outer layers" true and checkable, not just a suggestion.
- A repository **interface** living in `domain` and its MySQL
  **implementation** living in `infrastructure` is dependency inversion in
  practice: the service depends on the abstraction, and the concrete class
  gets handed to it from outside. Swapping MySQL for anything else touches
  `infrastructure/` and `container.py` only.
- Keeping `domain/exceptions.py` free of Flask means the same `AuthorService`
  could sit behind a CLI or a different web framework without a single
  change — only `interfaces/web/errors.py` would need to translate its
  exceptions differently.
- `container.py` being the one file allowed to import both an abstraction and
  its implementation is what makes the rest of the dependency rule
  enforceable — every other file only ever has one side of that to import.
- Splitting "the input is malformed" (web layer) from "the business rule
  failed" (domain layer) keeps validators dumb and services free of
  HTTP-shaped error codes — a service raises `NotFoundError`, never `404`.
- `commit()` or the write silently doesn't happen. `%s` placeholders or it's
  SQL injection. `WHERE` or the whole table changes. None of that changed by
  moving files around — Clean Architecture reorganizes where code lives, not
  what the SQL has to get right.
