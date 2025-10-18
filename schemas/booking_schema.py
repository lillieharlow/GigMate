"""Schemas for serializing, deserializing, and validating Booking-related data.

Defines Marshmallow schemas for the Booking model, including field validation,
normalization, and nested relationships. Used for input validation and output
formatting in API endpoints and data processing.
"""

from marshmallow_sqlalchemy import SQLAlchemyAutoSchema
from marshmallow import fields, pre_load, post_dump, validate, validates_schema, ValidationError

from init import db
from models.booking import Booking
from utils.validators import seat_number_regex, seat_number_validation_error
from utils.constraints import DATE_DISPLAY_FORMAT

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