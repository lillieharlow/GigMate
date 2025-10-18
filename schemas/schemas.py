"""Marshmallow schemas for GigMate API models.

Provides serialization, deserialization, validation, and normalization
for TicketHolder, Organiser, Venue, Event, Show, and Booking models.

Includes:
- Field validations (regex, length, range, enums)
- Pre-load normalization (trimming, lowercasing, proper case)
- Post-dump transformations (enum serialization, placeholders)
- Nested relationships for related models
"""

from marshmallow_sqlalchemy import SQLAlchemyAutoSchema, auto_field
from marshmallow import fields, pre_load, post_dump, post_load, validate, validates_schema, ValidationError
from sqlalchemy import Date, cast

from init import db
from models.ticket_holder import TicketHolder
from models.organiser import Organiser
from models.venue import Venue
from models.event import Event
from models.show import Show
from models.booking import Booking
from utils.validators import email_validators, phone_validators, first_name_validators, last_name_validators, full_name_validators, venue_name_validators, venue_location_validators, seat_number_regex, seat_number_validation_error
from utils.constraints import DATE_DISPLAY_FORMAT, DATETIME_DISPLAY_FORMAT

# ========== TICKET HOLDER SCHEMA ==========
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

# ========== ORGANISER SCHEMA ==========
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

# ========== VENUE SCHEMA ==========
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

# ========== EVENT SCHEMA ==========
class EventSchema(SQLAlchemyAutoSchema):
    """Schema for Event model with nested shows/organiser and field validations.

    Attributes:
        event_id (int)
        title (str)
        description (str)
        duration_hours (float)
        shows (list[Show]): Nested shows for display (only show_id, date_time, venue.name and venue.location).
        organiser_id (int optional): ID of the organiser.
        organiser (dict, dump_only): Nested organiser to display full_name only.

    Validations:
        - organiser_id must be positive if provided
        - Title length (3-100 characters)
        - Duration hours (1 - 12)

    Pre-load:
        - Trim whitespace from title and description

    Post-load:
        - Ensure combination of title + description is unique in the database
    
    Post-dump:
        - Add placeholder organiser if none assigned ('To Be Determined')
    """
    class Meta:
        model = Event
        load_instance = True
        include_fk = True
        include_relationships = True
        fields = ("event_id", "title", "description", "duration_hours", "shows", "organiser_id", "organiser")
    
    shows = fields.List(fields.Nested("ShowSchema", only = ("show_id", "date_time", "venue")))
    organiser = fields.Nested("OrganiserSchema", dump_only = True, only = ("full_name",))
    
    organiser_id = fields.Integer(allow_none = True, validate = [validate.Range(min = 1, error = "Organiser ID must be a positive number")])
    title = auto_field(required = True, validate = [validate.Length(min = 3, max = 100)])
    description = auto_field()
    duration_hours = fields.Float(required = True, validate = [validate.Range(min = 1, max = 12, error = "Duration must be between 1 and 12 hours")])
    
    @pre_load
    def normalize_event(self, data, **kwargs):
        if isinstance(data, dict):
            title = data.get('title')
            if isinstance(title, str):
                data['title'] = title.strip()
            description = data.get('description')
            if isinstance(description, str):
                data['description'] = description.strip()
        return data

    @post_load
    def check_uniqueness(self, data, **kwargs):
        title = data.get('title')
        description = data.get('description')
        if title and description:
            query = db.session.query(Event).filter_by(title = title, description = description)
            if getattr(self, 'instance', None):
                query = query.filter(Event.event_id != self.instance.event_id)
            if query.first():
                raise ValidationError({"title": ["Event with this title and description already exists."]})
        return data
    
    @post_dump
    def add_organiser_placeholder(self, data, **kwargs):
        if 'organiser' in data and data.get('organiser') is None and data.get('organiser_id') is None:
            data['organiser'] = {'full_name': 'To Be Determined',}
        return data

