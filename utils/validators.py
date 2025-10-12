"""Utility module for reusable Marshmallow validators.
Provides pre-built validator lists for consistent validation across all schemas."""

from marshmallow import validate
from .constraints import (
    phone_regex, phone_validation_error, 
    email_regex, email_validation_error,
    name_regex, name_validation_error,
    venue_title_regex, venue_title_validation_error,
    venue_location_regex, venue_location_validation_error
)

# Email validation (length + regex)
email_validators = [
    validate.Length(max = 100), 
    validate.Regexp(email_regex, error = email_validation_error)
]

# Phone validation (length + regex)
phone_validators = [
    validate.Length(max = 15), 
    validate.Regexp(phone_regex, error = phone_validation_error)
]

# Name validation (length + regex)
first_name_validators = [
    validate.Length(max = 20), 
    validate.Regexp(name_regex, error = name_validation_error)
]

last_name_validators = [
    validate.Length(max = 30), 
    validate.Regexp(name_regex, error = name_validation_error)
]

full_name_validators = [
    validate.Length(max = 50), 
    validate.Regexp(name_regex, error = name_validation_error)
]

# Venue title and location validation
venue_title_validators = [
    validate.Length(max = 30),
    validate.Regexp(venue_title_regex, error = venue_title_validation_error)
]

venue_location_validators = [
    validate.Length(max = 200),
    validate.Regexp(venue_location_regex, error = venue_location_validation_error)
]