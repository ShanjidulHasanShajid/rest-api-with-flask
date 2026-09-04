from flask import Blueprint, jsonify
from flask import request

from db import get_connection

authors_bp = Blueprint("authors", __name__, url_prefix="/api/authors")


@authors_bp.route("", methods=["GET"])
def list_authors():
    connection = get_connection()
    cursor = connection.cursor(dictionary=True, buffered=True)
    try:
        cursor.execute("SELECT id, name, country FROM authors ORDER BY name")
        authors = cursor.fetchall()
        return jsonify(authors), 200
    finally:
        cursor.close()
        connection.close()

@authors_bp.route("/<int:author_id>", methods=["GET"])
def get_author(author_id):
    connection = get_connection()
    cursor = connection.cursor(dictionary=True, buffered=True)
    try:
        cursor.execute(
            "SELECT id, name, country FROM authors WHERE id = %s",
            (author_id,),
        )
        author = cursor.fetchone()

        if author is None:
            return jsonify({"error": "Author not found."}), 404

        return jsonify(author), 200
    finally:
        cursor.close()
        connection.close()

@authors_bp.route("", methods=["POST"])
def create_author():
    data = request.get_json(silent=True) or {}

    name = (data.get("name") or "").strip()
    country = (data.get("country") or "").strip() or None

    if not name:
        return jsonify({"error": "Name is required."}), 400

    connection = get_connection()
    cursor = connection.cursor(dictionary=True, buffered=True)
    try:
        cursor.execute(
            "INSERT INTO authors (name, country) VALUES (%s, %s)",
            (name, country),
        )
        connection.commit()
        new_id = cursor.lastrowid

        cursor.execute(
            "SELECT id, name, country FROM authors WHERE id = %s",
            (new_id,),
        )
        author = cursor.fetchone()

        return jsonify(author), 201
    finally:
        cursor.close()
        connection.close()

@authors_bp.route("/<int:author_id>", methods=["PUT"])
def update_author(author_id):
    data = request.get_json(silent=True) or {}

    name = (data.get("name") or "").strip()
    country = (data.get("country") or "").strip() or None

    if not name:
        return jsonify({"error": "Name is required."}), 400

    connection = get_connection()
    cursor = connection.cursor(dictionary=True, buffered=True)
    try:
        cursor.execute("SELECT id FROM authors WHERE id = %s", (author_id,))
        if cursor.fetchone() is None:
            return jsonify({"error": "Author not found."}), 404

        cursor.execute(
            "UPDATE authors SET name = %s, country = %s WHERE id = %s",
            (name, country, author_id),
        )
        connection.commit()

        cursor.execute(
            "SELECT id, name, country FROM authors WHERE id = %s",
            (author_id,),
        )
        author = cursor.fetchone()

        return jsonify(author), 200
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
            return jsonify({"error": "Author not found."}), 404

        return jsonify({"message": "Author deleted."}), 200
    finally:
        cursor.close()
        connection.close()