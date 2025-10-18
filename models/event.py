"""Event model definition.

Contains the Event class which represents events that can have multiple shows,
including constraints for duration and uniqueness of content.
"""

from sqlalchemy import CheckConstraint, UniqueConstraint

from init import db

class Event(db.Model):
    """Model for events.

    Attributes:
        event_id (int): Primary key.
        title (str): Title of the event.
        description (str | None): Description of the event.
        duration_hours (float): Duration of the event in hours (1 - 12).
        organiser_id (int | None): Foreign key to Organiser; nullable.
        organiser (Organiser | None): Relationship to the organiser of this event.
        shows (list[Show]): List of shows associated with the event.

    Constraints:
        - duration_hours must between 1 and 12.
        - Unique combination of title and description to prevent duplicates.

    Relationships and delete behavior:
        - Each event is organised by one organiser (organiser_id set to NULL if
          organiser deleted or not defined and assigns a placeholder 'To Be Determined').
        - Each event can have multiple shows; deleting an event deletes all its shows.
    """
    __tablename__ = "events"
    __table_args__ = (
        CheckConstraint("duration_hours >= 1", name = 'check_duration_min'),
        CheckConstraint("duration_hours <= 12", name = 'check_duration_max'),
        UniqueConstraint('title', 'description', name = 'unique_event_content'),
    )

    event_id = db.Column(db.Integer, primary_key = True)
    title = db.Column(db.String(100), nullable = False)
    description = db.Column(db.Text, nullable = False)
    duration_hours = db.Column(db.Float, nullable = False)
    organiser_id = db.Column(db.Integer, db.ForeignKey("organisers.organiser_id", ondelete = "SET NULL"), nullable = True)
    
    organiser = db.relationship("Organiser", back_populates = "events")
    shows = db.relationship("Show", back_populates = "event", cascade = "all, delete-orphan")