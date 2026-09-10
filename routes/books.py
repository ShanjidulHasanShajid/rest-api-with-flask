from flask import Blueprint, jsonify

from factories import make_book_service
from validators import book_payload

books_bp = Blueprint("books", __name__, url_prefix="/books")


@books_bp.route("", methods=["GET"])
def list_books():
    service, connection = make_book_service()
    try:
        books = service.list_books()
        return jsonify([b.to_dict() for b in books]), 200
    finally:
        connection.close()


@books_bp.route("/<int:book_id>", methods=["GET"])
def get_book(book_id):
    service, connection = make_book_service()
    try:
        book = service.get_book(book_id)
        return jsonify(book.to_dict()), 200
    finally:
        connection.close()


@books_bp.route("", methods=["POST"])
def create_book():
    title, year, author_id = book_payload()
    service, connection = make_book_service()
    try:
        book = service.create_book(title, year, author_id)
        return jsonify(book.to_dict()), 201
    finally:
        connection.close()


@books_bp.route("/<int:book_id>", methods=["PUT"])
def update_book(book_id):
    title, year, author_id = book_payload()
    service, connection = make_book_service()
    try:
        book = service.update_book(book_id, title, year, author_id)
        return jsonify(book.to_dict()), 200
    finally:
        connection.close()


@books_bp.route("/<int:book_id>", methods=["DELETE"])
def delete_book(book_id):
    service, connection = make_book_service()
    try:
        service.delete_book(book_id)
        return jsonify({"message": f"Book {book_id} deleted."}), 200
    finally:
        connection.close()