Here's an updated README that assumes the container already installs dependencies and handles database migrations
automatically:

---

# Airbnb Listings Harvester API

A Django API service that harvests Airbnb listings data using Scrapy.

## Prerequisites

- Setup of container is required for this service. Please look at the root README.md for more information on how to set
  up.

## Setup

### 1. Starting the Services

Run the following command, in the root, to start all services, including the `listings` Django app and the PostgreSQL database:

```bash
docker-compose up -d
```

This command:

- Starts a PostgreSQL database container that the Django application connects to.
- Launches the `listings` container with the Django API server running at `http://localhost:8001/`.
- Automatically handles dependency installation and database migrations inside the container.

### 2. Accessing the Application

The Django server is accessible at `http://localhost:8001/` on your host machine.

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
curl http://localhost:8001/listings/harvest-listings/
```

## Testing

To run tests in the `listings` container:

```bash
docker-compose exec listings python manage.py test listings
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

## Troubleshooting

- **Database Connection Errors**: Make sure the `db` container is healthy and reachable. Check your `.env` file to
  ensure all environment variables are correctly set.
- **Permission Issues**: For development, ensure shared volumes have the correct permissions if you encounter file
  access issues.

