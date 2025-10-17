"""Controller for TicketHolder-related routes and logic.
Handles all CRUD operations/logic for ticket holders:
    - Get all ticket holders
    - Get one ticket holder by ID
    - Create a new ticket holder
    - Update an existing ticket holder
    - Delete a ticket holder

Note: IntegrityError and ValidationError are handled globally in utils.error_handlers.
"""

from datetime import datetime

from flask import Blueprint, jsonify, request
from sqlalchemy.exc import IntegrityError
from marshmallow import ValidationError

from init import db
from models.ticket_holder import TicketHolder
from models.booking import BookingStatus
from schemas.schemas import ticket_holder_schema, ticket_holders_schema

ticket_holders_bp = Blueprint("ticket_holders", __name__, url_prefix = "/ticket_holders")

# GET / (get all ticket_holders)
@ticket_holders_bp.route("/", methods = ["GET"])
def get_ticket_holders():
    stmt = db.select(TicketHolder)
    ticket_holders_list = db.session.scalars(stmt)
    data = ticket_holders_schema.dump(ticket_holders_list)
    if not data:
        return {"message": "No ticket holders found."}, 200
    return jsonify(data), 200

# GET /id (get one ticket holder by id)
@ticket_holders_bp.route("/<int:ticket_holder_id>", methods = ["GET"])
def get_one_ticket_holder(ticket_holder_id):
    stmt = db.select(TicketHolder).where(TicketHolder.ticket_holder_id == ticket_holder_id)
    ticket_holder = db.session.scalar(stmt)
    data = ticket_holder_schema.dump(ticket_holder)
    if data:
        return jsonify(data), 200
    else:
        return {"message": f"Ticket holder with id {ticket_holder_id} doesn't exist."}, 404

# POST / (create a new ticket holder)
@ticket_holders_bp.route("/", methods = ["POST"])
def create_ticket_holder():
    body_data = request.get_json()
    new_ticket_holder = ticket_holder_schema.load(
        body_data,
        session = db.session
    )
    db.session.add(new_ticket_holder)
    db.session.commit()
    return ticket_holder_schema.dump(new_ticket_holder), 201

# PATCH/PUT /id (update ticket holder by id)
@ticket_holders_bp.route("/<int:ticket_holder_id>", methods = ["PUT", "PATCH"])
def update_ticket_holder(ticket_holder_id):
    stmt = db.select(TicketHolder).where(TicketHolder.ticket_holder_id == ticket_holder_id)
    ticket_holder = db.session.scalar(stmt)
    if not ticket_holder:
        return {"message": f"Ticket holder with id {ticket_holder_id} doesn't exist."}, 404
    else:
        try:
            update_ticket_holder = ticket_holder_schema.load(
                request.get_json(),
                instance = ticket_holder,
                session = db.session,
                partial = True
            )
            db.session.commit()
            return ticket_holder_schema.dump(update_ticket_holder), 200
        except ValidationError as err:
            return jsonify(err.messages), 400
        except IntegrityError as err:
            db.session.rollback()
            return {"message": str(err.orig) if getattr(err, 'orig', None) else str(err)}, 400
    
# DELETE /id (delete ticket holder by id)
@ticket_holders_bp.route("/<int:ticket_holder_id>", methods = ["DELETE"])
def delete_ticket_holder(ticket_holder_id):
    stmt = db.select(TicketHolder).where(TicketHolder.ticket_holder_id == ticket_holder_id)
    ticket_holder = db.session.scalar(stmt)
    if ticket_holder:
        current_date = datetime.now()
        future_confirmed_bookings = [
            booking for booking in ticket_holder.bookings
            if booking.booking_status == BookingStatus.CONFIRMED and booking.show and booking.show.date_time > current_date
        ]
        if future_confirmed_bookings:
            return {"message": f"Ticket holder with id {ticket_holder_id} can't be deleted because they have future confirmed bookings."}, 400
        db.session.delete(ticket_holder)
        db.session.commit()
        return {"message": f"Ticket holder with id {ticket_holder_id} has been deleted."}, 200
    else:
        return {"message": f"Ticket holder with id {ticket_holder_id} doesn't exist."}, 404