"""Controller for Organiser-related routes and logic.
Handles all CRUD operations/logic for organisers:
    - Get all organisers
    - Get one organiser by ID
    - Create a new organiser
    - Update an existing organiser
    - Delete an organiser

Note: IntegrityError and ValidationError are handled globally in utils.error_handlers.
"""

from flask import Blueprint, jsonify, request
from sqlalchemy.exc import IntegrityError
from marshmallow import ValidationError

from init import db
from models.organiser import Organiser
from schemas.schemas import organiser_schema, organisers_schema

organisers_bp = Blueprint("organisers", __name__, url_prefix = "/organisers")

# GET / (get all organisers)
@organisers_bp.route("/", methods = ["GET"])
def get_organisers():
    stmt = db.select(Organiser)
    organisers_list = db.session.scalars(stmt)
    data = organisers_schema.dump(organisers_list)
    if not data:
        return {"message": "No organisers found."}, 200
    return jsonify(data), 200
     
# GET /id (get one organiser by id)
@organisers_bp.route("/<int:organiser_id>", methods = ["GET"])
def get_one_organiser(organiser_id):
    stmt = db.select(Organiser).where(Organiser.organiser_id == organiser_id)
    organiser = db.session.scalar(stmt)
    data = organiser_schema.dump(organiser)
    if data:
        return jsonify(data), 200
    else:
        return {"message": f"Organiser with id {organiser_id} doesn't exist."}, 404
    
# POST / (create a new organiser)
@organisers_bp.route("/", methods = ["POST"])
def create_organiser():
    body_data = request.get_json()
    new_organiser = organiser_schema.load(
        body_data,
        session = db.session
    )
    db.session.add(new_organiser)
    db.session.commit()
    return organiser_schema.dump(new_organiser), 201

# PATCH/PUT /id (update organiser by id)
@organisers_bp.route("/<int:organiser_id>", methods = ["PUT", "PATCH"])
def update_organiser(organiser_id):
    stmt = db.select(Organiser).where(Organiser.organiser_id == organiser_id)
    organiser = db.session.scalar(stmt)
    if not organiser:
        return {"message": f"Organiser with id {organiser_id} doesn't exist."}, 404
    else:
        try:
            update_organiser = organiser_schema.load(
                request.get_json(),
                instance = organiser,
                session = db.session,
                partial = True
            )
            db.session.commit()
            return organiser_schema.dump(update_organiser), 200
        except ValidationError as err:
            return jsonify(err.messages), 400
        except IntegrityError as err:
            db.session.rollback()
            return {"message": str(err.orig) if getattr(err, 'orig', None) else str(err)}, 400

# DELETE /id (delete organiser by id)
@organisers_bp.route("/<int:organiser_id>", methods = ["DELETE"])
def delete_organiser(organiser_id):
    stmt = db.select(Organiser).where(Organiser.organiser_id == organiser_id)
    organiser = db.session.scalar(stmt)
    if organiser:
        db.session.delete(organiser)
        db.session.commit()
        return {"message": f"Organiser with id {organiser_id} has been deleted."}, 200
    else:
        return {"message": f"Organiser with id {organiser_id} doesn't exist."}, 404