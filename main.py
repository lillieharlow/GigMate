"""Flask application factory and configuration.
Sets up the Flask app, database connection, and registers blueprints.
"""

import os

from flask import Flask
from dotenv import load_dotenv

from init import db
from controllers.cli_controller import db_commands
from controllers.ticket_holder_controller import ticket_holders_bp
from controllers.organiser_controller import organisers_bp
from controllers.venue_controller import venues_bp
from controllers.event_controller import events_bp
from controllers.show_controller import shows_bp
from controllers.booking_controller import bookings_bp
from utils.error_handlers import error_handlers

load_dotenv()

def create_app():
    """Create and configure the Flask application.
    Returns: Flask app instance.
    """
    app = Flask(__name__)
    print("Flask server started.")
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get("DATABASE_URI")
    app.json.sort_keys = False # keep order of keys in JSON
    db.init_app(app)
    app.register_blueprint(db_commands)
    app.register_blueprint(ticket_holders_bp)
    app.register_blueprint(organisers_bp)
    app.register_blueprint(venues_bp)
    app.register_blueprint(events_bp)
    app.register_blueprint(shows_bp)
    app.register_blueprint(bookings_bp)

    error_handlers(app)
    return app