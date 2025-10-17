"""Booking model definition.

Contains the Booking class which represents ticket bookings for shows,
including constraints for unique bookings and seat allocations.
"""

from sqlalchemy import func, UniqueConstraint
from sqlalchemy.types import Enum

from init import db
from utils.constraints import BookingStatus, Section

class Booking(db.Model):
    """Model for bookings.
    
    Attributes:
        booking_id (int): Primary key.
        booking_date (date): Date of the booking; defaults to current date.
        booking_status (BookingStatus): Status of the booking (Confirmed, Cancelled, Refunded).
        section (Section): Section of the venue (General Admission Standing, Seating).
        seat_number (str | None): Seat number if applicable; nullable for General Admission.
        ticket_holder_id (int): Foreign key to TicketHolder.
        show_id (int): Foreign key to Show.
        ticket_holder (TicketHolder): Relationship to the ticket holder of this booking.
        show (Show): Relationship to the show of this booking.

    Constraints:
        - Unique combination of ticket_holder_id and show_id (one booking per ticket holder per show).
        - Unique seat_number per show for seated sections.
        
    Relationships and delete behavior:
        - Each booking is linked to one TicketHolder and one Show.
        - Deleting a TicketHolder with existing bookings is restricted.
        - Deleting a Show is restricted (show_id in bookings must remain valid).
    """
    __tablename__ = "bookings"
    __table_args__ = (
        UniqueConstraint("ticket_holder_id", "show_id", name = "booking_unique_ticket_holder_show"),
        UniqueConstraint("show_id", "seat_number", name = "unique_seat_per_show"), # Enforce seat uniqueness when seat_number is not null
    )

    booking_id = db.Column(db.Integer, primary_key = True)
    booking_date = db.Column(db.Date, default = func.current_date(), nullable = False)  # Default to current date
    booking_status = db.Column(Enum(BookingStatus), nullable = False, default = BookingStatus.CONFIRMED)
    section = db.Column(Enum(Section), nullable = False, default = Section.GENERAL_ADMISSION_STANDING)
    seat_number = db.Column(db.String(4), nullable = True)
    ticket_holder_id = db.Column(db.Integer, db.ForeignKey("ticket_holders.ticket_holder_id", ondelete="RESTRICT"), nullable = False)
    show_id = db.Column(db.Integer, db.ForeignKey("shows.show_id", ondelete="RESTRICT"), nullable = False)

    ticket_holder = db.relationship("TicketHolder", back_populates = "bookings")
    show = db.relationship("Show", back_populates = "bookings")