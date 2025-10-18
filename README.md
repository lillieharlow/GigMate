# GigMate

Rock Your Music Events with Ease. GigMate is your backstage pass to managing music tours, venues, organisers, and ticket bookings - all through a powerful RESTful API.

From underground gigs to sold-out stadiums - GigMate keeps your tour in tune, your shows scheduled, and your fans hyped.

Plan. Book. Sell out. Repeat.

Built for developers who want a clean, reliable backend for music events.
<hr>

**Tech Stack:** Python · Flask · PostgreSQL · SQLAlchemy · Marshmallow
<hr>

## Target Audience / User Stories
Who’s GigMate For?

👩‍💻 *Developers:* Building web or mobile apps that need a backend for event management.

🎟️ *Event organisers:* Integrating ticketing and bookings into apps or dashboards.

🚀 *Startups & agencies:* Creating tools for tours, venues, or ticket sales.

*GigMate provides the RESTful endpoints to automate and manage music events programmatically - no messy spreadsheets, no guesswork.*
<hr>

## Table of Contents
* [API Features](#api-features)
* [Setup & Installation](#setup--installation)
   * [Quick Start](#quick-start)
   * [System Requirements](#system-requirements)
   * [Clone Repository](#clone-repository)
   * [Install Dependencies](#install-dependencies)
   * [Set Up PostgreSQL](#set-up-postgresql)
   * [Create User & Grant Permissions](#create-user--grant-permissions)
   * [Create `.env` file](#create-env-file)
   * [Run the API](#run-the-api)
* [Hardware Requirements](#hardware-requirements)
* [Dependencies](#dependencies)
   * [Purpose of Key Dependencies](#purpose-of-key-dependencies)
   * [Legal & Ethical Impacts](#legal--ethical-impacts)
   * [Security Impact](#security-impact)
   * [Conflicts](#conflicts)
* [API Endpoints](#api-endpoints)
   * [Shows](#shows-shows)
   * [Events](#events-events)
   * [Venues](#venues-venues)
   * [Organisers](#organisers-organisers)
   * [Bookings](#bookings-bookings)
   * [Ticket Holders](#ticket-holders-ticket_holders)
   * [Common Response Codes](#common-response-codes)
* [Required Files](required-files)
* [Reference List](reference-list)
<hr>

## API Features

🎶 RESTful endpoints for venues, events, shows, organisers, ticket holders and bookings.

🪩 JSON - simple, predictable data formats for seamless integration.

🧑‍💻 Developer-first design with clean routes, robust validation, and easy scalability.

🚀 Built to perform - lightweight, stateless, and production-ready.

🎛️ Extendable - integrate payments, analytics, or artist profiles without rewriting your encore.
<hr>

## Setup & Installation

GigMate runs on macOS, Linux and Windows (WSL). For development, Python 3.8+ is recommended.

### **Quick Start**
   ```bash
   git clone https://github.com/lillieharlow/GigMate.git
   cd GigMate
   python3 -m venv .venv && source .venv/bin/activate
   pip install -r requirements.txt
   flask run
   ```

### **System Requirements**
   - **Python:** 3.8 or newer
   - **pip:** Python package manager
   - **PostgreSQL:** Installed locally or accessible remotely
   - **VSCode or preferred IDE**
   Tip: Verify Python and pip:

   ```bash
   python3 --version
   pip3 --version
   ```

### **Clone Repository**
   ```bash
   git clone https://github.com/lillieharlow/GigMate.git
   cd GigMate
   ```

### **Install Dependencies**
   Create a virtual environment and activate it:
   ```bash
   python3 -m venv .venv
   # macOS/Linux:
   source .venv/bin/activate
   # Windows CMD:
   .venv\Scripts\activate
   # Windows PowerShell:
   .venv\Scripts\Activate.ps1
   ```
   Then install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

### **Set Up PostgreSQL**
    Open PostgreSQL shell:
    - macOS:
       ```bash
       psql
       ```
    - Linux/WSL:
       ```bash
       sudo -u postgres psql
       ```
    - Windows:
       - Use pgAdmin (GUI) or open the PostgreSQL shell from the Start Menu, or:
       ```bash
       psql -U postgres
       ```
    Create database (if needed):
    ```sql
    CREATE DATABASE database_name;
    \c database_name;
    ```

### Create User & Grant Permissions
   ```sql
   CREATE USER user_name WITH PASSWORD 'password';
   GRANT ALL PRIVILEGES ON DATABASE database_name TO user_name;
   GRANT ALL ON SCHEMA public TO user_name;
   \q
   ```

### Create `.env` file
   Create your own `.env` file and define your DATABASE_URI.
   See `.env.example` DATABASE_URI example:
   ```
   DATABASE_URI=database+driver://username:password@server:port/databasename
   ```

### Run the API
Drop, create, and seed demo data from `controllers/cli_controller.py` with custom CLI commands:
```bash
flask db drop && flask db create && flask db seed
```
Or, if using Flask-Migrate, run:
```bash
flask db upgrade
```
Run the server:
```bash
flask run
```

API available at: **http://127.0.0.1:5000**

<hr>

## Hardware Requirements
- **Minimum:** 1 CPU core, 1 GB RAM, small SSD
- **Recommended:** 2+ CPU cores, 2–4 GB RAM
<hr>

## Dependencies
The full list is in `requirements.txt`. Key packages include:

| Library | Purpose |
|---|---|
| `Flask` | Web framework and CLI |
| `Flask-SQLAlchemy` | DB integration for Flask |
| `SQLAlchemy` | ORM layer used by models |
| `marshmallow` | Serialization & validation |
| `marshmallow-sqlalchemy` | Schema generation for models |
| `python-dotenv` | Load `.env` files for local dev |
| `psycopg2-binary` | Postgres driver (install on your server only) |
| `gunicorn` | Production-grade WSGI server for deploying Flask apps |

Notes:
- `requirements.txt` in this repo was trimmed to top-level packages; transitive dependencies will be installed automatically by pip.
- If you are running tests, you will need to install `pytest` separately (this is not listed on `requirements.txt`).

### Purpose of Key Dependencies
- App wiring: Flask & Flask-SQLAlchemy
- Persistence: SQLAlchemy, database drivers (psycopg2 for Postgres)
- Validation/serialization: Marshmallow + marshmallow-sqlalchemy
- Local convenience: python-dotenv
- Production server: gunicorn
- CLI & signals: click, blinker
- Templating & security: Jinja2, MarkupSafe, itsdangerous

### Legal & Ethical Impacts
- All libraries are open-source with permissive licenses.
- No external analytics, or tracking code is included.
- Developers should verify licenses for commercial use.

### Security Impact
- Environment variables must be used for secrets (DB credentials, API keys).
- Never commit sensitive credentials to version control.
- Test/seed data is included for demos; production databases should enforce TLS/SSL.

### Conflicts
- Use a virtual environment to prevent package conflicts.
- Pin versions in requirements.txt to ensure consistency across environments.
- Avoid mixing global Python packages with the virtual environment.
<hr>

## API Endpoints
All endpoints return JSON.
Full CRUD flexibility, if you don't require all endpoints, remove them.  
Base URL: `http://127.0.0.1:5000/`

### Shows (`/shows`)
| Method | Endpoint              | Description                      |
|--------|----------------------|----------------------------------|
| GET    | `/shows/`            | Get all shows                    |
| GET    | `/shows/<id>`        | Get one show by ID               |
| POST   | `/shows/`            | Create a new show                |
| PATCH/PUT  | `/shows/<id>`        | Update a show by ID    |
| DELETE | `/shows/<id>`        | Cancel a show by ID (cancels all bookings but retains historical show data.) |

### Events (`/events`)
| Method | Endpoint              | Description                      |
|--------|----------------------|----------------------------------|
| GET    | `/events/`           | Get all events                   |
| GET    | `/events/<id>`       | Get one event by ID              |
| POST   | `/events/`           | Create a new event               |
| PATCH/PUT  | `/events/<id>`       | Update an event by ID (partial or full update) |
| DELETE | `/events/<id>`       | Cancel an event by ID (cancels all bookings but retains historical show data.) |

### Venues (`/venues`)
| Method | Endpoint              | Description                      |
|--------|----------------------|----------------------------------|
| GET    | `/venues/`           | Get all venues                   |
| GET    | `/venues/<id>`       | Get one venue by ID              |
| POST   | `/venues/`           | Create a new venue               |
| PATCH/PUT  | `/venues/<id>`       | Update a venue by ID (partial or full update)  |
| DELETE | `/venues/<id>`       | Delete a venue by ID             |

### Organisers (`/organisers`)
| Method | Endpoint              | Description                      |
|--------|----------------------|----------------------------------|
| GET    | `/organisers/`       | Get all organisers               |
| GET    | `/organisers/<id>`   | Get one organiser by ID          |
| POST   | `/organisers/`       | Create a new organiser           |
| PATCH/PUT  | `/organisers/<id>`   | Update an organiser by ID (partial or full update)     |
| DELETE | `/organisers/<id>`   | Delete an organiser by ID        |

### Bookings (`/bookings`)
| Method | Endpoint              | Description                      |
|--------|----------------------|----------------------------------|
| GET    | `/bookings/`         | Get all bookings (supports pagination)                  |
| GET    | `/bookings/<id>`     | Get one booking by ID            |
| POST   | `/bookings/`         | Create a new booking             |
| PATCH/PUT  | `/bookings/<id>`     | Update a booking by ID (partial or full update) |
| DELETE | `/bookings/<id>`     | Delete a booking by ID           |

#### Pagination Parameters
`GET /bookings/` supports pagination using query parameters:

| Parameter | Type | Default | Description |
|------------|------|----------|-------------|
| `page`     | int  | 1        | Page number to retrieve |
| `per_page` | int  | 10       | Number of records per page |

**Example:**
```bash
GET /bookings?page=2
```

### Ticket Holders (`/ticket_holders`)
| Method | Endpoint                    | Description                          |
|--------|-----------------------------|--------------------------------------|
| GET    | `/ticket_holders/`          | Get all ticket holders               |
| GET    | `/ticket_holders/<id>`      | Get one ticket holder by ID          |
| POST   | `/ticket_holders/`          | Create a new ticket holder           |
| PATCH/PUT  | `/ticket_holders/<id>`      | Update a ticket holder by ID (partial or full update)     |
| DELETE | `/ticket_holders/<id>`      | Delete a ticket holder by ID         |

#### Common Response Codes
- `200 OK` — Successful operation
- `201 Created` — Resource successfully created
- `400 Bad Request` — Validation error
- `404 Not Found` — Resource not found

## Required Files

These are the only files/folders you need to run the API locally:

- `main.py` — application factory (create_app)
- `init.py` — Flask + SQLAlchemy init (defines the `db` object)
- `requirements.txt` — runtime dependencies to install in a `.venv`
- `.env` - environment variables, set `DATABASE_URI`
- `.flaskenv` - Flask CLI configuration
- `controllers/` — all route blueprints (ticket holder, organiser, venue, event, show, booking)
- `models/` — SQLAlchemy model classes
- `schemas/` — Marshmallow schemas for validation/serialization
- `utils/` — helper functions (error handlers, constraints)

Optional:
- `controllers/cli_controller.py` — seeds and helper DB commands

<hr>

## Reference List

Guest Manager. (n.d.) *Build your own ticketing platform*, https://www.guestmanager.com/tour/integrations/api, accessed: 28 September 2025.

Leapcell. (2025) *Mastering RESTful API Design: A Practical Guide*, https://leapcell.substack.com/p/mastering-restful-api-design-a-practical?utm_campaign=post&utm_medium=web, accessed: on 1 October 2025.

Marshmallow. (n.d.) *Marshmallow*, https://marshmallow.readthedocs.io/en/stable/index.html, accessed: 9 October 2025.

Paudel, A. (2025) *2025-JUN-flask-lms*, https://github.com/APaud3l/2025-JUN-flask-lms, accessed: 12 October 2025.

Pretty Printed. (2023) *Getting Started With Testing in Flask*, https://www.youtube.com/watch?v=RLKW7ZMJOf4, accessed: 1 October 2025.

Square Developer. (2022) *Sandbox 101: Bookings API Example App* https://www.youtube.com/watch?v=vTfDarZlNiU, accessed: 1 October 2025.