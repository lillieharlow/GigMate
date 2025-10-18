"""
Schemas for serializing, deserializing, and validating Event-related data.

Defines Marshmallow schemas for the Event model, including field validation,
normalization, and nested relationships. Used for input validation and output
formatting in API endpoints and data processing.
"""

from marshmallow_sqlalchemy import SQLAlchemyAutoSchema, auto_field
from marshmallow import fields, pre_load, post_dump, post_load, validate, ValidationError

from init import db
from models.event import Event

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