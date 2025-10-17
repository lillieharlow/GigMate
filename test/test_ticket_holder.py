"""
Unit tests for the Ticket Holder API endpoints in GigMate.

Tests basic CRUD operations on the /ticket_holders endpoint using the Flask test client.
Ensures correct HTTP status codes, JSON responses, and database updates.
"""

from init import db
from models.ticket_holder import TicketHolder

def test_get_ticket_holders(client):
    """GET /ticket_holders
    Test retrieving all ticket holders when the database is empty.
    Return: 404 with a friendly message.
    """
    response = client.get('/ticket_holders/')
    assert response.status_code == 404
    data = response.get_json()
    assert data.get('message') == 'No ticket holders found.'

def test_create_ticket_holder_success(client):
    """POST /ticket_holders
    Test creating a new ticket holder with valid data.
    Return: 201 with the created ticket holder's data.
    """
    new_ticket_holder = {
        "first_name": "John",
        "last_name": "Smith",
        "email": "john@email.com",
        "phone_number": "0324555444"
    }
    response = client.post('/ticket_holders/', json = new_ticket_holder)
    assert response.status_code == 201
    ticket_holder = response.get_json()
    assert 'ticket_holder_id' in ticket_holder
    assert ticket_holder['email'] == 'john@email.com'

def test_update_ticket_holder_success(client):
    """PATCH/PUT /ticket_holders/<ticket_holder_id>
    Test updating an existing ticket holder's first name.
    Return: 200 with the updated ticket holder's data.
    """
    ticket_holder = TicketHolder(
        first_name = "Test",
        last_name = "TicketHolder",
        email = "test@mail.com",
        phone_number = "0123456789"
    )
    db.session.add(ticket_holder)
    db.session.commit()
    ticket_holder_id = ticket_holder.ticket_holder_id

    update_data = {"first_name": "Passed"}
    response = client.patch(f"/ticket_holders/{ticket_holder_id}", json = update_data)
    assert response.status_code == 200
    updated_ticket_holder = response.get_json()
    assert updated_ticket_holder["first_name"] == "Passed"