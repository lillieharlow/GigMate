"""Controller for Booking-related routes and logic.
Handles all CRUD operations/logic for bookings:
    - Get all bookings
    - Get one booking by ID
    - Create a new booking
    - Update an existing booking
    - Delete a booking

Note:
    - IntegrityError and ValidationError are handled globally in utils.error_handlers.
    - Pagination is implemented for retrieving all bookings, 10 bookings per page.
"""

from flask import Blueprint, jsonify, request
from sqlalchemy.exc import IntegrityError
from marshmallow import ValidationError

from init import db
from models.booking import Booking
from schemas.booking_schema import booking_schema, bookings_schema

bookings_bp = Blueprint("bookings", __name__, url_prefix = "/bookings")

# ======== GET ALL BOOKINGS ========
@bookings_bp.route("/", methods=["GET"])
def get_bookings():
    """Retrieve all bookings with pagination."""
    page = int(request.args.get("page", 1))
    per_page = int(request.args.get("per_page", 10))
    bookings_list = Booking.query.paginate(page=page, per_page=per_page, error_out=False)
    data = bookings_schema.dump(bookings_list.items)
    if not data:
        return {"message": "No bookings found. Please add a booking to get started."}, 200
    return {
        "bookings": data,
        "page": page,
        "per_page": per_page,
        "total": bookings_list.total,
        "pages": bookings_list.pages
    }, 200

# ========= GET ONE BOOKING ========
@bookings_bp.route("/<int:booking_id>", methods = ["GET"])
def get_one_booking(booking_id):
    """Retrieve one booking by ID."""
    stmt = db.select(Booking).where(Booking.booking_id == booking_id)
    booking = db.session.scalar(stmt)
    data = booking_schema.dump(booking)
    if data:
        return jsonify(data), 200
    else:
        return {"message": f"Booking with id {booking_id} doesn't exist."}, 404

# ========= CREATE NEW BOOKING =========
@bookings_bp.route("/", methods = ["POST"])
def create_booking():
    """Create a new booking."""
    body_data = request.get_json()
    new_booking = booking_schema.load(
        body_data,
        session = db.session
    )
    db.session.add(new_booking)
    db.session.commit()
    return booking_schema.dump(new_booking), 201

# ========= UPDATE BOOKING =========
@bookings_bp.route("/<int:booking_id>", methods = ["PUT", "PATCH"])
def update_booking(booking_id):
    """Update an existing booking by ID."""
    stmt = db.select(Booking).where(Booking.booking_id == booking_id)
    booking = db.session.scalar(stmt)
    if not booking:
        return {"message": f"Booking with id {booking_id} doesn't exist."}, 404
    else:
        try:
            update_booking = booking_schema.load(
                request.get_json(),
                instance = booking,
                session = db.session,
                partial = True
            )
            db.session.commit()
            return booking_schema.dump(update_booking), 200
        except ValidationError as err:
            return jsonify(err.messages), 400
        except IntegrityError as err:
            db.session.rollback()
            return {"message": str(err.orig) if getattr(err, 'orig', None) else str(err)}, 400
    
# ========= DELETE BOOKING =========
@bookings_bp.route("/<int:booking_id>", methods = ["DELETE"])
def delete_booking(booking_id):
    """Delete a booking by ID."""
    stmt = db.select(Booking).where(Booking.booking_id == booking_id)
    booking = db.session.scalar(stmt)
    if booking:
        db.session.delete(booking)
        db.session.commit()
        return {"message": f"Booking id {booking_id} has been deleted."}, 200
    else:
        return {"message": f"Booking with id {booking_id} doesn't exist."}, 404