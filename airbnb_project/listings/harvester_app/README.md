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
