import enum

from sqlalchemy import func
from sqlalchemy.types import Enum

from init import db

# Define set values for booking_status column of booking table.
class BookingStatus(enum.Enum):
    CONFIRMED = "Confirmed"
    CANCELLED = "Cancelled"
    REFUNDED = "Refunded"
    
# Define set values for section column of booking table.
class Section(enum.Enum):
    GENERAL_ADMISSION_STANDING = "General Admission/Standing"
    SEATING = "Seating"
    VIP = "VIP"
    ACCESSIBLE = "Accessible"

class Booking(db.Model):
    __tablename__ = "bookings"
    """Model for bookings.
    Attributes:
        booking_id (int): Primary key.
        booking_date (date): Date of the booking.
        booking_status (BookingStatus): Status of the booking (Confirmed, Cancelled, Refunded).
        section (Section): Section of the venue (General Admission/Standing, Seating, VIP, Accessible).
        seat_number (str): Seat number if applicable (nullable for General Admission).
        ticket_holder_id (int): Foreign key to the ticket holder.
        show_id (int): Foreign key to the show.
        ticket_holder (TicketHolder): The ticket holder of the booking.
        show (Show): The show of the booking."""
    __table_args__ = (
        db.UniqueConstraint("ticket_holder_id", "show_id", name = "booking_unique_ticket_holder_show"),
        db.UniqueConstraint("show_id", "seat_number", name = "unique_seat_per_show"), # Enforce seat uniqueness when seat_number is not null (seated sections)
    )

    booking_id = db.Column(db.Integer, primary_key = True)
    booking_date = db.Column(db.Date, default = func.current_date(), nullable = False)  # Use DATE_DISPLAY_FORMAT for serialization
    booking_status = db.Column(Enum(BookingStatus), nullable = False, default = BookingStatus.CONFIRMED)
    section = db.Column(Enum(Section), nullable = False, default = Section.GENERAL_ADMISSION_STANDING)
    seat_number = db.Column(db.String(4), nullable = True)
    ticket_holder_id = db.Column(db.Integer, db.ForeignKey("ticket_holders.ticket_holder_id", ondelete="RESTRICT"), nullable = False)
    show_id = db.Column(db.Integer, db.ForeignKey("shows.show_id", ondelete="SET NULL"), nullable = True)

    """Relationships:
    - one booking has one and only one ticket_holder.
    - one booking is for one and only one show.
    Delete behaviour:
    - if a ticket_holder is deleted, bookings prevent deletion (RESTRICT) - ticket_holders with active bookings can't be deleted.
    - if a show is deleted, its bookings remain but show_id is set to NULL."""
    ticket_holder = db.relationship("TicketHolder", back_populates = "bookings")
    show = db.relationship("Show", back_populates = "bookings")
