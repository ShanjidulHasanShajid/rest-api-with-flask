from flask import Blueprint, jsonify

from db import get_connection
from errors import ApiError
from validators import author_payload

authors_bp = Blueprint("authors", __name__, url_prefix="/authors")

AUTHOR_QUERY = "SELECT * FROM authors"


def fetch_author(cursor, author_id):
    """One author, or a 404. Used by GET, POST and PUT."""
    cursor.execute(AUTHOR_QUERY + " WHERE id = %s", (author_id,))
    author = cursor.fetchone()
    if author is None:
        raise ApiError(404, f"No author with id {author_id}.")
    return author


@authors_bp.route("", methods=["GET"])
def list_authors():
    connection = get_connection()
    cursor = connection.cursor(dictionary=True, buffered=True)
    try:
        cursor.execute(AUTHOR_QUERY + " ORDER BY name")
        authors = cursor.fetchall()
        return jsonify([a["name"] for a in authors]), 200      # ["Chinua Achebe", "Jhumpa Lahiri"]
    finally:
        cursor.close()
        connection.close()


@authors_bp.route("/<int:author_id>", methods=["GET"])
def get_author(author_id):
    connection = get_connection()
    cursor = connection.cursor(dictionary=True, buffered=True)
    try:
        return jsonify(fetch_author(cursor, author_id)), 200
    finally:
        cursor.close()
        connection.close()


@authors_bp.route("", methods=["POST"])
def create_author():
    name, country = author_payload()          # 415 / 400 / 422 raised in here

    connection = get_connection()
    cursor = connection.cursor(dictionary=True, buffered=True)
    try:
        cursor.execute(
            "INSERT INTO authors (name, country) VALUES (%s, %s)",
            (name, country),
        )
        connection.commit()
        return jsonify(fetch_author(cursor, cursor.lastrowid)), 201
    finally:
        cursor.close()
        connection.close()


@authors_bp.route("/<int:author_id>", methods=["PUT"])
def update_author(author_id):
    name, country = author_payload()

    connection = get_connection()
    cursor = connection.cursor(dictionary=True, buffered=True)
    try:
        fetch_author(cursor, author_id)       # 404 if the author is gone
        cursor.execute(
            "UPDATE authors SET name = %s, country = %s WHERE id = %s",
            (name, country, author_id),
        )
        connection.commit()
        return jsonify(fetch_author(cursor, author_id)), 200
    finally:
        cursor.close()
        connection.close()


@authors_bp.route("/<int:author_id>", methods=["DELETE"])
def delete_author(author_id):
    connection = get_connection()
    cursor = connection.cursor(dictionary=True, buffered=True)
    try:
        cursor.execute("DELETE FROM authors WHERE id = %s", (author_id,))
        connection.commit()

        if cursor.rowcount == 0:
            raise ApiError(404, f"No author with id {author_id}.")

        return jsonify({"message": f"Author {author_id} deleted."}), 200
    finally:
        cursor.close()
        connection.close()