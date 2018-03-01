import scrapy
from scrapy.crawler import CrawlerProcess
from instagram_parser.crawler.crawler.spiders.example import ExampleSpider

process = CrawlerProcess(
    {'LOG_LEVEL': 'INFO', 'FEED_URI': 'result.json', 'FEED_FORMAT': 'json'}
)

process.crawl(ExampleSpider)
process.start() # the script will block here until the crawling is finished