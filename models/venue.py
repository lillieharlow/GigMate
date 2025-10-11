from sqlalchemy import CheckConstraint

from init import db
from utils.constraints import VENUE_NAME_MAX, VENUE_LOCATION_MAX, name_regex, address_regex


class Venue(db.Model):
    __tablename__ = "venues"
    """Model for venues.
    Attributes:
        venue_id (int): Primary key.
        name (str): Name of the venue.
        location (str): Full address of the venue (e.g., "11 The Esplanade, St Kilda VIC 3182").
        capacity (int): Capacity of the venue.
        shows (list): List of shows associated with the venue.
    """
    __table_args__ = (
        CheckConstraint("capacity >= 1", name='check_capacity_positive'),
        CheckConstraint("capacity <= 200000", name='check_capacity_realistic'), # Max realistic venue capacity
        CheckConstraint(f"name ~ '{name_regex}'", name='check_name_format'), # Validate venue name format
        CheckConstraint(f"location ~ '{address_regex}'", name='check_address_format'), # Validate Google Maps style address
    )

    venue_id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String(VENUE_NAME_MAX), nullable = False, unique = True)
    location = db.Column(db.String(VENUE_LOCATION_MAX), nullable = False)
    capacity = db.Column(db.Integer, nullable = False)

    """Relationship: one venue can host many shows.
    Delete behaviour: venues with scheduled shows cannot be deleted (RESTRICT)."""
    shows = db.relationship("Show", back_populates = "venue")