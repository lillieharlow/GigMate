from init import db
from sqlalchemy import CheckConstraint
from utils.constraints import VENUE_NAME_MAX


class Venue(db.Model):
    __tablename__ = "venues"
    """Model for venues.
    Attributes:
        venue_id (int): Primary key.
        name (str): Name of the venue.
        location (str): Location of the venue.
        capacity (int): Capacity of the venue.
        shows (list): List of shows associated with the venue.
    """
    __table_args__ = (
        CheckConstraint("capacity >= 1", name='check_capacity_positive'),
    )

    venue_id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String(VENUE_NAME_MAX), nullable = False, unique = True)
    location = db.Column(db.String(100), nullable = False)
    capacity = db.Column(db.Integer, nullable = False)

    """Relationship: one venue can host many shows.
    Delete behaviour: if a venue is deleted, the shows remain. Placeholder attributes are added via 'add_venue_fallback' in schema.py"""
    shows = db.relationship("Show", back_populates = "venue")