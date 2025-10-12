from sqlalchemy import CheckConstraint

from init import db

class Event(db.Model):
    __tablename__ = "events"
    """Model for events.
    Attributes:
        event_id (int): Primary key.
        title (str): Title of the event.
        description (str): Description of the event.
        duration_hours (float): Duration of the event in hours.
        organiser_id (int): Foreign key to the organiser.
        organiser (Organiser): The organiser of the event.
        shows (list): List of shows associated with the event."""
    __table_args__ = (
        CheckConstraint("duration_hours > 0", name='check_duration_positive'), # Duration must be a positive digit
        CheckConstraint("duration_hours <= 12", name='check_duration_max'),  # Max 12 hours per event
    )

    event_id = db.Column(db.Integer, primary_key = True)
    title = db.Column(db.String(100), nullable = False)
    description = db.Column(db.Text)
    duration_hours = db.Column(db.Float, nullable = False)
    organiser_id = db.Column(db.Integer, db.ForeignKey("organisers.organiser_id", ondelete = "SET NULL"), nullable = True)
    
    """Relationships:
    - one event is organised by one organiser.
    - one event can have many shows (each show has its own date and venue).
    Delete behaviour: 
    - if an organiser is deleted, their events remain but organiser_id is set to NULL.
    - if an event is deleted, all its shows are also deleted."""
    organiser = db.relationship("Organiser", back_populates = "events")
    shows = db.relationship("Show", back_populates = "event", cascade = "all, delete-orphan")