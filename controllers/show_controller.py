"""Controller for Show-related routes and logic.
Handles all CRUD operations/logic for shows:
    - Get all shows
    - Get one show by ID
    - Create new show
    - Update existing show
    - Cancel show (cancelling all associated bookings)

Note:
    - IntegrityError and ValidationError are handled globally in utils.error_handlers.
    - Shows are never deleted from the database for audit/history purposes.
"""
from flask import Blueprint, jsonify, request
from sqlalchemy.exc import IntegrityError
from marshmallow import ValidationError

from init import db
from models.show import Show, ShowStatus
from utils.constraints import BookingStatus
from schemas.show_schema import show_schema, shows_schema

shows_bp = Blueprint("shows", __name__, url_prefix = "/shows")

# ========= GET ALL SHOWS =========
@shows_bp.route("/", methods = ["GET"])
def get_shows():
    """Retrieve all shows from the database."""
    stmt = db.select(Show)
    shows_list = db.session.scalars(stmt)
    data = shows_schema.dump(shows_list)
    if not data:
        return {"message": "No shows found. Please add a show to get started."}, 200
    return jsonify(data), 200

# ========= GET ONE SHOW =========
@shows_bp.route("/<int:show_id>", methods = ["GET"])
def get_one_show(show_id):
    """Retrieve a single show by its ID."""
    stmt = db.select(Show).where(Show.show_id == show_id)
    show = db.session.scalar(stmt)
    data = show_schema.dump(show)
    if data:
        return jsonify(data), 200
    else:
        return {"message": f"Show with id {show_id} doesn't exist."}, 404

# ========= CREATE NEW SHOW =========
@shows_bp.route("/", methods=["POST"])
def create_show():
    """Create a new show. Prevents duplicates by event_id, date_time, and venue_id."""
    body_data = request.get_json()
    new_show = show_schema.load(
        body_data, 
        session = db.session
    )

    existing_show = db.session.query(Show).filter( # Check if show already exists for this event, date and venue
        Show.event_id == new_show.event_id,
        Show.date_time == new_show.date_time,
        Show.venue_id == new_show.venue_id
    ).first()

    if existing_show:
        return {"message": "A show for this event, date, and venue already exists."}, 409

    db.session.add(new_show)
    db.session.commit()
    return show_schema.dump(new_show), 201

# ========= UPDATE SHOW =========
@shows_bp.route("/<int:show_id>", methods = ["PUT", "PATCH"])
def update_show(show_id):
    """Update existing show by its ID."""
    stmt = db.select(Show).where(Show.show_id == show_id)
    show = db.session.scalar(stmt)
    if not show:
        return {"message": f"Show with id {show_id} doesn't exist."}, 404
    else:
        try:
            update_show = show_schema.load(
                request.get_json(),
                instance = show,
                session = db.session,
                partial = True
            )
            db.session.commit()
            return show_schema.dump(update_show), 200
        except ValidationError as err:
            return jsonify(err.messages), 400
        except IntegrityError as err:
            db.session.rollback()
            return {"message": str(err.orig) if getattr(err, 'orig', None) else str(err)}, 400
    
# ========= CANCEL SHOW =========
@shows_bp.route("/<int:show_id>", methods = ["DELETE"])
def delete_show(show_id):
    """Cancel a show by its ID. Cancels all associated bookings."""
    stmt = db.select(Show).where(Show.show_id == show_id)
    show = db.session.scalar(stmt)
    if not show:
        return {"message": f"Show with id {show_id} doesn't exist."}, 404

    show.show_status = ShowStatus.CANCELLED
    
    # Cancel all bookings for this show
    for booking in show.bookings:
        booking.booking_status = BookingStatus.CANCELLED
    
    db.session.commit()
    return {"message": f"Show id {show_id} has been cancelled. All bookings for this show cancelled."}, 200
