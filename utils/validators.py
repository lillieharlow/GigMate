"""Utility module for reusable Marshmallow validators.

This module centralizes validation logic (regex, length, format checks)
to ensure consistent validation across all schemas in the GigMate API.
"""

from marshmallow import validate
from .constraints import (
    phone_regex, phone_validation_error, 
    email_regex, email_validation_error,
    name_regex, name_validation_error,
    venue_name_regex, venue_name_validation_error,
    venue_location_regex, venue_location_validation_error,
    seat_number_regex, seat_number_validation_error
)

# ========== Email validation (length + regex) ==========
email_validators = [
    validate.Length(min = 5, max = 100, error = "Email must be 5-100 characters"), 
    validate.Regexp(email_regex, error = email_validation_error)
]

# ========== Phone validation (length + regex) ==========
phone_validators = [
    validate.Regexp(phone_regex, error = phone_validation_error)
]

# ========== Name validation (length + regex) ==========
first_name_validators = [
    validate.Length(min = 1, max = 20, error = "First name must be 1-20 characters"), 
    validate.Regexp(name_regex, error = name_validation_error)
]

last_name_validators = [
    validate.Length(min = 1, max = 30, error = "Last name must be 1-30 characters"), 
    validate.Regexp(name_regex, error = name_validation_error)
]

full_name_validators = [
    validate.Length(min = 2, max = 50, error = "Full name must be 2-50 characters"), 
    validate.Regexp(name_regex, error = name_validation_error)
]

# ========== Venue name and location validation ==========
venue_name_validators = [
    validate.Length(min = 2, max = 30, error = "Venue name must be 2-30 characters"),
    validate.Regexp(venue_name_regex, error = venue_name_validation_error)
]

venue_location_validators = [
    validate.Length(min = 10, max = 200, error = "Location must be 10-200 characters"),
    validate.Regexp(venue_location_regex, error = venue_location_validation_error)
]

# ========== Seat number validation ==========
seat_number_validators = [
    validate.Regexp(seat_number_regex, error = seat_number_validation_error)
]