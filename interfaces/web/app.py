import logging

from flask import Flask

from interfaces.web.errors import register_error_handlers
from interfaces.web.routes.api_bp import api_bp


def create_app():
    logging.basicConfig(level=logging.INFO)

    app = Flask(__name__)
    app.register_blueprint(api_bp)
    register_error_handlers(app)

    return app
