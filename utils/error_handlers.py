"""
Centralized error handling for the GigMate RESTful API.

This module registers global error handlers for common exceptions raised 
across the Flask application — including validation errors, database integrity 
issues, client request problems, and unexpected server failures.

By using a consistent JSON schema via the `error_response()` helper, 
all error responses follow a predictable format for frontend/API clients.
"""

from flask import jsonify
from flask.cli import NoAppException
from marshmallow import ValidationError
from sqlalchemy.exc import IntegrityError, DataError, ProgrammingError, OperationalError
from psycopg2 import errorcodes, OperationalError as P2OperationalError


# ========== STANDARDIZED ERROR RESPONSE ==========
def error_response(message, status_code, error_type="Error"):
    return jsonify({
        "error": {
            "type": error_type,
            "message": message,
            "status": status_code
        }
    }), status_code

# ========== ERROR HANDLERS ==========
def error_handlers(app):

# ========== NAME ERRORS ==========    
    @app.errorhandler(NoAppException)
    def handle_no_app_exception(err):
        return {
            "message": (
                "Flask could not find or import your app. Please check your FLASK_APP setting "
                "and ensure your main application file and imports are correct."
            )
        }, 500

    @app.errorhandler(NameError)
    def handle_name_error(err):
        return {
            "message": f"Name error: {str(err)}. This usually means a variable or import is missing or misspelled."
        }, 500

# ========== VALIDATION ERRORS ==========
    @app.errorhandler(ValidationError)
    def handle_validation_error(err):
        return error_response(err.messages, 400, "ValidationError")

# ========== IMPORT / MODULE ERRORS ==========
    @app.errorhandler(ImportError)
    def handle_import_error(err):
        return error_response(f"Import error: {str(err)}. Please check your dependencies.", 500, "ImportError")

    @app.errorhandler(ModuleNotFoundError)
    def handle_module_not_found_error(err):
        return error_response(f"Module not found: {str(err)}. Please check your imports.", 500, "ModuleNotFoundError")

# ========== DATABASE ERRORS ==========
    @app.errorhandler(IntegrityError)
    def handle_integrity_error(err):
        if hasattr(err, "orig") and err.orig:
            code = err.orig.pgcode
            if code == errorcodes.NOT_NULL_VIOLATION:
                return error_response(f"Missing required field: {err.orig.diag.column_name}.", 409, "IntegrityError")
            if code == errorcodes.UNIQUE_VIOLATION:
                detail = getattr(err.orig.diag, "message_detail", "")
                if "already exists" in detail:
                    return error_response(f"This item already exists. {detail}", 409, "IntegrityError")
                return error_response(f"This item cannot be duplicated. {detail}", 409, "IntegrityError")
            if code == errorcodes.FOREIGN_KEY_VIOLATION:
                return error_response(
                    "A referenced value does not exist. Please check that all foreign key IDs are valid.",
                    409,
                    "ForeignKeyViolation"
                )
            if code == errorcodes.CHECK_VIOLATION:
                if "check_future_show" in str(err.orig):
                    return error_response("Shows must be scheduled for future dates and times.", 400, "CheckViolation")
                return error_response(err.orig.diag.message_detail, 409, "CheckViolation")
            return error_response("Unknown integrity error occurred.", 409, "IntegrityError")
        return error_response("Integrity error occurred.", 409, "IntegrityError")

    @app.errorhandler(DataError)
    def handle_data_error(err):
        msg = ""
        if hasattr(err.orig, "diag") and hasattr(err.orig.diag, "message_primary"):
            msg = err.orig.diag.message_primary
        elif hasattr(err.orig, "args") and err.orig.args:
            msg = err.orig.args[0]

        if any(x in msg for x in ["date/time", "out of range", "invalid input syntax for type timestamp"]):
            return error_response(
                "Invalid date/time value. Please use DD-MM-YYYY | HH:MM AM/PM (e.g., '27-11-2025 | 08:30 PM').",
                400,
                "DataError"
            )
        return error_response(msg or "Invalid data input.", 409, "DataError")

    @app.errorhandler(OperationalError)
    def handle_sqlalchemy_operational_error(err):
        return error_response("Database operational error. Please check your database configuration.", 500, "OperationalError")

    @app.errorhandler(P2OperationalError)
    def handle_psycopg2_operational_error(err):
        return error_response("Database operational error (psycopg2). Please check your database server.", 500, "OperationalError")

    @app.errorhandler(ProgrammingError)
    def handle_programming_error(err):
        if hasattr(err, "orig") and getattr(err.orig, "pgcode", None) == "42P01":
            return error_response(
                "A required database table does not exist. Ensure you have successfully initialized your database.",
                500,
                "ProgrammingError"
            )
        return error_response(f"Database programming error: {str(err)}", 500, "ProgrammingError")
    
# ========== CLIENT ERRORS ==========
    @app.errorhandler(TypeError)
    def handle_type_error(err):
        return error_response("Invalid data format. Please check your input.", 400, "TypeError")

    @app.errorhandler(AttributeError)
    def handle_attribute_error(err):
        return error_response("Missing required data. Please check your request.", 400, "AttributeError")

    @app.errorhandler(KeyError)
    def handle_key_error(err):
        missing_key = str(err).strip("'\"")
        return error_response(
            f"Missing required field: '{missing_key}'. Please check your request data and ensure all required fields are present.",
            400,
            "KeyError"
        )

    @app.errorhandler(ValueError)
    def handle_value_error(err):
        return error_response(f"Invalid value: {str(err)}. Please check your input types and formats.", 400, "ValueError")

    @app.errorhandler(400)
    def handle_bad_request(err):
        if "JSON" in str(err) or "decode" in str(err):
            return error_response("Invalid JSON format. Check for syntax errors in your request.", 400, "BadRequest")
        return error_response("Invalid request. Please check your data and try again.", 400, "BadRequest")

    @app.errorhandler(404)
    def handle_404(err):
        return error_response("Resource not found. Please check the URL.", 404, "NotFoundError")

    @app.errorhandler(405)
    def handle_method_not_allowed(err):
        return error_response("Method not allowed. Please check the HTTP method.", 405, "MethodNotAllowed")

# ========== SERVER ERRORS ==========
    @app.errorhandler(ConnectionError)
    def handle_connection_error(err):
        return error_response("Database connection error. Please check your database and network connection.", 500, "ConnectionError")

    @app.errorhandler(500)
    def handle_server_error(err):
        return error_response("Server error occurred. Please try again later.", 500, "ServerError")
    
    @app.errorhandler(502)
    def handle_bad_gateway(err):
        return error_response("Bad gateway. The server received an invalid response, please try again soon.", 502, "BadGateway")

# ========== UNEXPECTED / FALLBACK ==========
    @app.errorhandler(Exception)
    def handle_uncaught_exception(err):
        return error_response("An unexpected error occurred. Please try again later or contact support.", 500, "UnexpectedError")
