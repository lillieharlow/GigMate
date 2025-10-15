"""Utility module for common constraints and validation patterns to be used across models and schemas.
Maintains consistency, reusability, maintainability and scalability."""

import enum

# Enum definitions
class BookingStatus(enum.Enum):
    CONFIRMED = "Confirmed"
    CANCELLED = "Cancelled"
    REFUNDED = "Refunded"

class ShowStatus(enum.Enum):
    CONFIRMED = "Confirmed"
    CANCELLED = "Cancelled"
    POSTPONED = "Postponed"
    RESCHEDULED = "Rescheduled"

class Section(enum.Enum):
    GENERAL_ADMISSION_STANDING = "General Admission Standing"
    SEATING = "Seating"

# Phone regex for phone number validation
phone_regex = r'^\+?[0-9]{10,15}$'
phone_validation_error = "Phone number must contain 10-15 digits, area code '+' accepted."

# Email regex for email validation
email_regex = r'^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$'
email_validation_error = "Invalid email format. Expected name@domain.com"

# Name regex for validation - letters, spaces, hyphens, apostrophes only (no numbers or just whitespace)
name_regex = r"^[A-Za-z]([A-Za-z\s\-''\.]*[A-Za-z])?$"
name_validation_error = "Name only accepts letters, spaces, hyphens, and apostrophes. Can't be just whitespace or contain any numbers."

# Venue title regex - allows letters, numbers, spaces, hyphens, apostrophes, ampersands
venue_title_regex = r"^[A-Za-z0-9]([A-Za-z0-9\s\-''\.&]*[A-Za-z0-9])?$"
venue_title_validation_error = "Venue title can only contain letters, numbers, spaces, hyphens, apostrophes, and ampersands."

# Venue location regex for Google Maps style validation - optional street number, location name, suburb, state, postcode
venue_location_regex = r"^([0-9]+[A-Za-z]?\s+)?[A-Za-z\s\-''\.]+,\s*[A-Za-z\s\-''\.]+\s+[A-Z]{2,3}\s+[0-9]{4}$"
venue_location_validation_error = "Location must follow Google Maps style exactly: 'Number (optional) Location Name, Suburb/City STATE POSTCODE'"

# DateTime format constants for consistent display
DATETIME_DISPLAY_FORMAT = "%d-%m-%Y | %I:%M %p"  # e.g., "15-10-2025 | 08:30 PM"
DATE_DISPLAY_FORMAT = "%d-%m-%Y"  # e.g., "15-10-2025"
DATETIME_VALIDATION_ERROR = 'Please format Date and time: DD-MM-YYYY | HH:MM AM/PM (e.g., "15-10-2025 | 08:30 PM")'