import pytest
from init import db
from models.ticket_holder import TicketHolder
from models.event import Event
from models.show import Show
from models.booking import Booking, BookingStatus, Section


def test_seat_uniqueness_per_show(client):
    # seed minimal objects
    th = TicketHolder(first_name='A', last_name='B', email='a@b.com', phone_number='+11111111111')
    db.session.add(th)
    ev = Event(title='E1', description='d', duration_hours=1.0)
    db.session.add(ev)
    db.session.commit()

    # create two shows
    show1 = Show(date_time='2025-11-01 19:00:00', event_id=ev.event_id)
    show2 = Show(date_time='2025-11-02 19:00:00', event_id=ev.event_id)
    db.session.add_all([show1, show2])
    db.session.commit()

    # booking seat A1 on show1 should succeed
    b1 = Booking(booking_status=BookingStatus.CONFIRMED, section=Section.SEATING, seat_number='A1', ticket_holder_id=th.ticket_holder_id, show_id=show1.show_id)
    db.session.add(b1)
    db.session.commit()

    # booking seat A1 on same show should raise IntegrityError on commit
    b2 = Booking(booking_status=BookingStatus.CONFIRMED, section=Section.SEATING, seat_number='A1', ticket_holder_id=th.ticket_holder_id, show_id=show1.show_id)
    db.session.add(b2)
    with pytest.raises(Exception):
        db.session.commit()
    db.session.rollback()

    # booking seat A1 on different show should succeed
    b3 = Booking(booking_status=BookingStatus.CONFIRMED, section=Section.SEATING, seat_number='A1', ticket_holder_id=th.ticket_holder_id, show_id=show2.show_id)
    db.session.add(b3)
    db.session.commit()

    assert b3.booking_id is not None
