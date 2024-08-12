# Harvester App

Harvester is a web scraping application designed to collect data from Airbnb listings. It uses Scrapy, a powerful web scraping framework for Python.

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

Follow the root `README.md` to install any dependencies required. 

## Usage

To run the spider:
1. `cd` into the `harvester` directory
2. Run `scrapy crawl <spider name>`. The spider name to crawl airbnb listings is `listings_spider`.

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
3. Once the spider has finished, it will save all the listings to `listings.csv` in the `harvester` folder.

