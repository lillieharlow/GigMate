from sqlalchemy import CheckConstraint, DateTime

from init import db
from utils.constraints import DATETIME_DISPLAY_FORMAT

class Show(db.Model):
    __tablename__ = "shows"
    """Model for shows.
    Attributes:
        show_id (int): Primary key.
        date_time (datetime): Date and time of the show.
        event_id (int): Foreign key to the event.
        venue_id (int): Foreign key to the venue.
        event (Event): The event of the show.
        venue (Venue): The venue of the show.
        bookings (list): List of bookings associated with the show."""
    __table_args__ = (
        db.UniqueConstraint('event_id', 'venue_id', 'date_time', name='unique_show_occurrence'), # Prevent duplicate shows
        CheckConstraint("date_time > CURRENT_TIMESTAMP", name='check_future_show'), # Ensure shows are scheduled in the future
    )

    show_id = db.Column(db.Integer, primary_key = True)
    date_time = db.Column(db.DateTime, nullable = False)  # Use DATETIME_DISPLAY_FORMAT for serialization
    event_id = db.Column(db.Integer, db.ForeignKey("events.event_id", ondelete = "CASCADE"), nullable = False)
    venue_id = db.Column(db.Integer, db.ForeignKey("venues.venue_id", ondelete = "RESTRICT"), nullable = False)
    
    """Relationships:
    - one show is one and only one event.
    - one show can be held at one and only one venue.
    - one show can have many bookings.
    Delete behaviour:
    - if an event is deleted, all its shows are also deleted (CASCADE).
    - if a venue is deleted, shows at that venue cannot be deleted (RESTRICT).
    - if a show is deleted, its bookings remain but show_id is set to NULL."""
    event = db.relationship("Event", back_populates = "shows")
    venue = db.relationship("Venue", back_populates = "shows")
    bookings = db.relationship("Booking", back_populates = "show")
