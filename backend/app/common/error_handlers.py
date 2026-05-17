from __future__ import annotations

from flask import Flask, jsonify

from .errors import ApiError, error_payload


def register_error_handlers(app: Flask) -> None:
    @app.errorhandler(ApiError)
    def handle_api_error(err: ApiError):
        return jsonify(error_payload(err.code, err.message, err.details)), err.status

    @app.errorhandler(404)
    def handle_404(_err):
        return jsonify(error_payload("not_found", "Resource not found.")), 404

    @app.errorhandler(405)
    def handle_405(_err):
        return jsonify(error_payload("method_not_allowed", "Method not allowed.")), 405

    @app.errorhandler(Exception)
    def handle_uncaught(err: Exception):
        # Flask will show a debugger page in debug mode; this keeps API responses consistent
        # when exceptions propagate.
        return jsonify(error_payload("internal_error", "Internal server error.")), 500
