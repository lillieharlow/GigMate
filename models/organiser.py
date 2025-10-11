from sqlalchemy import CheckConstraint

from init import db
from utils.constraints import FULL_NAME_MAX, EMAIL_MAX, PHONE_MAX, email_regex, phone_regex, name_regex

class Organiser(db.Model):
    __tablename__ = "organisers"
    """Model for organisers.
    Attributes:
        organiser_id (int): Primary key.
        full_name (str): Full name of the organiser.
        email (str): Email address of the organiser.
        phone_number (str): Phone number of the organiser.
        events (list): List of events associated with the organiser.
    """
    __table_args__ = (
        CheckConstraint(f"email ~ '{email_regex}'", name = 'check_email_format'), # Validate email format
        CheckConstraint(f"phone_number ~ '{phone_regex}'", name = 'check_phone_format'), # Validate phone number format  
        CheckConstraint(f"full_name ~ '{name_regex}'", name = 'check_full_name_format'), # Validate full name format
    )
    organiser_id = db.Column(db.Integer, primary_key = True)
    full_name = db.Column(db.String(FULL_NAME_MAX), nullable = False)
    email = db.Column(db.String(EMAIL_MAX), nullable = False, unique = True)
    phone_number = db.Column(db.String(PHONE_MAX), nullable = False, unique = True)

    """Relationship: one organiser can organise many events.
    Delete behaviour: if an organiser is deleted, their events remain but organiser_id is set to NULL."""
    events = db.relationship("Event", back_populates = "organiser", passive_deletes=True)