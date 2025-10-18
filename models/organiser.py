"""Organiser model definition.

Contains the Organiser class which represents organisers who create and manage events,
including constraints for email, phone, and name formats.
"""

from sqlalchemy import CheckConstraint

from init import db
from utils.constraints import email_regex, phone_regex, name_regex

class Organiser(db.Model):
    """Model for organisers.

    Attributes:
        organiser_id (int): Primary key.
        full_name (str): Full name of the organiser.
        email (str): Email address of the organiser; must be unique and match email_regex.
        phone_number (str): Phone number of the organiser; must be unique and match phone_regex.
        events (list[Event]): List of events organised by this organiser.

    Constraints:
        - full_name must match name_regex.
        - email must match email_regex.
        - phone_number must match phone_regex.
        - email and phone_number must be unique.

    Relationships and delete behavior:
        - One organiser can organise many events.
        - Deleting an organiser sets organiser_id to NULL on their events.
    """
    __tablename__ = "organisers"
    
    organiser_id = db.Column(db.Integer, primary_key = True)
    full_name = db.Column(db.String(50), nullable = False)
    email = db.Column(db.String(100), nullable = False, unique = True)
    phone_number = db.Column(db.String(15), nullable = False, unique = True)

    __table_args__ = (
        CheckConstraint(f"full_name ~ '{name_regex}'", name = 'check_full_name_format'),
        CheckConstraint(f"email ~ '{email_regex}'", name = 'check_email_format'),
        CheckConstraint(f"phone_number ~ '{phone_regex}'", name = 'check_phone_format')
    )

    events = db.relationship("Event", back_populates = "organiser", passive_deletes=True)