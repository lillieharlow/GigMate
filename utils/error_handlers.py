from flask import jsonify
from marshmallow import ValidationError
from sqlalchemy.exc import IntegrityError, DataError
from psycopg2 import errorcodes
from flask.cli import NoAppException

def error_handlers(app):
    @app.errorhandler(ValidationError)
    def handle_validation_error(err):
        return jsonify(err.messages), 400
    
    @app.errorhandler(ImportError)
    def handle_import_error(err):
        return {"message": f"Import error: {str(err)}. Please check your dependencies."}, 500
    
    @app.errorhandler(ModuleNotFoundError)
    def handle_module_not_found_error(err):
        return {"message": f"Module not found: {str(err)}. Please check your imports."}, 500
    
    @app.errorhandler(IntegrityError)
    def handle_integrity_error(err):
        if hasattr(err, "orig") and err.orig:
            if err.orig.pgcode == errorcodes.NOT_NULL_VIOLATION:
                return {"message": f"Missing required field: {err.orig.diag.column_name}."}, 409
        
            if err.orig.pgcode == errorcodes.UNIQUE_VIOLATION:
                detail = err.orig.diag.message_detail
                if 'already exists' in detail:
                    return {"message": f"This item already exists. {detail}"}, 409
                return {"message": f"This item cannot be duplicated. {detail}"}, 409
            
            if err.orig.pgcode == errorcodes.FOREIGN_KEY_VIOLATION:
                detail = err.orig.diag.message_detail if hasattr(err.orig.diag, 'message_detail') else str(err)
                return {"message": "A referenced value does not exist. Please check that all foreign key IDs (such as venue, event, organiser, etc.) are valid and present in the database."}, 409
            
            if err.orig.pgcode == errorcodes.CHECK_VIOLATION:
                if 'check_future_show' in str(err.orig):
                    return {"message": "Shows must be scheduled for future dates and times."}, 400
                return {"message": err.orig.diag.message_detail}, 409
            else:
                return {"message": "Unknown integrity error occured."}, 409
        else:
            return  {"message": "Integrity Error occured."}, 409
        
    @app.errorhandler(DataError)
    def handle_data_error(err):
        msg = ""
        if hasattr(err.orig, "diag") and hasattr(err.orig.diag, "message_primary"):
            msg = err.orig.diag.message_primary
        elif hasattr(err.orig, "args") and err.orig.args:
            msg = err.orig.args[0]
        if "date/time" in msg or "out of range" in msg or "invalid input syntax for type timestamp" in msg:
            return {
                "message": "Invalid date/time value. Please use DD-MM-YYYY | HH:MM AM/PM (e.g., '27-11-2025 | 08:30 PM')."
            }, 400
        return {"message": msg}, 409

    @app.errorhandler(TypeError)
    def handle_type_error(err):
        return {"message": "Invalid data format. Please check your input."}, 400
    
    @app.errorhandler(AttributeError)
    def handle_attribute_error(err):
        return {"message": "Missing required data. Please check your request."}, 400
    
    @app.errorhandler(400)
    def handle_bad_request(err):
        if 'JSON' in str(err) or 'decode' in str(err):
            return {"message": "Invalid JSON format. Check for syntax errors in your request."}, 400
        return {"message": "Invalid request. Please check your data and try again."}, 400
    
    @app.errorhandler(404)
    def handle_404(err):
        return {"message": "Resource not found. Please check the URL."}, 404
    
    @app.errorhandler(405)
    def handle_method_not_allowed(err):
        return {"message": "Method not allowed. Please check the HTTP method."}, 405
    
    @app.errorhandler(500)
    def handle_server_related_errors(err):
        return {"message": "Server error occurred. Please try again later."}, 500
