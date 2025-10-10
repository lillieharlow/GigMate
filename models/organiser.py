from init import db
from sqlalchemy import CheckConstraint

from utils.constraints import FULL_NAME_MAX, EMAIL_MAX, PHONE_MAX

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
        CheckConstraint("length(phone_number) <= 15", name = 'check_phone_number_max_length'),
    )
    organiser_id = db.Column(db.Integer, primary_key = True)
    full_name = db.Column(db.String(FULL_NAME_MAX), nullable = False)
    email = db.Column(db.String(EMAIL_MAX), nullable = False, unique = True)
    phone_number = db.Column(db.String(PHONE_MAX), nullable = False, unique = True)

    """Relationship: one organiser can organise many events.
    Delete behaviour: if an organiser is deleted, their events remain but organiser_id is set to NULL."""
    events = db.relationship("Event", back_populates = "organiser")