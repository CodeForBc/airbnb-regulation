# Airbnb Listings Harvester API

A Django API service that harvests Airbnb listings data using Scrapy. 
## Prerequisites

- Python 3.x
- Poetry for dependency management
- Docker and Docker Compose (for database)

## Setup

### 1. Environment Configuration

Create a `.env` file in the `airbnb_project` folder with the following variables:

```env
SECRET_KEY=your_secret_key
DJANGO_DEBUG=True
AIRBNB_PUBLIC_API_KEY=d306zoyjsyarp7ifhu67rjxn52tv0t20
POSTGRES_PASSWORD=your_password
POSTGRES_USER=your_username
POSTGRES_DB=your_db_name
POSTGRES_HOST_PORT=5432
```

### 2. Database Setup

Start the PostgreSQL database using Docker:

```bash
docker-compose up -d
```

### 3. Database Migrations

Run the following commands to set up the database schema:

```bash
python manage.py makemigrations listings
python manage.py migrate listings
```

### 4. Dependencies Installation

Install required dependencies using Poetry:

```bash
poetry install
```

## Running the Application

Start the Django development server:

```bash
python manage.py runserver
```

The server will be available at `http://127.0.0.1:8000/`.

## API Documentation

### Harvest Listings Endpoint

Triggers the Airbnb listings harvesting process.

- **URL**: `/listings/harvest-listings/`
- **Method**: `GET`
- **Success Response**:
  - **Code**: 200
  - **Content**: Harvesting process started successfully
- **Error Responses**:
  - **Code**: 409
    - **Content**: A harvesting process is already running
  - **Code**: 500
    - **Content**: Internal server error during harvest initiation

Example usage with curl:
```bash
curl http://127.0.0.1:8000/listings/harvest-listings/
```

## Testing

Run the tests using:

```bash
python manage.py test listings
```

### Expected Test Output

A successful test run should show output similar to:

```text
Found 21 test(s).
Creating test database for alias 'default'...
System check identified no issues (0 silenced).
.......................

----------------------------------------------------------------------
Ran 21 tests in 0.077s

OK
Destroying test database for alias 'default'...
```