event_schema = EventSchema()
events_schema = EventSchema(many = True)

# ========== SHOW SCHEMA ==========
class ShowSchema(SQLAlchemyAutoSchema):
    """Schema for Show model with nested event/venue, enum serialization,
    placeholders, FK validation, and field validations.

    Attributes:
        show_id (int)
        date_time (datetime)
        duration_hours (float)
        show_status (str, enum: CONFIRMED, CANCELLED, POSTPONED, RESCHEDULED)
        event_id (int): ID for event
        event (dict, dump-only): Nested event to display title only
        venue_id (int, optional)
        venue (dict, dump-only): Nested venue to display name and location

    Validations:
        - show_status must be a valid enum
        - date_time required and formatted
        - Event ID must refer to an existing ID
        - Only one show per venue per day
        - Event ID and Venue ID positive integers
        - Unique constraint:
            - Each venue can only have one show per day.

    Post-dump:
        - Add placeholder venue if none assigned ('Venue To Be Announced', 'TBA')
        - Convert enum to string
    """
    class Meta:
        model = Show
        load_instance = True
        include_fk = True
        include_relationships = True
        fields = ("show_id", "date_time", "show_status", "event_id", "event", "venue_id", "venue")

    event = fields.Nested("EventSchema", dump_only = True, only = ("title",))
    venue = fields.Nested("VenueSchema", dump_only = True, only = ("name", "location"))

    show_status = fields.Str(required = False, validate = validate.OneOf(['CONFIRMED', 'CANCELLED', 'POSTPONED', 'RESCHEDULED'], error = "Show status must be one of: CONFIRMED, CANCELLED, POSTPONED, RESCHEDULED."))
    date_time = fields.DateTime(required = True, format = DATETIME_DISPLAY_FORMAT)
    event_id = fields.Integer(required = True, validate = validate.Range(min = 1))
    venue_id = fields.Integer(allow_none = True, validate = validate.Range(min = 1))

    @validates_schema
    def validate_unique_per_day_per_venue(self, data, **kwargs):
        venue_id = data.get("venue_id")
        date_time = data.get("date_time")
        if not (venue_id and date_time):
            return
        query = db.session.query(Show).filter(Show.venue_id == venue_id, cast(Show.date_time, Date) == date_time.date())
        if getattr(self, "instance", None) and getattr(self.instance, "show_id", None):
            query = query.filter(Show.show_id != self.instance.show_id)
        if query.first():
            raise ValidationError({"venue_id": [f"Venue already has a show scheduled on {date_time.strftime(DATE_DISPLAY_FORMAT)}."]})

    @post_dump
    def add_venue_placeholder(self, data, **kwargs):
        if 'venue' in data and data.get('venue') is None and data.get('venue_id') is None:
            data['venue'] = {'name': 'Venue To Be Announced', 'location': 'TBA'}
        return data

    @post_dump
    def convert_enum_to_value(self, data, **kwargs):
        if 'show_status' in data:
            if hasattr(data['show_status'], 'value'):
                data['show_status'] = data['show_status'].value
            elif isinstance(data['show_status'], str) and 'ShowStatus.' in data['show_status']:
                data['show_status'] = data['show_status'].split('.')[-1]
        return data

show_schema = ShowSchema()
shows_schema = ShowSchema(many=True)

