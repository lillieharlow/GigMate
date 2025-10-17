"""Database custom CLI commands for creating, dropping, and seeding tables.
Provides:
    - `flask db drop`: Drop all database tables.
    - `flask db create`: Create all database tables.
    - `flask db seed`: Populate tables with initial sample data.

Note:
    - Foreign key dependencies are respected: TicketHolders → Organisers → Venues → Events → Shows → Bookings.
"""

from flask import Blueprint
from datetime import datetime

from init import db
from models.ticket_holder import TicketHolder
from models.organiser import Organiser
from models.venue import Venue
from models.event import Event
from models.show import Show
from models.booking import Booking, BookingStatus, Section
from utils.constraints import DATETIME_DISPLAY_FORMAT

db_commands = Blueprint("db", __name__)

# ======== CLI COMMANDS ========
@db_commands.cli.command("drop")
def drop_tables():
    """Drop all database tables."""
    db.drop_all()
    print("Tables dropped.")

@db_commands.cli.command("create")
def create_tables():
    """Create all database tables."""
    db.create_all()
    print("Tables created.")

@db_commands.cli.command("seed")
def seed_tables():
    """Seed database tables."""
    # ========== SEED TICKET HOLDERS ==========
    ticket_holders = [TicketHolder(
        first_name = "Bobby",
        last_name = "Mac Manus",
        email = "bobby@email.com",
        phone_number = "+64424111222"
    ), TicketHolder(
        first_name = "Susie",
        last_name = "Tinsdale",
        email = "susie@email.com",
        phone_number = "+64232666777"
    ), TicketHolder(
        first_name = "Josie",
        last_name = "Roberts",
        email = "josie@email.com",
        phone_number = "+64232444333"
    ), TicketHolder(
        first_name = "Lottie",
        last_name = "Timins",
        email = "lottie@email.com",
        phone_number = "+64424555688"
    )]

    db.session.add_all(ticket_holders)
    db.session.commit()

    # ========== SEED ORGANISERS ==========
    organisers = [Organiser(
        full_name = "Johnnie Marks",
        email = "johnnie@email.com",
        phone_number = "0232333456"
    ), Organiser(
        full_name = "Georgia Pierce-allen",
        email = "georgia@email.com",
        phone_number = "0888976543"
    )]

    db.session.add_all(organisers)
    db.session.commit()

    # ========== SEED VENUES ==========
    venues = [Venue(
        name = "Rod Laver Arena",
        location = "200 Batman Ave, Melbourne VIC 3004",
        capacity = 15000
    ), Venue(
        name = "Hordern Pavilion",
        location = "1 Driver Ave, Moore Park NSW 2021",
        capacity = 5000
    )]

    db.session.add_all(venues)
    db.session.commit()

    # ========== SEED EVENTS ==========
    events = [Event(
        title = "Linkin Park: From Zero World Tour",
        description = """The band will perform both new hits like “The Emptiness Machine” and “Heavy Is The Crown” alongside iconic anthems spanning their 20+ year career. Following the release of “Heavy Is The Crown”, the official League of Legends World Championship Anthem and their first collaboration with Riot Games, Linkin Park reasserted their position as one of rock’s defining voices. The song’s hard-hitting rhythm and anthemic energy embody the bold, renewed spirit of the band, resonating with fans across the globe and paving the way for From Zero.

Linkin Park made their triumphant return to the spotlight with "The Emptiness Machine," which surged to #1 on both the Billboard Alternative and Mainstream Rock Airplay charts, marking their 13th and 11th chart-toppers on these lists, respectively. The song also debuted at #4 on the UK Singles Chart, achieving the band’s highest UK chart position in their 24-year career.

With over 54 million monthly listeners on Spotify and accolades from Billboard, The New York Times, and The Los Angeles Times on their recent singles, Linkin Park’s comeback has proven they are more influential than ever. Their timeless appeal, and their latest music has struck a powerful chord, propelling them to the forefront of rock music once again.""",
        duration_hours = 2.25,
        organiser_id = organisers[0].organiser_id
    ), Event(
        title = "Halsey: For My Last Trick",
        description = """Diamond-certified and GRAMMY®Award-nominated artist Halsey continues the celebration for the 10th anniversary of her triple platinum certified full-length debut album, BADLANDS, with the announcement of her Back to Badlands Tour

The new tour announce arrives on the heels of Halsey wrapping her “FOR MY LAST TRICK,” tour, which was the best selling tour of her career, with Variety branding the tour as “one of the most ambitious pop tours of the year.”

When BADLANDS was first released on August 28, 2015, it catapulted Halsey into music history. Since its release the album has sold over 3 Million albums-adjusted in the US, and has accumulated over 9 Billion on-demand streams worldwide. It is one of the only albums in music history to have every song, RIAA certified gold, platinum or multi-platinum. As well as multiple certifications in other countries including the UK, and Australia.""",
        duration_hours = 2.5,
        organiser_id = organisers[1].organiser_id
    )]

    db.session.add_all(events)
    db.session.commit()

    # ========== SEED SHOWS ==========
    shows = [Show(
        date_time = datetime.strptime("8-3-2026 | 7:00 PM", DATETIME_DISPLAY_FORMAT),
        event_id = events[0].event_id,
        venue_id = venues[0].venue_id
    ), Show(
        date_time = datetime.strptime("9-3-2026 | 7:00 PM", DATETIME_DISPLAY_FORMAT),
        event_id = events[0].event_id,
        venue_id = venues[0].venue_id
    ), Show(
        date_time = datetime.strptime("11-3-2026 | 7:00 PM", DATETIME_DISPLAY_FORMAT),
        event_id = events[0].event_id,
        venue_id = venues[1].venue_id
    ), Show(
        date_time = datetime.strptime("13-2-2026 | 7:00 PM", DATETIME_DISPLAY_FORMAT),
        event_id = events[1].event_id,
        venue_id = venues[1].venue_id
    ), Show(
        date_time = datetime.strptime("14-2-2026 | 7:00 PM", DATETIME_DISPLAY_FORMAT),
        event_id = events[1].event_id,
        venue_id = venues[1].venue_id
    )]

    db.session.add_all(shows)
    db.session.commit()

    # ========== SEED BOOKINGS ==========
    bookings = [Booking(
        booking_status = BookingStatus.CONFIRMED,
        section = Section.GENERAL_ADMISSION_STANDING,
        seat_number = None,
        ticket_holder_id = ticket_holders[0].ticket_holder_id,
        show_id = shows[4].show_id
    ), Booking(
        booking_status = BookingStatus.CONFIRMED,
        section = Section.SEATING,
        seat_number = "A32",
        ticket_holder_id = ticket_holders[1].ticket_holder_id,
        show_id = shows[3].show_id
    ), Booking(
        booking_status = BookingStatus.CONFIRMED,
        section = Section.SEATING,
        seat_number = "G12",
        ticket_holder_id = ticket_holders[3].ticket_holder_id,
        show_id = shows[1].show_id
    ), Booking(
        booking_status = BookingStatus.CONFIRMED,
        section = Section.GENERAL_ADMISSION_STANDING,
        seat_number = None,
        ticket_holder_id = ticket_holders[2].ticket_holder_id,
        show_id = shows[2].show_id
    )]

    db.session.add_all(bookings)
    db.session.commit()

    print("Tables seeded.")