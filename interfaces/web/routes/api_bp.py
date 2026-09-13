from flask import Blueprint

from interfaces.web.routes.authors import authors_bp
from interfaces.web.routes.books import books_bp

api_bp = Blueprint("api_bp", __name__, url_prefix="/api")


api_bp.register_blueprint(authors_bp)
api_bp.register_blueprint(books_bp)
