# Harvester App

Harvester is a web scraping application designed to collect data from Airbnb listings. It uses Scrapy, a powerful web
scraping framework for Python.

## Project Structure

```
harvestor_app/
│
├── harvester/
│   ├── spiders/
│   │   ├── init.py
│   │   ├── airbnb_url_builder.py
│   │   ├── cordinates.json
│   │   ├── listings_spider.py
│   │
│   ├── init.py
│   ├── items.py
│   ├── middlewares.py
│   ├── pipelines.py
│   ├── settings.py
│   
│
├── README.md
└── scrapy.cfg

```

## Description

This project is structured to scrape Airbnb listings data. Here's a brief overview of the key components:

- `spiders/`: Contains the spider definitions and related JSON files.
    - `listings_spider.py`: The main spider for scraping Airbnb listings.
    - `airbnb_url_builder.py`: Utility for building Airbnb URLs.
    - `coordinates.json`: Contains coordinates for the edges of boxes in which airbnb listings are searched in.
- `items.py`: Defines the data structure for scraped items.
- `middlewares.py`: Contains custom middleware components.
- `pipelines.py`: Defines data processing pipelines.
- `settings.py`: Configuration settings for the Scrapy project.

## Setup and Installation

1. Follow the root `README.md` to install any dependencies required.
2. Add the airbnb API key in `custom_settings.py` for the `AIRBNB_PUBLIC_API_KEY` key. 

## Usage

To run the spider:

1. `cd` into the `spiders` directory
2. Run `python3 listings_spiders.py`.

This should run the spider, you will get an output like this. This shows the start of the spider.
It will also print out the ids of listings it has saved.

```
024-08-12 13:36:42 [scrapy.utils.log] INFO: Scrapy 2.11.2 started (bot: harvester)
2024-08-12 13:36:42 [scrapy.utils.log] INFO: Versions: lxml 5.2.2.0, libxml2 2.11.7, cssselect 1.2.0, parsel 1.9.1, w3lib 2.2.1, Twisted 24.3.0, Python 3.10.11 (tags/v3.10.11:7d4cc5a, Apr  5 2023, 00:38:17) [MSC v.1929 64 bit (AMD64)], pyOpenSSL 24.2.1 (OpenSSL 3.3.1 4 Jun 2024), cryptography 43.0.0, Platform Windows-10-10.0.22631-SP0
.
.
.
.
.
listing_id 19271929
listing_id 829152679576545039
listing_id 578285252934806382
```

3. Once the spider has finished, it will save all the listings to `listings.csv` in the `spiders` folder.

## Process of Getting Listings Step-by-Step

The process of getting Airbnb listings using the `ListingsSpider` involves multiple steps that can be broken down into
phases: initialization, sending requests, parsing responses, and handling pagination. Here’s a step-by-step explanation:

#### 1. Initialization Phase

1. **Setting Up the Spider**:
    - The `ListingsSpider` class is initialized with attributes such
      as `allowed_domains`, `start_urls`, `next_page_cursors`, `total_listings`, and `ALREADY_SCRAPED_LISTINGS`.

2. **Loading Already Scraped Listings**:
    - The spider reads already scraped listing IDs from a CSV file and stores them in the `ALREADY_SCRAPED_LISTINGS` set
      to avoid re-scraping the same listings.

3. **Loading Coordinates**:
    - Coordinates are read from a JSON file in which the locations will be processed.

4. **Generating Initial Requests**:
    - Initial Scrapy requests are generated using the URL templates and the coordinates read from the JSON file. Each
      request is a `FormRequest` to search Airbnb listings in specific areas of Vancouver.

#### 2. Sending Requests Phase

1. **Sending Initial Requests**:
    - The `start_requests` method sends out the generated requests to the URLs formed using the coordinates and URL
      templates.

#### 3. Parsing Responses Phase

1. **Parsing Search Results**:
    - The `parse` method handles the response from Airbnb's search results page.
    - The method extracts the JSON data embedded in the page's script tag.
    - It parses the JSON to extract listings and pagination information.
    - For each listing, it checks if the listing ID has already been scraped.

2. **Requesting Listing Details**:
    - If a listing has not been scraped yet, it constructs a new request URL to fetch detailed information about the
      listing.
    - The constructed URL uses the Airbnb API with the listing ID encoded using base64 and URL encoding functions.
    - These requests are sent with the necessary headers, including the API key.

#### 4. Handling Listing Details Phase

1. **Handling Detailed Listing Responses**:
    - The `handle_listing` method handles the response containing detailed information about a listing.
    - It parses the JSON response to extract detailed information such as location, person capacity, registration
      number, number of beds, and number of baths.
    - An `ExpandedAirBnBListingItem` object is created with the extracted details.

2. **Yielding Listing Items**:
    - The listing item is yielded, which Scrapy collects and processes (e.g., storing it in a database or a file).

#### 5. Handling Pagination Phase

1. **Handling Pagination**:
    - The `parse` method also extracts pagination cursors from the JSON data.
    - If there are more pages to process, it constructs a new URL for the next page using the cursor and sends a request
      to continue parsing.

### Diagram Representation

A diagram can help visualize this process. Here’s a high-level flowchart:

```plaintext
Start
  |
  V
Initialize Spider
  |
  V
Load Already Scraped Listings
  |
  V
Load Coordinates
  |
  V
Generate Initial Requests
  |
  V
Send Initial Requests
  |
  V
Parse Search Results
  |          |
  |          V
  |   Extract Listings
  |          |
  |          V
  |   For each Listing
  |          |
  |          V
  |  Check if Already Scraped
  |          |
  |          V
  |  Construct Details Request
  |          |
  |          V
  | Send Details Request ----
  |                          |
  |                          V
  |                  Handle Details Response
  |                          |
  |                          V
  |                Extract Listing Details
  |                          |
  |                          V
  |                Yield Listing Item
  |                          |
  |                          V
  |                 Check for More Pages
  |                          |
  |                          V
  -----------------------------------
                |
                V
             End
```

In the diagram:

- Each box represents a process step.
- Arrows represent the flow from one step to the next.
- The loop back to "Send Initial Requests" represents handling pagination by sending requests for additional pages.