"""Controller for Show-related routes and logic.
Handles all CRUD operations/logic for shows:
    - Get all shows
    - Get one show by ID
    - Create a new show
    - Update an existing show
    - Cancel a show (cancelling all associated bookings)

Note: IntegrityError and ValidationError are handled globally in utils.error_handlers.
"""
from flask import Blueprint, jsonify, request
from sqlalchemy.exc import IntegrityError
from marshmallow import ValidationError

from init import db
from models.show import Show, ShowStatus
from utils.constraints import BookingStatus
from schemas.schemas import show_schema, shows_schema

shows_bp = Blueprint("shows", __name__, url_prefix = "/shows")

# GET / (get all shows)
@shows_bp.route("/", methods = ["GET"])
def get_shows():
    stmt = db.select(Show)
    shows_list = db.session.scalars(stmt)
    data = shows_schema.dump(shows_list)
    if not data:
        return {"message": "No shows found. Please add a show to get started."}, 200
    return jsonify(data), 200

# GET /id (get one show by id)
@shows_bp.route("/<int:show_id>", methods = ["GET"])
def get_one_show(show_id):
    stmt = db.select(Show).where(Show.show_id == show_id)
    show = db.session.scalar(stmt)
    data = show_schema.dump(show)
    if data:
        return jsonify(data), 200
    else:
        return {"message": f"Show with id {show_id} doesn't exist."}, 404

# POST / (create a new show)
"""venue_id is nullable to allow for pop-up events without a fixed venue.
try/except block added to catch IntegrityError from UniqueConstraint on (event_id, venue_id, date_time)
otherwise duplicate shows could be created."""
@shows_bp.route("/", methods=["POST"])
def create_show():
    """Create a new show. Checks for duplicates by event_id, date_time, and venue_id."""
    body_data = request.get_json()
    try: # Load and validate via schema (handles date_time parsing)
        new_show = show_schema.load(body_data, session=db.session)
    except ValidationError as ve:
        return {"message": ve.messages}, 400

    duplicate = db.session.query(Show).filter( # Check for duplicate show
        Show.event_id == new_show.event_id,
        Show.date_time == new_show.date_time,
        Show.venue_id == new_show.venue_id
    ).first()

    if duplicate:
        return {"message": "A show for this event, date, and venue already exists."}, 409

    db.session.add(new_show)
    db.session.commit()
    return show_schema.dump(new_show), 201

# PATCH/PUT /id (update show by id)
@shows_bp.route("/<int:show_id>", methods = ["PUT", "PATCH"])
def update_show(show_id):
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
    
# DELETE /id (cancel show by id)
"""Shows are not deleted from the database to preserve historical/audit data.
Instead, all associated bookings are cancelled."""

@shows_bp.route("/<int:show_id>", methods = ["DELETE"])
def delete_show(show_id):
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
