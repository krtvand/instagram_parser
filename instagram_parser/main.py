import scrapy
from scrapy.crawler import CrawlerProcess
from instagram_parser.crawler.crawler.spiders.example import ExampleSpider

process = CrawlerProcess({'LOG_LEVEL': 'INFO'})

process.crawl(ExampleSpider)
process.start() # the script will block here until the crawling is finished