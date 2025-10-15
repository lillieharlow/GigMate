"""Controller for Venue-related routes and logic.
Handles all CRUD operations/logic for venues:
    - Get all venues
    - Get one venue by ID
    - Create a new venue
    - Update an existing venue
    - Delete a venue

Note: IntegrityError and ValidationError are handled globally in utils.error_handlers.
"""

from flask import Blueprint, jsonify, request
from sqlalchemy.exc import IntegrityError
from marshmallow import ValidationError

from init import db
from models.venue import Venue
from schemas.schemas import venue_schema, venues_schema

venues_bp = Blueprint("venues", __name__, url_prefix = "/venues")

# GET / (get all venues)
@venues_bp.route("/", methods = ["GET"])
def get_venues():
    stmt = db.select(Venue)
    venues_list = db.session.scalars(stmt)
    data = venues_schema.dump(venues_list)
    if not data:
        return {"message": "No venues found. Please add a venue to get started."}, 404
    return jsonify(data), 200

# GET /id (get one venue by id)
@venues_bp.route("/<int:venue_id>", methods = ["GET"])
def get_one_venue(venue_id):
    stmt = db.select(Venue).where(Venue.venue_id == venue_id)
    venue = db.session.scalar(stmt)
    data = venue_schema.dump(venue)
    if data:
        return jsonify(data), 200
    else:
        return {"message": f"Venue with id {venue_id} doesn't exist."}, 404
    
# POST / (create a new venue)
@venues_bp.route("/", methods = ["POST"])
def create_a_venue():
    body_data = request.get_json()
    new_venue = venue_schema.load(
        body_data,
        session = db.session
    )
    db.session.add(new_venue)
    db.session.commit()
    return venue_schema.dump(new_venue), 201

# PATCH/PUT /id (update venue by id)
@venues_bp.route("/<int:venue_id>", methods=["PUT", "PATCH"])
def update_a_venue(venue_id):
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
    
# DELETE /id (delete venue by id)
@venues_bp.route("/<int:venue_id>", methods = ["DELETE"])
def delete_a_venue(venue_id):
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