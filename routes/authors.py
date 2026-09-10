from flask import Blueprint, jsonify
from factories import make_author_service
from validators import author_payload

authors_bp = Blueprint("authors", __name__, url_prefix="/authors")


@authors_bp.route("", methods=["GET"])
def list_authors():
    service, connection = make_author_service()
    try:
        authors = service.list_authors()
        return jsonify([a.to_dict() for a in authors]), 200
    finally:
        connection.close()


@authors_bp.route("/<int:author_id>", methods=["GET"])
def get_author(author_id):
    service, connection = make_author_service()
    try:
        author = service.get_author(author_id)
        return jsonify(author.to_dict()), 200
    finally:
        connection.close()


@authors_bp.route("", methods=["POST"])
def create_author():
    name, country = author_payload()
    service, connection = make_author_service()
    try:
        author = service.create_author(name, country)
        return jsonify(author.to_dict()), 201
    finally:
        connection.close()


@authors_bp.route("/<int:author_id>", methods=["PUT"])
def update_author(author_id):
    name, country = author_payload()
    service, connection = make_author_service()
    try:
        author = service.update_author(author_id, name, country)
        return jsonify(author.to_dict()), 200
    finally:
        connection.close()


@authors_bp.route("/<int:author_id>", methods=["DELETE"])
def delete_author(author_id):
    service, connection = make_author_service()
    try:
        service.delete_author(author_id)
        return jsonify({"message": f"Author {author_id} deleted."}), 200
    finally:
        connection.close()