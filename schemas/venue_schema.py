"""Schemas for serializing, deserializing, and validating Venue-related data.

Defines Marshmallow schemas for the Venue model, including field validation,
normalization, and nested relationships. Used for input validation and output
formatting in API endpoints and data processing.
"""

from marshmallow_sqlalchemy import SQLAlchemyAutoSchema, auto_field
from marshmallow import fields, pre_load, post_load, validate, ValidationError

from init import db
from models.venue import Venue
from utils.validators import venue_name_validators, venue_location_validators

class VenueSchema(SQLAlchemyAutoSchema):
    """Schema for Venue model with nested shows, proper-case normalization, 
    field validations, and uniqueness enforcement.

    Attributes:
        venue_id (int)
        name (str)
        location (str)
        capacity (int)
        shows (list[Show]): Nested shows for display (only show_id, date_time and event.title).

    Validations:
        - Name format
        - Location format
        - Capacity range

    Pre-load:
        - Trim whitespace
        - Proper-case name
        
    Post-load:
        - Ensure venue name is unique in the database
    """
    class Meta:
        model = Venue
        load_instance = True
        include_relationships = True
        fields = ("venue_id", "name", "location", "capacity", "shows")
    
    shows = fields.List(fields.Nested("ShowSchema", only = ("show_id", "date_time", "event")))
    
    name = auto_field(required = True, validate = venue_name_validators)
    location = auto_field(required = True, validate = venue_location_validators)
    capacity = fields.Integer(required = True, validate = [validate.Range(min = 1, max = 200000, error = "Capacity must be a number between 1 and 200,000")])
    
    @pre_load
    def normalize_venue(self, data, **kwargs):
        if isinstance(data, dict):
            name = data.get('name')
            if isinstance(name, str):
                data['name'] = name.strip()
            location = data.get('location')
            if isinstance(location, str):
                data['location'] = location.strip()
        return data

    @post_load
    def check_uniqueness(self, data, **kwargs):
        name = data.get('name')
        if name:
            query = db.session.query(Venue).filter_by(name = name)
            if getattr(self, 'instance', None):
                query = query.filter(Venue.venue_id != self.instance.venue_id)
            if query.first():
                raise ValidationError({"name": ["Venue name already exists."]})
        return data

venue_schema = VenueSchema()
venues_schema = VenueSchema(many = True)