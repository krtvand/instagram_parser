from scrapy.crawler import CrawlerProcess
from instagram_parser.crawler.crawler.spiders.example import ExampleSpider
from instagram_parser.crawler.crawler.spider_stopper import ItemsCountSpiderStopper


MAX_ITEMS_COUNT = 50

process = CrawlerProcess(
    {'LOG_LEVEL': 'INFO', 'FEED_URI': 'result.json', 'FEED_FORMAT': 'json'}
)

spider_stopper = ItemsCountSpiderStopper({'max_items_count': MAX_ITEMS_COUNT})

process.crawl(ExampleSpider, spider_stopper=spider_stopper)
process.start() # the script will block here until the crawling is finished