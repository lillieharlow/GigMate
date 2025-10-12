import re

from marshmallow_sqlalchemy import SQLAlchemyAutoSchema, auto_field
from marshmallow import fields, pre_load

from models.ticket_holder import TicketHolder
from models.organiser import Organiser
from models.venue import Venue
from models.event import Event
from models.show import Show
from models.booking import Booking
from utils.validators import email_validators, phone_validators, first_name_validators, last_name_validators, full_name_validators

# ========== TicketHolder Schema ==========
class TicketHolderSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = TicketHolder
        load_instance = True
        include_relationships = True
        fields = ("ticket_holder_id", "first_name", "last_name", "email", "phone_number", "bookings")
    
    bookings = fields.List(fields.Nested("BookingSchema", exclude = ("ticket_holder", "booking_id", "booking_date", "ticket_holder_id", "show_id")))

    first_name = auto_field(required = True, validate = first_name_validators)
    last_name = auto_field(required = True, validate = last_name_validators)
    email = fields.Email(required = True, validate = email_validators)
    phone_number = fields.Str(required = True, validate = phone_validators)

    @pre_load
    def normalize_ticket_holder(self, data, **kwargs):
        # strip and lowercase email, trim phone whitespace
        if isinstance(data, dict):
            email = data.get('email')
            if isinstance(email, str):
                data['email'] = email.strip().lower()
            phone = data.get('phone_number')
            if isinstance(phone, str):
                data['phone_number'] = phone.strip()
        return data
    
ticket_holder_schema = TicketHolderSchema()
ticket_holders_schema = TicketHolderSchema(many = True)

# ========== Organiser Schema ==========
class OrganiserSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = Organiser
        load_instance = True
        include_relationships = True
        fields = ("organiser_id", "full_name", "email", "phone_number", "events")

    events = fields.List(fields.Nested("EventSchema", only = ("event_id", "title")))

    full_name = auto_field(required=True, validate = full_name_validators)
    email = fields.Email(required=True, validate = email_validators)
    phone_number = fields.Str(required=True, validate = phone_validators)

    @pre_load
    def normalize_organiser(self, data, **kwargs):
        if isinstance(data, dict):
            email = data.get('email')
            if isinstance(email, str):
                data['email'] = email.strip().lower()
            phone = data.get('phone_number')
            if isinstance(phone, str):
                data['phone_number'] = phone.strip()
        return data

organiser_schema = OrganiserSchema()
organisers_schema = OrganiserSchema(many = True)