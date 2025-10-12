"""Controller for Event-related routes and logic.
Handles all CRUD operations/logic for events:
    - Get all events
    - Get one event by ID
    - Create a new event
    - Update an existing event
    - Delete an event (cancelling all associated bookings)
    
Note: IntegrityError and ValidationError are handled globally in utils.error_handlers.
"""

from flask import Blueprint, jsonify, request
from sqlalchemy.exc import IntegrityError
from marshmallow import ValidationError

from init import db
from models.event import Event
from models.booking import BookingStatus
from schemas.schemas import event_schema, events_schema

events_bp = Blueprint("events", __name__, url_prefix = "/events")

# GET / (get all events)
@events_bp.route("/", methods = ["GET"])
def get_events():
    stmt = db.select(Event)
    events_list = db.session.scalars(stmt)
    data = events_schema.dump(events_list)
    if not data:
        return {"message": "No events found. Please add an event to get started."}, 404
    return jsonify(data), 200

# GET /id (get one event by id)
@events_bp.route("/<int:event_id>", methods = ["GET"])
def get_one_event(event_id):
    stmt = db.select(Event).where(Event.event_id == event_id)
    event = db.session.scalar(stmt)
    data = event_schema.dump(event)
    if data:
        return jsonify(data), 200
    else:
        return {"message": f"Event with id {event_id} doesn't exist."}, 404

# POST / (create a new event)
@events_bp.route("/", methods = ["POST"])
def create_a_event():
    body_data = request.get_json()
    new_event = event_schema.load(
        body_data,
        session = db.session
    )
    db.session.add(new_event)
    db.session.commit()
    return event_schema.dump(new_event), 201

# PATCH/PUT /id (update event by id)
@events_bp.route("/<int:event_id>", methods = ["PUT", "PATCH"])
def update_a_event(event_id):
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
    
# DELETE /id (delete event by id)
@events_bp.route("/<int:event_id>", methods = ["DELETE"])
def delete_a_event(event_id):
    stmt = db.select(Event).where(Event.event_id == event_id)
    event = db.session.scalar(stmt)
    if event:
        for show in event.shows:  # Cancel all bookings for all related shows
            for booking in show.bookings:
                booking.booking_status = BookingStatus.CANCELLED
        
        db.session.delete(event)
        db.session.commit()
        return {"message": f"Event with id {event_id} has been deleted and all bookings cancelled."}, 200
    else:
        return {"message": f"Event with id {event_id} doesn't exist."}, 404