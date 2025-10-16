import re

from marshmallow_sqlalchemy import SQLAlchemyAutoSchema, auto_field
from marshmallow import fields, pre_load, post_dump, validate, ValidationError, validates

from models.ticket_holder import TicketHolder
from models.organiser import Organiser
from models.venue import Venue
from models.event import Event
from models.show import Show
from models.booking import Booking
from utils.validators import email_validators, phone_validators, first_name_validators, last_name_validators, full_name_validators, venue_title_validators, venue_location_validators
from utils.constraints import DATE_DISPLAY_FORMAT, DATETIME_DISPLAY_FORMAT, DATETIME_VALIDATION_ERROR, BookingStatus, Section, ShowStatus

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

# ========== Venue Schema ==========
class VenueSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = Venue
        load_instance = True
        include_relationships = True
        fields = ("venue_id", "name", "location", "capacity", "shows")
    
    shows = fields.List(fields.Nested("ShowSchema", only = ("show_id", "date_time", "event")))

    name = auto_field(required = True, validate = venue_title_validators)
    location = auto_field(required = True, validate = venue_location_validators)
    capacity = fields.Integer(required = True, validate = [
        validate.Range(min = 1, max = 200000, error = "Capacity must be a number between 1 and 200,000")
    ])
    
    @pre_load
    def normalize_venue(self, data, **kwargs):
        if isinstance(data, dict):
            name = data.get('name')
            if isinstance(name, str):
                data['name'] = name.strip().title()  # Proper case for venue names
            location = data.get('location')
            if isinstance(location, str):
                data['location'] = location.strip()
        return data

venue_schema = VenueSchema()
venues_schema = VenueSchema(many = True)

# ========== Event Schema ==========
class EventSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = Event
        load_instance = True
        include_fk = True
        include_relationships = True
        fields = ("event_id", "title", "description", "duration_hours", "shows", "organiser")
    
    shows = fields.List(fields.Nested("ShowSchema", only = ("show_id", "date_time", "venue")))
    organiser = fields.Nested("OrganiserSchema", dump_only = True, only = ("organiser_id",))
    
    organiser_id = fields.Integer(allow_none = True, validate = [
        validate.Range(min = 1, error = "Organiser ID must be a positive number")
    ])
    title = auto_field(required = True, validate = [validate.Length(min = 3, max = 100)])
    description = auto_field()
    duration_hours = fields.Float(required = True, validate = [
        validate.Range(min = 0.1, max = 12, error = "Duration must be between 0.1 and 12 hours")
    ])
    
    @pre_load
    def normalize_event(self, data, **kwargs):
        if isinstance(data, dict):
            title = data.get('title')
            if isinstance(title, str):
                data['title'] = title.strip()
        return data

event_schema = EventSchema()
events_schema = EventSchema(many = True)

# ========== Show Schema ==========
class ShowSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = Show
        load_instance = True
        include_fk = True
        include_relationships = True
        fields = ("show_id", "date_time", "show_status", "event_id", "event", "venue_id", "venue")
    
    event = fields.Nested("EventSchema", dump_only = True, only = ("title",))
    venue = fields.Nested("VenueSchema", dump_only = True, only = ("name", "location"))

    # String field with enum validation
    show_status = fields.Str(validate=validate.OneOf(['CONFIRMED', 'CANCELLED', 'POSTPONED', 'RESCHEDULED']))

    @post_dump
    def convert_enum_to_value(self, data, **kwargs):
        """Convert enum objects to their string values"""
        if 'show_status' in data:
            if hasattr(data['show_status'], 'value'):
                data['show_status'] = data['show_status'].value
            elif isinstance(data['show_status'], str) and 'ShowStatus.' in data['show_status']:
                # Handle case where enum is converted to string representation
                data['show_status'] = data['show_status'].split('.')[-1]
        return data

    date_time = fields.DateTime(required = True, format = DATETIME_DISPLAY_FORMAT, error_messages = {
        'invalid': DATETIME_VALIDATION_ERROR
    })
    event_id = fields.Integer(required = True, validate = [
        validate.Range(min = 1, error = "Event ID must be a positive number")
    ])
    venue_id = fields.Integer(allow_none = True, validate = [
        validate.Range(min = 1, error = "Venue ID must be a positive number")
    ])

    @post_dump # If a show has no venue, add placeholder.
    def add_venue_placeholder(self, data, **kwargs):
        # Only add placeholder if venue field is expected but venue_id is actually None in DB
        # AND no venue data was loaded (not just missing from the nested fields)
        if 'venue' in data and data.get('venue') is None and data.get('venue_id') is None:
            data['venue'] = {
                'name': 'Venue To Be Announced',
                'location': 'TBA'
            }
        return data

show_schema = ShowSchema()
shows_schema = ShowSchema(many = True)

# ========== Booking Schema ==========
class BookingSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = Booking
        load_instance = True
        include_fk = True
        fields = ("booking_id", "booking_date", "booking_status", "section", "seat_number", "ticket_holder_id", "show_id", "ticket_holder", "show")
    
    # Simple nested fields for display
    ticket_holder = fields.Nested("TicketHolderSchema", dump_only=True, only=("first_name", "last_name"))
    show = fields.Nested("ShowSchema", dump_only=True, only=("date_time", "event"))

    # Simple string fields with enum validation - no hassle!
    # booking_status and section are validated against allowed values using marshmallow's OneOf validator.
    booking_status = fields.Str(validate=validate.OneOf(['CONFIRMED', 'CANCELLED', 'REFUNDED']))
    section = fields.Str(validate=validate.OneOf(['GENERAL_ADMISSION_STANDING', 'SEATING']))

    @post_dump
    def convert_enum_to_value(self, data, **kwargs):
        """
        Ensure enum fields (booking_status, section) are serialized as plain strings.
        Handle enum objects and string representations to avoid this: 'BookingStatus.CONFIRMED'.
        """
        # Marshmallow doesn’t automatically serialize Python Enums, so convert to string manually.
        if 'booking_status' in data:
            if hasattr(data['booking_status'], 'value'):
                data['booking_status'] = data['booking_status'].value
            elif isinstance(data['booking_status'], str) and 'BookingStatus.' in data['booking_status']:
                data['booking_status'] = data['booking_status'].split('.')[-1]
        if 'section' in data:
            if hasattr(data['section'], 'value'):
                data['section'] = data['section'].value
            elif isinstance(data['section'], str) and 'Section.' in data['section']:
                data['section'] = data['section'].split('.')[-1]
        return data

    # Field validations using marshmallow validators
    booking_date = fields.Date(format=DATE_DISPLAY_FORMAT, dump_only=True)
    ticket_holder_id = fields.Integer(required=True, validate=[validate.Range(min=1)])
    show_id = fields.Integer(required=True, validate=[validate.Range(min=1)])
    seat_number = fields.Str(allow_none=True, validate=[validate.Length(min=1, max=4)])

    @pre_load
    def validate_seating_requirements(self, data, **kwargs):
        """
        Check if seat_number is provided when section is SEATING.
        Prevent bookings for seated sections without a seat_number.
        """
        section = data.get('section')
        seat = data.get('seat_number')
        # Require seat_number when section is SEATING
        if section == 'SEATING' and not seat:
            raise ValidationError({'seat_number': ['Required when section is SEATING']})
        return data
    
booking_schema = BookingSchema()
bookings_schema = BookingSchema(many = True)