"""Schemas for serializing, deserializing, and validating Show-related data.

Defines Marshmallow schemas for the Show model, including field validation,
normalization, and nested relationships. Used for input validation and output
formatting in API endpoints and data processing.
"""

from marshmallow_sqlalchemy import SQLAlchemyAutoSchema
from marshmallow import fields, post_dump, validate, validates_schema, ValidationError
from sqlalchemy import Date, cast

from init import db
from models.show import Show
from utils.constraints import DATE_DISPLAY_FORMAT, DATETIME_DISPLAY_FORMAT

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