from init import db
from models.ticket_holder import TicketHolder

# TDD for API endpoints on ticket_holder.py:

# GET /ticket_holders
# Expected response: 404 with message "No ticket holders found."
def test_get_ticket_holders(client):
    response = client.get('/ticket_holders/')
    # When there are no ticket holders, API should return 404 with a friendly message
    assert response.status_code == 404
    data = response.get_json()
    assert data.get('message') == 'No ticket holders found.'

# POST /ticket_holders
# Expected response: 201 OK, JSON response
def test_create_ticket_holder_success(client):
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

# PATCH/PUT /ticket_holders/<ticket_holder_id>
# Expected response: 200 OK, JSON response
def test_update_ticket_holder_success(client):
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