from flask import Blueprint, jsonify

from db import get_connection
from errors import ApiError
from validators import book_payload

books_bp = Blueprint("books", __name__, url_prefix="/api/books")

BOOK_QUERY = """
    SELECT books.id, books.title, books.published_year, books.author_id,
           authors.name AS author_name
    FROM books
    JOIN authors ON authors.id = books.author_id
"""


def fetch_book(cursor, book_id):
    """One book, or a 404. Used by GET, POST, and PUT."""
    cursor.execute(BOOK_QUERY + " WHERE books.id = %s", (book_id,))
    book = cursor.fetchone()
    if book is None:
        raise ApiError(404, f"No book with id {book_id}.")
    return book


def require_author(cursor, author_id):
    """The author must exist, or it's a validation failure on that field."""
    cursor.execute("SELECT id FROM authors WHERE id = %s", (author_id,))
    if cursor.fetchone() is None:
        raise ApiError(422, "Some fields are invalid.",
                       fields={"author_id": f"No author with id {author_id}."})


@books_bp.route("", methods=["GET"])
def list_books():
    connection = get_connection()
    cursor = connection.cursor(dictionary=True, buffered=True)
    try:
        cursor.execute(BOOK_QUERY + " ORDER BY books.id")
        return jsonify(cursor.fetchall()), 200
    finally:
        cursor.close()
        connection.close()


@books_bp.route("/<int:book_id>", methods=["GET"])
def get_book(book_id):
    connection = get_connection()
    cursor = connection.cursor(dictionary=True, buffered=True)
    try:
        return jsonify(fetch_book(cursor, book_id)), 200
    finally:
        cursor.close()
        connection.close()


@books_bp.route("", methods=["POST"])
def create_book():
    title, year, author_id = book_payload()          # 415 / 400 / 422 raised in here

    connection = get_connection()
    cursor = connection.cursor(dictionary=True, buffered=True)
    try:
        require_author(cursor, author_id)
        cursor.execute(
            "INSERT INTO books (title, published_year, author_id) VALUES (%s, %s, %s)",
            (title, year, author_id),
        )
        connection.commit()
        return jsonify(fetch_book(cursor, cursor.lastrowid)), 201
    finally:
        cursor.close()
        connection.close()


@books_bp.route("/<int:book_id>", methods=["PUT"])
def update_book(book_id):
    title, year, author_id = book_payload()

    connection = get_connection()
    cursor = connection.cursor(dictionary=True, buffered=True)
    try:
        fetch_book(cursor, book_id)                  # 404 if the book is gone
        require_author(cursor, author_id)            # 422 if the author is wrong
        cursor.execute(
            "UPDATE books SET title = %s, published_year = %s, author_id = %s WHERE id = %s",
            (title, year, author_id, book_id),
        )
        connection.commit()
        return jsonify(fetch_book(cursor, book_id)), 200
    finally:
        cursor.close()
        connection.close()


@books_bp.route("/<int:book_id>", methods=["DELETE"])
def delete_book(book_id):
    connection = get_connection()
    cursor = connection.cursor(dictionary=True, buffered=True)
    try:
        cursor.execute("DELETE FROM books WHERE id = %s", (book_id,))
        connection.commit()
        if cursor.rowcount == 0:
            raise ApiError(404, f"No book with id {book_id}.")
        return jsonify({"message": f"Book {book_id} deleted."}), 200
    finally:
        cursor.close()
        connection.close()