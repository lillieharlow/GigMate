"""TicketHolder model definition.

Contains the TicketHolder class which represents individuals who purchase tickets,
including constraints for valid names, emails, and phone numbers.
"""

from sqlalchemy import CheckConstraint

from init import db
from utils.constraints import email_regex, phone_regex, name_regex

class TicketHolder(db.Model):
    """Model for ticket holders.

    Attributes:
        ticket_holder_id (int): Primary key.
        first_name (str): First name of the ticket holder.
        last_name (str): Last name of the ticket holder.
        email (str): Email address of the ticket holder; must be unique and match email format.
        phone_number (str): Phone number of the ticket holder; must be unique and match phone format.
        bookings (list[Booking]): List of bookings associated with this ticket holder.

    Constraints:
        - Validates first_name and last_name using regex.
        - Validates email using regex.
        - Validates phone_number using regex.
        - Email and phone_number must be unique.

    Relationships and delete behavior:
        - One ticket holder can have many bookings.
        - Ticket holders cannot be deleted if they have future confirmed bookings.
    """
    __tablename__ = "ticket_holders"
    __table_args__ = (
        CheckConstraint(f"email ~ '{email_regex}'", name = 'check_email_format'),
        CheckConstraint(f"phone_number ~ '{phone_regex}'", name = 'check_phone_format'),
        CheckConstraint(f"first_name ~ '{name_regex}'", name = 'check_first_name_format'),
        CheckConstraint(f"last_name ~ '{name_regex}'", name = 'check_last_name_format'),
    )
    ticket_holder_id = db.Column(db.Integer, primary_key = True)
    first_name = db.Column(db.String(20), nullable = False)
    last_name = db.Column(db.String(30), nullable = False)
    email = db.Column(db.String(100), nullable = False, unique = True)
    phone_number = db.Column(db.String(15), nullable = False, unique = True)

    bookings = db.relationship("Booking", back_populates = "ticket_holder")