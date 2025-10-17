"""Venue model definition.

Contains the Venue class which represents physical locations where shows take place,
including constraints for capacity, name, and address formatting.
"""

from sqlalchemy import CheckConstraint

from init import db
from utils.constraints import name_regex, venue_location_regex

class Venue(db.Model):
    """Model for venues.

    Attributes:
        venue_id (int): Primary key.
        name (str): Name of the venue; must be unique and match name regex.
        location (str): Full address of the venue (e.g., "11 The Esplanade, St Kilda VIC 3182"); validated via regex.
        capacity (int): Capacity of the venue; must be a positive realistic number.
        shows (list[Show]): List of shows hosted at this venue.

    Constraints:
        - Capacity must be between 1 and 200,000.
        - Name must match the defined name regex.
        - Location must match the defined address regex (Google Maps style).

    Relationships and delete behavior:
        - Each venue can host many shows.
        - Deleting a venue sets venue_id to NULL on associated shows and assigns a placeholder 'Venue To Be Announced'.
    """
    __tablename__ = "venues"
    __table_args__ = (
        CheckConstraint("capacity >= 1", name='check_capacity_positive'),
        CheckConstraint("capacity <= 200000", name='check_capacity_realistic'), # Max realistic venue capacity
        CheckConstraint(f"name ~ '{name_regex}'", name='check_name_format'),
        CheckConstraint(f"location ~ '{venue_location_regex}'", name='check_address_format'), # Validate Google Maps style address
    )

    venue_id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String(30), nullable = False, unique = True)
    location = db.Column(db.String(100), nullable = False)
    capacity = db.Column(db.Integer, nullable = False)

    shows = db.relationship("Show", back_populates = "venue")