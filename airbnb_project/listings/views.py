from django.http import HttpResponse
from twisted.internet import reactor
from scrapy.crawler import CrawlerRunner
from listings.harvestor_app.harvester.spiders.update_listing_spider import UpdateListingSpider
from listings.harvestor_app.harvester.test_settings import get_scrapy_settings


def scrapy_background_process():
    print("Scrapy process started")
    runner = CrawlerRunner(settings=get_scrapy_settings())
    d = runner.crawl(UpdateListingSpider)
    d.addBoth(lambda _: reactor.stop())
    reactor.run()
    print("Scrapy process done")


def scrape_listings(request):
    scrapy_background_process()
    return HttpResponse("process started")
