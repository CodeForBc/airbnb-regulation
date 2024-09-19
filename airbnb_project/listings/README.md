# Harvest Listings API

This project includes a Django API endpoint that triggers a listings collections process using Scrapy. The view (
`harvest_listings`) allows users to start the scraping process via a get request.

## Prerequisites

1. Have python3 installed
2. Have all the poetry dependencies installed
3. Have postgres server running

## Running the Server

1. **Start the Django Development Server**:

    ```bash
    python manage.py runserver
    ```

   This will start the server on `http://127.0.0.1:8000/`.

## Endpoint Details

### `GET /harvest-listings/`

This endpoint starts the harvesting process.

- **URL**: `listings/harvest-listings/`
- **Method**: `GET`
- **Status Codes**:
    - `200`: Harvesting process started successfully.
    - `409`: A harvesting process is already running.
    - `500`: Failed to start the harvesting process due to an internal error.

## How to Trigger the View

You can trigger the harvesting process by sending a GET request to the `listings/harvest-listings/` endpoint.  
The harvested listings will be saved in `listings_djando.csv` in `harvester_app/harvester/spiders/`.

## Testing

To the run tests for the listings modules:

```sh
python manage.py test listings
```

Example output when all tests passed:

```text
Found 18 test(s).
Creating test database for alias 'default'...
System check identified no issues (0 silenced).
.2024-09-19 16:27:16 [listings.views] ERROR: Failed to start harvesting process: Crawler error
2024-09-19 16:27:16 [django.request] ERROR: Internal Server Error: /listings/harvest-listings/
........regis 123456
.........
----------------------------------------------------------------------
Ran 18 tests in 0.016s

OK

```