# ========== BOOKING SCHEMA ==========
class BookingSchema(SQLAlchemyAutoSchema):
    """
    Schema for Booking model with nested ticket_holder/show, enum serialization,
    seat number rules, and field validations.

    Attributes:
        booking_id (int)
        booking_date (date, dump-only)
        booking_status (str, enum: CONFIRMED, CANCELLED, REFUNDED)
        section (str, enum: GENERAL_ADMISSION_STANDING, SEATING)
        seat_number (str, optional): Required for SEATING section
        ticket_holder_id (int): Required
        show_id (int): Required
        ticket_holder (dict, dump-only): Nested ticket_holder info (first_name, last_name)
        show (dict, dump-only): Nested show info (date_time, event)

    Validations:
    - booking_status and section must be valid enum values
    - ticket_holder_id and show_id must be positive integers
    - seat_number:
        - Required when section is SEATING
        - Forbidden when section is GENERAL_ADMISSION_STANDING
        - Must match regex pattern if provided
    - Unique constraints:
        - Ticket holder cannot have multiple bookings for the same show
        - Seat cannot be double-booked for the same show

Post-dump:
    - Converts enum fields (booking_status, section) to plain string values
    """
    class Meta:
        model = Booking
        load_instance = True
        include_fk = True
        fields = ("booking_id", "booking_date", "booking_status", "section", "seat_number", "ticket_holder_id", "show_id", "ticket_holder", "show")
        
    ticket_holder = fields.Nested("TicketHolderSchema", dump_only=True, only=("first_name", "last_name"))
    show = fields.Nested("ShowSchema", dump_only=True, only=("date_time", "event"))

    booking_status = fields.Str(validate = validate.OneOf(['CONFIRMED', 'CANCELLED', 'REFUNDED'], error = "Booking status must be one of: CONFIRMED, CANCELLED, REFUNDED."))
    section = fields.Str(validate = validate.OneOf(['GENERAL_ADMISSION_STANDING', 'SEATING'], error = "Section must be one of: GENERAL_ADMISSION_STANDING, SEATING."))
    seat_number = fields.Str(allow_none=True, validate=[validate.Length(min=1, max=4), validate.Regexp(seat_number_regex, error=seat_number_validation_error)])
    booking_date = fields.Date(format=DATE_DISPLAY_FORMAT, dump_only=True)
    ticket_holder_id = fields.Integer(required=True, validate=[validate.Range(min=1)])
    show_id = fields.Integer(required=True, validate=[validate.Range(min=1)])

    @validates_schema
    def validate_booking(self, data, **kwargs):
        ticket_holder_id = data.get("ticket_holder_id")
        show_id = data.get("show_id")
        seat_number = data.get("seat_number")
        section = data.get("section")
        instance_id = getattr(self, "instance", None) and getattr(self.instance, "booking_id", None)

        if section == "SEATING" and not seat_number:
            raise ValidationError({"seat_number": ["Required when section is SEATING. Format: 1-2 letters followed by 1-2 digits (e.g., 'A1', 'B12', 'AA10')."]})
        if section == "GENERAL_ADMISSION_STANDING" and seat_number:
            raise ValidationError({"seat_number": ["Seat number must not be provided for GENERAL_ADMISSION_STANDING bookings."]})

        if ticket_holder_id and show_id:
            query = db.session.query(Booking).filter_by(ticket_holder_id = ticket_holder_id, show_id = show_id)
            if instance_id:
                query = query.filter(Booking.booking_id != instance_id)
            if query.first():
                raise ValidationError({"ticket_holder_id": ["This ticket holder already has a booking for this show."]})
            
        if seat_number and show_id:
            query = db.session.query(Booking).filter_by(show_id = show_id, seat_number = seat_number)
            if instance_id:
                query = query.filter(Booking.booking_id != instance_id)
            if query.first():
                raise ValidationError({"seat_number": [f"Seat {seat_number} is already booked for this show."]})
            
    @post_dump
    def convert_enum_to_value(self, data, **kwargs):
        for field_name in ('booking_status', 'section'):
            value = data.get(field_name)
            if value:
                if hasattr(value, 'value'):
                    data[field_name] = value.value
                elif isinstance(value, str) and '.' in value:
                    data[field_name] = value.split('.')[-1]
        return data
    
    @pre_load
    def reject_manual_booking_date(self, data, **kwargs):
        if "booking_date" in data:
            raise ValidationError({"booking_date": ["Booking dates are automatic, do not set booking_date manually."]})
        return data
    
booking_schema = BookingSchema()
bookings_schema = BookingSchema(many = True)