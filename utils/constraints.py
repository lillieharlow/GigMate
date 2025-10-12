"""Utility module for common constraints and validation patterns to be used across models and schemas.
Maintains consistency, reusability, maintainability and scalability."""

# Phone regex for phone number validation
phone_regex = r'^\+?[0-9]{10,15}$'
phone_validation_error = "Phone number must contain 10-15 digits, area code '+' accepted."

# Email regex for email validation
email_regex = r'^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$'
email_validation_error = "Invalid email format. Expected name@domain.com"

# Name regex for validation - letters, spaces, hyphens, apostrophes only (no numbers or just whitespace)
name_regex = r"^[A-Za-z]([A-Za-z\s\-'\.]*[A-Za-z])?$"
name_validation_error = "Name only accepts letters, spaces, hyphens, and apostrophes. Can't be just whitespace or contain any numbers."

# Address regex for Google Maps style validation - optional street number, location name, suburb, state, postcode
address_regex = r"^([0-9]+[A-Za-z]?\s+)?[A-Za-z\s\-'\.]+,\s*[A-Za-z\s\-'\.]+\s+[A-Z]{2,3}\s+[0-9]{4}$"
address_validation_error = "Address must follow Google Maps style: 'Number (optional) Location Name, Suburb/City STATE POSTCODE'"

# DateTime format constants for consistent display
DATETIME_DISPLAY_FORMAT = "%d-%m-%Y | %I:%M %p"  # e.g., "15-10-2025 | 08:30 PM"
DATE_DISPLAY_FORMAT = "%d-%m-%Y"  # e.g., "15-10-2025"