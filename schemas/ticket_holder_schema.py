"""Schemas for serializing, deserializing, and validating TicketHolder-related models.

Defines Marshmallow schemas for TicketHolder and related models, including
field validation, normalization, nested relationships, and post-processing.
Used for input validation and output formatting in API endpoints.
"""

from marshmallow_sqlalchemy import SQLAlchemyAutoSchema, auto_field
from marshmallow import fields, pre_load, post_load, ValidationError

from init import db
from models.ticket_holder import TicketHolder
from utils.validators import email_validators, phone_validators, first_name_validators, last_name_validators

class TicketHolderSchema(SQLAlchemyAutoSchema):
    """Schema for TicketHolder model with nested bookings and field validations.

    Attributes:
        ticket_holder_id (int)
        first_name (str)
        last_name (str)
        email (str)
        phone_number (str)
        bookings (list[Booking]): Nested bookings for display, including show date and event title.

    Validations:
        - First and lastname format
        - Email format
        - Phone number format

    Pre-load:
        - Trim whitespace
        - Lowercase email
        - Proper case names
    
    Post-load:
        - Ensure email and phone number are unique in the database
    """
    class Meta:
        model = TicketHolder
        load_instance = True
        include_relationships = True
        fields = ("ticket_holder_id", "first_name", "last_name", "email", "phone_number", "bookings")
    
    bookings = fields.List(fields.Nested("BookingSchema", exclude = ("ticket_holder", "booking_id", "booking_date", "ticket_holder_id", "show_id")))
    
    first_name = auto_field(required = False, validate = first_name_validators)
    last_name = auto_field(required = False, validate = last_name_validators)
    email = fields.Email(required = False, validate = email_validators)
    phone_number = fields.Str(required = False, validate = phone_validators)

    @pre_load
    def normalize_ticket_holder(self, data, **kwargs):
        """Normalize input data before validation and loading."""
        if isinstance(data, dict):
            first = data.get('first_name')
            if isinstance(first, str):
                data['first_name'] = first.strip().title()
            last = data.get('last_name')
            if isinstance(last, str):
                data['last_name'] = last.strip().title()
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
            query = db.session.query(TicketHolder).filter_by(email = data['email'])
            if getattr(self, 'instance', None):
                query = query.filter(TicketHolder.ticket_holder_id != self.instance.ticket_holder_id)
            if query.first():
                raise ValidationError({"email": ["Email already exists."]})

        if 'phone_number' in data and data['phone_number']:
            query = db.session.query(TicketHolder).filter_by(phone_number = data['phone_number'])
            if getattr(self, 'instance', None):
                query = query.filter(TicketHolder.ticket_holder_id != self.instance.ticket_holder_id)
            if query.first():
                raise ValidationError({"phone_number": ["Phone number already exists."]})
        return data

ticket_holder_schema = TicketHolderSchema()
ticket_holders_schema = TicketHolderSchema(many = True)