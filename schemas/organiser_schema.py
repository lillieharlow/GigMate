"""Schemas for serializing, deserializing, and validating Organiser-related data.

Defines Marshmallow schemas for the Organiser model, including field validation,
normalization, and nested event relationships. Used for input validation and
output formatting in API endpoints and data processing.
"""

from marshmallow_sqlalchemy import SQLAlchemyAutoSchema, auto_field
from marshmallow import fields, pre_load, post_load, ValidationError

from init import db
from models.organiser import Organiser
from utils.validators import email_validators, phone_validators, full_name_validators

class OrganiserSchema(SQLAlchemyAutoSchema):
    """Schema for Organiser model with nested events and field validations.

    Attributes:
        organiser_id (int)
        full_name (str)
        email (str)
        phone_number (str)
        events (list[Event]): Nested events for display (only event_id and title).

    Validations:
        - Full name format
        - Email format
        - Phone number format

    Pre-load:
        - Trim whitespace
        - Lowercase email
        
    Post-load:
        - Ensure email and phone number are unique in the database
    """
    class Meta:
        model = Organiser
        load_instance = True
        include_relationships = True
        fields = ("organiser_id", "full_name", "email", "phone_number", "events")

    events = fields.List(fields.Nested("EventSchema", only = ("event_id", "title")))
    
    full_name = auto_field(required = True, validate = full_name_validators)
    email = fields.Email(required = True, validate = email_validators)
    phone_number = fields.Str(required = True, validate = phone_validators)

    @pre_load
    def normalize_organiser(self, data, **kwargs):
        """Normalize input data before validation and loading."""
        if isinstance(data, dict):
            name = data.get('full_name')
            if isinstance(name, str):
                data['full_name'] = name.strip().title()
            email = data.get('email')
            if isinstance(email, str):
                data['email'] = email.strip().lower()
            phone = data.get('phone_number')
            if isinstance(phone, str):
                data['phone_number'] = phone.strip()
        return data
    
    @post_load
    def check_uniqueness(self, data, **kwargs):
        if 'email' in data and data['email']:
            query = db.session.query(Organiser).filter_by(email = data['email'])
            if getattr(self, 'instance', None):
                query = query.filter(Organiser.organiser_id != self.instance.organiser_id)
            if query.first():
                raise ValidationError({"email": ["Email already exists."]})

        if 'phone_number' in data and data['phone_number']:
            query = db.session.query(Organiser).filter_by(phone_number = data['phone_number'])
            if getattr(self, 'instance', None):
                query = query.filter(Organiser.organiser_id != self.instance.organiser_id)
            if query.first():
                raise ValidationError({"phone_number": ["Phone number already exists."]})
        return data

organiser_schema = OrganiserSchema()
organisers_schema = OrganiserSchema(many = True)