"""Everything about failure responses lives here."""

import logging

import mysql.connector
from flask import jsonify, request
from werkzeug.exceptions import HTTPException

logger = logging.getLogger(__name__)

DEFAULT_CODES = {
    400: "BAD_REQUEST",
    404: "NOT_FOUND",
    405: "METHOD_NOT_ALLOWED",
    409: "CONFLICT",
    415: "UNSUPPORTED_MEDIA_TYPE",
    422: "VALIDATION_FAILED",
    500: "INTERNAL_ERROR",
    503: "DATABASE_UNAVAILABLE",
}


class ApiError(Exception):
    """Raise this anywhere and the matching JSON response is sent."""

    def __init__(self, status, message, code=None, fields=None):
        super().__init__(message)
        self.status = status
        self.message = message
        self.code = code or DEFAULT_CODES.get(status, "ERROR")
        self.fields = fields

    def to_response(self):
        body = {"error": self.message, "code": self.code}
        if self.fields:
            body["fields"] = self.fields
        return jsonify(body), self.status


def wants_json():
    return request.path.startswith("/api/")


def json_error(status, message, code=None, fields=None):
    return ApiError(status, message, code, fields).to_response()


def register_error_handlers(app):
    @app.errorhandler(ApiError)
    def handle_api_error(err):
        return err.to_response()

    @app.errorhandler(404)
    def handle_404(err):
        if wants_json():
            return json_error(404, "That endpoint does not exist.")
        return err.get_response()

    @app.errorhandler(405)
    def handle_405(err):
        if wants_json():
            return json_error(405, f"{request.method} is not allowed on this URL.")
        return err.get_response()

    @app.errorhandler(415)
    def handle_415(err):
        if wants_json():
            return json_error(415, "Send Content-Type: application/json.")
        return err.get_response()

    @app.errorhandler(mysql.connector.IntegrityError)
    def handle_integrity(err):
        logger.warning("Integrity error on %s %s: %s", request.method, request.path, err)
        if wants_json():
            return json_error(409, "That change conflicts with existing data.")
        raise err

    @app.errorhandler(mysql.connector.Error)
    def handle_database(err):
        logger.exception("Database error on %s %s", request.method, request.path)
        if wants_json():
            return json_error(500, "The database rejected that request.")
        raise err

    @app.errorhandler(Exception)
    def handle_unexpected(err):
        if isinstance(err, HTTPException):      # 400, 404, 405... already handled above
            return err.get_response()

        logger.exception("Unhandled error on %s %s", request.method, request.path)
        if wants_json():
            return json_error(500, "Something went wrong on the server.")
        raise err
