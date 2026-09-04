from flask import Blueprint, jsonify, request

from db import get_connection

books_bp = Blueprint("books", __name__, url_prefix="/api/books")

BOOK_QUERY = """
    SELECT
        books.id,
        books.title,
        books.published_year,
        books.author_id,
        authors.name AS author_name
    FROM books
    JOIN authors ON authors.id = books.author_id
"""

def read_book_payload(data):
    """Pull title, year and author_id out of the request body.

    Returns (values, error). Exactly one of them is None.
    """
    title = (data.get("title") or "").strip()
    if not title:
        return None, "Title is required."

    try:
        author_id = int(data.get("author_id"))
    except (TypeError, ValueError):
        return None, "Choose an author."

    year = data.get("published_year")
    if year in (None, ""):
        year = None
    else:
        try:
            year = int(year)
        except (TypeError, ValueError):
            return None, "Published year must be a number."

    return (title, year, author_id), None

@books_bp.route("", methods=["GET"])
def list_books():
    connection = get_connection()
    cursor = connection.cursor(dictionary=True, buffered=True)
    try:
        cursor.execute(BOOK_QUERY + " ORDER BY books.id")
        books = cursor.fetchall()
        return jsonify(books), 200
    finally:
        cursor.close()
        connection.close()

@books_bp.route("/<int:book_id>", methods=["GET"])
def get_book(book_id):
    connection = get_connection()
    cursor = connection.cursor(dictionary=True, buffered=True)
    try:
        cursor.execute(BOOK_QUERY + " WHERE books.id = %s", (book_id,))
        book = cursor.fetchone()

        if book is None:
            return jsonify({"error": "Book not found."}), 404

        return jsonify(book), 200
    finally:
        cursor.close()
        connection.close()

@books_bp.route("", methods=["POST"])
def create_book():
    data = request.get_json(silent=True) or {}

    values, error = read_book_payload(data)
    if error:
        return jsonify({"error": error}), 400

    title, year, author_id = values

    connection = get_connection()
    cursor = connection.cursor(dictionary=True, buffered=True)
    try:
        cursor.execute("SELECT id FROM authors WHERE id = %s", (author_id,))
        if cursor.fetchone() is None:
            return jsonify({"error": "That author does not exist."}), 400

        cursor.execute(
            "INSERT INTO books (title, published_year, author_id) VALUES (%s, %s, %s)",
            (title, year, author_id),
        )
        connection.commit()

        cursor.execute(BOOK_QUERY + " WHERE books.id = %s", (cursor.lastrowid,))
        book = cursor.fetchone()

        return jsonify(book), 201
    finally:
        cursor.close()
        connection.close()

@books_bp.route("/<int:book_id>", methods=["PUT"])
def update_book(book_id):
    data = request.get_json(silent=True) or {}

    values, error = read_book_payload(data)
    if error:
        return jsonify({"error": error}), 400

    title, year, author_id = values

    connection = get_connection()
    cursor = connection.cursor(dictionary=True, buffered=True)
    try:
        cursor.execute("SELECT id FROM books WHERE id = %s", (book_id,))
        if cursor.fetchone() is None:
            return jsonify({"error": "Book not found."}), 404

        cursor.execute("SELECT id FROM authors WHERE id = %s", (author_id,))
        if cursor.fetchone() is None:
            return jsonify({"error": "That author does not exist."}), 400

        cursor.execute(
            """
            UPDATE books
            SET title = %s, published_year = %s, author_id = %s
            WHERE id = %s
            """,
            (title, year, author_id, book_id),
        )
        connection.commit()

        cursor.execute(BOOK_QUERY + " WHERE books.id = %s", (book_id,))
        book = cursor.fetchone()

        return jsonify(book), 200
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
            return jsonify({"error": "Book not found."}), 404

        return jsonify({"message": "Book deleted."}), 200
    finally:
        cursor.close()
        connection.close()

