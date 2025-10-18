"""Controller for Venue-related routes and logic.
Handles all CRUD operations/logic for venues:
    - Get all venues
    - Get one venue by ID
    - Create a new venue
    - Update an existing venue
    - Delete a venue

Note:
    - IntegrityError and ValidationError are handled globally in utils.error_handlers.
"""

from flask import Blueprint, jsonify, request
from sqlalchemy.exc import IntegrityError
from marshmallow import ValidationError

from init import db
from models.venue import Venue
from schemas.venue_schema import venue_schema, venues_schema

venues_bp = Blueprint("venues", __name__, url_prefix = "/venues")

# ========= GET ALL VENUES =========
@venues_bp.route("/", methods = ["GET"])
def get_venues():
    """Retrieve all venues."""
    stmt = db.select(Venue)
    venues_list = db.session.scalars(stmt)
    data = venues_schema.dump(venues_list)
    if not data:
        return {"message": "No venues found. Please add a venue to get started."}, 200
    return jsonify(data), 200

# ========= GET ONE VENUE =========
@venues_bp.route("/<int:venue_id>", methods = ["GET"])
def get_one_venue(venue_id):
    """Retrieve one venue by ID."""
    stmt = db.select(Venue).where(Venue.venue_id == venue_id)
    venue = db.session.scalar(stmt)
    data = venue_schema.dump(venue)
    if data:
        return jsonify(data), 200
    else:
        return {"message": f"Venue with id {venue_id} doesn't exist."}, 404

# ========= CREATE NEW VENUE =========
@venues_bp.route("/", methods = ["POST"])
def create_venue():
    """Create a new venue."""
    body_data = request.get_json()
    new_venue = venue_schema.load(
        body_data,
        session = db.session
    )
    db.session.add(new_venue)
    db.session.commit()
    return venue_schema.dump(new_venue), 201

# ========= UPDATE VENUE =========
@venues_bp.route("/<int:venue_id>", methods=["PUT", "PATCH"])
def update_venue(venue_id):
    """Update an existing venue by ID."""
    stmt = db.select(Venue).where(Venue.venue_id == venue_id)
    venue = db.session.scalar(stmt)
    if not venue:
        return {"message": f"Venue with id {venue_id} doesn't exist."}, 404
    try:
        update_venue = venue_schema.load(
            request.get_json(),
            instance=venue,
            session=db.session,
            partial=True,
        )
        db.session.commit()
        return venue_schema.dump(update_venue), 200
    except ValidationError as err:
        return jsonify(err.messages), 400
    except IntegrityError as err:
        db.session.rollback()
        return {"message": str(err.orig) if getattr(err, 'orig', None) else str(err)}, 400

# ========= DELETE VENUE =========
@venues_bp.route("/<int:venue_id>", methods = ["DELETE"])
def delete_venue(venue_id):
    """Delete a venue by ID. Updates related shows to display 'Venue To Be Announced'."""
    stmt = db.select(Venue).where(Venue.venue_id == venue_id)
    venue = db.session.scalar(stmt)
    if venue:
        show_count = len(venue.shows) if venue.shows else 0
        db.session.delete(venue)
        db.session.commit()
        if show_count > 0:
            return {"message": f"Venue with id {venue_id} has been deleted. {show_count} shows now display 'Venue To Be Announced'."}, 200
        else:
            return {"message": f"Venue with id {venue_id} has been deleted."}, 200
    else:
        return {"message": f"Venue with id {venue_id} doesn't exist."}, 404