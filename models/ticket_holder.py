from init import db
from sqlalchemy import CheckConstraint
from utils.constraints import FIRST_NAME_MAX, LAST_NAME_MAX, EMAIL_MAX, PHONE_MAX

class TicketHolder(db.Model):
    __tablename__ = "ticket_holders"
    """Model for ticket holders.
    Attributes:
        ticket_holder_id (int): Primary key.
        first_name (str): First name of the ticket holder.
        last_name (str): Last name of the ticket holder.
        email (str): Email address of the ticket holder.
        phone_number (str): Phone number of the ticket holder.
        bookings (list): List of bookings associated with the ticket holder.
    """
    __table_args__ = (
        CheckConstraint("length(phone_number) <= 15", name = 'check_phone_number_max_length'),
    )
    ticket_holder_id = db.Column(db.Integer, primary_key = True)
    first_name = db.Column(db.String(FIRST_NAME_MAX), nullable = False)
    last_name = db.Column(db.String(LAST_NAME_MAX), nullable = False)
    email = db.Column(db.String(EMAIL_MAX), nullable = False, unique = True)
    phone_number = db.Column(db.String(PHONE_MAX), nullable = False, unique = True)

    """Relationship: one ticket holder can have many bookings.
    Cascade: if a ticket holder is deleted, all their bookings are also deleted."""
    bookings = db.relationship("Booking", back_populates = "ticket_holder", cascade = "all, delete-orphan")