"""Show model definition.

Contains the Show class which represents individual show instances of events,
including constraints for unique show occurrences and future scheduling.
"""

from sqlalchemy import CheckConstraint, UniqueConstraint
from sqlalchemy.types import Enum

from init import db
from utils.constraints import ShowStatus

class Show(db.Model):
    """Model for shows.

    Attributes:
        show_id (int): Primary key.
        date_time (datetime): Date and time of the show; must be in the future.
        show_status (ShowStatus): Status of the show (Confirmed, Cancelled, Postponed, Rescheduled).
        event_id (int): Foreign key to Event.
        venue_id (int | None): Foreign key to Venue; nullable for shows without a fixed venue.
        event (Event): Relationship to the event of this show.
        venue (Venue | None): Relationship to the venue; None if TBD.
        bookings (list[Booking]): List of bookings associated with this show.

    Constraints:
        - Each venue can only have one show per day.
        - Shows must be scheduled in the future.

    Relationships and delete behavior:
        - Each show belongs to exactly one event.
        - Each show may belong to one venue or have venue_id as NULL.
        - A show can have many bookings.
        - Deleting an event deletes all its shows.
        - Deleting a venue sets venue_id to NULL on its shows and a placeholder value is added: 'Venue To Be Announced'.
        - Deleting a show leaves bookings intact (show_id in bookings remains valid and booking_status is updated to CANCELLED).
    """
    __tablename__ = "shows"
    __table_args__ = (
        UniqueConstraint('venue_id', 'date_time', name='unique_show_occurrence'),
        CheckConstraint("date_time > CURRENT_TIMESTAMP", name='check_future_show')
    )

    show_id = db.Column(db.Integer, primary_key = True)
    date_time = db.Column(db.DateTime, nullable = False)
    show_status = db.Column(Enum(ShowStatus), nullable = False, default = ShowStatus.CONFIRMED)
    event_id = db.Column(db.Integer, db.ForeignKey("events.event_id", ondelete = "CASCADE"), nullable = False)
    venue_id = db.Column(db.Integer, db.ForeignKey("venues.venue_id", ondelete = "SET NULL"), nullable = True)
    
    event = db.relationship("Event", back_populates = "shows")
    venue = db.relationship("Venue", back_populates = "shows")
    bookings = db.relationship("Booking", back_populates = "show")