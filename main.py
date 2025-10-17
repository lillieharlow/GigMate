"""Flask application factory and configuration for the GigMate API.

Sets up the Flask app, database connection, registers blueprints, 
and attaches centralized error handlers.
"""

import os

from flask import Flask, jsonify
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
    Returns: Configured Flask app instance.
    """
    app = Flask(__name__)
    print("Flask server started.")
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv("DATABASE_URI")
    app.json.sort_keys = False # keep order of keys in JSON
    db.init_app(app) # Initialize the database with the app
    app.register_blueprint(db_commands) # Register CLI commands blueprint
    app.register_blueprint(ticket_holders_bp) # Register API blueprints
    app.register_blueprint(organisers_bp)
    app.register_blueprint(venues_bp)
    app.register_blueprint(events_bp)
    app.register_blueprint(shows_bp)
    app.register_blueprint(bookings_bp)

    error_handlers(app) # Register global error handlers
    
    @app.route("/") # Define home route with detailed welcome message
    def home():
        return jsonify({
        "message": """Rock Your Music Events with Ease. GigMate is your backstage pass to managing music tours, venues, organisers, and ticket bookings - all through a powerful RESTful API.

From underground gigs to sold-out stadiums - GigMate keeps your tour in tune, your shows scheduled, and your fans hyped.

Plan. Book. Sell out. Repeat.

Built for developers who want a clean, reliable backend for music events."""
    }), 200

    return app