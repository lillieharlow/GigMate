"""Utility module for reusable Marshmallow validators.
Provides pre-built validator lists for consistent validation across all schemas."""

from marshmallow import validate
from .constraints import (
    phone_regex, phone_validation_error, 
    email_regex, email_validation_error,
    name_regex, name_validation_error,
    FIRST_NAME_MAX, LAST_NAME_MAX, EMAIL_MAX, PHONE_MAX, FULL_NAME_MAX,
)

# Email validation (length + regex)
email_validators = [
    validate.Length(max=EMAIL_MAX), 
    validate.Regexp(email_regex, error=email_validation_error)
]

# Phone validation (length + regex)
phone_validators = [
    validate.Length(max=PHONE_MAX), 
    validate.Regexp(phone_regex, error=phone_validation_error)
]

# Name validation (length + regex)
first_name_validators = [
    validate.Length(max=FIRST_NAME_MAX), 
    validate.Regexp(name_regex, error=name_validation_error)
]

last_name_validators = [
    validate.Length(max=LAST_NAME_MAX), 
    validate.Regexp(name_regex, error=name_validation_error)
]

full_name_validators = [
    validate.Length(max=FULL_NAME_MAX), 
    validate.Regexp(name_regex, error=name_validation_error)
]