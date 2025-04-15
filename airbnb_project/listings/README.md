
# Airbnb Listings Harvester API

A Django API service that harvests Airbnb listings data using Scrapy.

## Prerequisites

To run this service, you'll need to set up Docker and Docker Compose for the environment. Please follow the instructions below for setting up Docker, building the containers, and configuring the environment.

### 1. Install Docker and Docker Compose

Ensure you have Docker and Docker Compose installed on your system. If not, you can install them as follows:

- **Docker Installation**: [Install Docker](https://docs.docker.com/get-docker/)
- **Docker Compose Installation**: [Install Docker Compose](https://docs.docker.com/compose/install/)

### 2. Set Up the Environment

Create a `.env` file in the root directory of the project with the following configuration. This file contains environment variables that will be used by the Docker containers:

#### Example `.env` File:

```env
# Django settings
SECRET_KEY=your_secret_key
DJANGO_DEBUG=True
AIRBNB_PUBLIC_API_KEY=

# PostgreSQL settings
POSTGRES_PASSWORD=your_password
POSTGRES_USER=your_username
POSTGRES_DB=your_db_name
POSTGRES_HOST_PORT=5432
```

Replace the placeholders with your actual values:
- **SECRET_KEY**: A secret key for Django.
- **POSTGRES_PASSWORD**, **POSTGRES_USER**, **POSTGRES_DB**: Credentials for your PostgreSQL database.

The `.env` file will automatically be used by Docker Compose to configure your containers.

### 3. Starting the Services

Run the following command from the root directory of your project to start all the necessary services:

```bash
docker-compose up -d
```

This command will:
- Build and start the PostgreSQL database container.
- Build and start the `listings` Django app container.
- Automatically install dependencies and apply database migrations inside the container.

### 4. Accessing the Application

Once the services are running, the Django server will be available at `http://localhost:8001/` on your host machine. You can access the API and other resources via this URL.

## API Documentation

### Harvest Listings Endpoint

This endpoint triggers the process of harvesting Airbnb listings data.

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

Example usage with `curl`:

```bash
curl http://localhost:8001/listings/harvest-listings/
```

## Testing

To run tests within the `listings` container, execute the following command:

```bash
docker-compose exec listings python manage.py test listings
```

This will run the tests for the `listings` app and output the results to your terminal.

### Expected Test Output

A successful test run should show output similar to the following:

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

### Development
* If you want to re-create all the containers, you can use 

```
docker compose up -d --build --force-recreate
```

* To tail logs for a docker container, you can use

```
docker logs -f --tail 50 <container_name>
```