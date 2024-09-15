from django.http import HttpResponse
from twisted.internet import reactor
from scrapy.crawler import CrawlerRunner
from listings.harvester_app.harvester.spiders.listings_spider import ListingsSpider
from listings.harvester_app.harvester.custom_settings import get_scrapy_settings


def scrapy_background_process():
    print("Scrapy process started")
    runner = CrawlerRunner(settings=get_scrapy_settings())
    d = runner.crawl(ListingsSpider)
    d.addBoth(lambda _: reactor.stop())
    reactor.run()
    print("Scrapy process done")


def scrape_listings(request):
    scrapy_background_process()
    return HttpResponse("process started")
