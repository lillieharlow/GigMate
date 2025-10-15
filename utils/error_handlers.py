from flask import jsonify
from marshmallow import ValidationError
from sqlalchemy.exc import IntegrityError, DataError
from psycopg2 import errorcodes

def error_handlers(app):
    @app.errorhandler(ValidationError)
    def handle_validation_error(err):
        return jsonify(err.messages), 400
    
    @app.errorhandler(IntegrityError)
    def handle_integrity_error(err):
        if hasattr(err, "orig") and err.orig:
            if err.orig.pgcode == errorcodes.NOT_NULL_VIOLATION:
                return {"message": f"Required field: {err.orig.diag.column_name} cannot be null."}, 409
        
            if err.orig.pgcode == errorcodes.UNIQUE_VIOLATION:
                return {"message": err.orig.diag.message_detail}, 409
            
            if err.orig.pgcode == errorcodes.FOREIGN_KEY_VIOLATION:
                return {"message": err.orig.diag.message_detail}, 409
            
            if err.orig.pgcode == errorcodes.CHECK_VIOLATION:
                if 'check_future_show' in str(err.orig):
                    return {"message": "Shows can only be scheduled for future dates and times."}, 400
                return {"message": err.orig.diag.message_detail}, 409
            else:
                return {"message": "Unknown integrity error occured."}, 409
        else:
            return  {"message": "Integrity Error occured."}, 409
        
    @app.errorhandler(DataError)
    def handle_data_error(err):
        return {"message": f"{err.orig.diag.message_primary}"}, 409
    
    @app.errorhandler(404)
    def handle_404(err):
        return {"message": "Requested resource not found/ does not exist."}, 404
    
    @app.errorhandler(500)
    def handle_server_related_errors(err):
        return {"message": "Server error occured. Please contact the site administration."}, 500
    