"""Controller for Event-related routes and logic.
Handles all CRUD operations/logic for events:
    - Get all events
    - Get one event by ID
    - Create a new event
    - Update an existing event
    - Cancel an event (cancelling all associated bookings)
    
Note:
    - IntegrityError and ValidationError are handled globally in utils.error_handlers.
"""

from flask import Blueprint, jsonify, request
from sqlalchemy.exc import IntegrityError
from marshmallow import ValidationError

from init import db
from models.event import Event
from models.show import ShowStatus
from utils.constraints import BookingStatus
from schemas.event_schema import event_schema, events_schema

events_bp = Blueprint("events", __name__, url_prefix = "/events")

# ========= GET ALL EVENTS =========
@events_bp.route("/", methods = ["GET"])
def get_events():
    """Retrieve all events."""
    stmt = db.select(Event)
    events_list = db.session.scalars(stmt)
    data = events_schema.dump(events_list)
    if not data:
        return {"message": "No events found. Please add an event to get started."}, 200
    return jsonify(data), 200

# ========= GET ONE EVENT =========
@events_bp.route("/<int:event_id>", methods = ["GET"])
def get_one_event(event_id):
    """Retrieve one event by ID."""
    stmt = db.select(Event).where(Event.event_id == event_id)
    event = db.session.scalar(stmt)
    data = event_schema.dump(event)
    if data:
        return jsonify(data), 200
    else:
        return {"message": f"Event with id {event_id} doesn't exist."}, 404

# ========= CREATE NEW EVENT =========
@events_bp.route("/", methods = ["POST"])
def create_event():
    """Create a new event."""
    body_data = request.get_json()
    new_event = event_schema.load(
        body_data,
        session = db.session
    )
    db.session.add(new_event)
    db.session.commit()
    return event_schema.dump(new_event), 201

# ========= UPDATE EVENT =========
@events_bp.route("/<int:event_id>", methods = ["PUT", "PATCH"])
def update_event(event_id):
    """Update an existing event by ID."""
    stmt = db.select(Event).where(Event.event_id == event_id)
    event = db.session.scalar(stmt)
    if not event:
        return {"message": f"Event with id {event_id} doesn't exist."}, 404
    else:
        try:
            update_event = event_schema.load(
                request.get_json(),
                instance = event,
                session = db.session,
                partial = True
            )
            db.session.commit()
            return event_schema.dump(update_event), 200
        except ValidationError as err:
            return jsonify(err.messages), 400
        except IntegrityError as err:
            db.session.rollback()
            return {"message": str(err.orig) if getattr(err, 'orig', None) else str(err)}, 400

# ========= CANCEL EVENT =========
@events_bp.route("/<int:event_id>", methods = ["DELETE"])
def delete_event(event_id):
    """Cancel an event by ID. Cancelling all associated shows and bookings."""
    stmt = db.select(Event).where(Event.event_id == event_id)
    event = db.session.scalar(stmt)
    if event:
        for show in event.shows:  # Cancel all shows for this event
            show.show_status = ShowStatus.CANCELLED
            for booking in show.bookings:  # Cancel all bookings for this show
                booking.booking_status = BookingStatus.CANCELLED
        
        db.session.commit()
        return {"message": f"Event with id {event_id} has been cancelled. All shows and bookings cancelled."}, 200
    else:
        return {"message": f"Event with id {event_id} doesn't exist."}, 404