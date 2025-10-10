"""Utility module for common constraints and validation patterns to be used across models and schemas.
Maintains consistency, reusability, maintainability and scalability."""

# Phone regex for phone number validation
phone_regex = r'^\+?[0-9]{10,15}$'
phone_validation_error = "Phone number must contain 10-15 digits, area code '+' accepted."

# Email regex for email validation
email_regex = r'^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$'
email_validation_error = "Invalid email format. Expected name@domain.tld"

# Common string lengths used across models/schemas
FIRST_NAME_MAX = 20
LAST_NAME_MAX = 30
EMAIL_MAX = 100
PHONE_MAX = 15
FULL_NAME_MAX = 50
VENUE_NAME_MAX = 30
SEAT_MAX = 4
EVENT_TITLE_MAX = 100