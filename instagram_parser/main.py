import json
import datetime

from scrapy.crawler import CrawlerProcess
from instagram_parser.crawler.crawler.spiders.example import ExampleSpider
from instagram_parser.crawler.crawler.spider_stopper import (ItemsCountSpiderStopper,
                                                             PostPublicationDateStopper)


MAX_ITEMS_COUNT = 10
FILE_NAME = 'result.json'
DATE_TILL = datetime.datetime.utcnow() - datetime.timedelta(minutes=30)

process = CrawlerProcess(
    {
        'LOG_LEVEL': 'INFO',
        'DOWNLOAD_DELAY': 1,
        'USER_AGENT': 'Firefox 20.0 (Win 8 32)" useragent="Mozilla/5.0 (Windows NT 6.2; rv:20.0) Gecko/20121202 Firefox/20.0'
    }
)

# spider_stopper = ItemsCountSpiderStopper({'max_items_count': MAX_ITEMS_COUNT})
spider_stopper = PostPublicationDateStopper({'oldest_publication_date': DATE_TILL})

def parse_instagram():
    process.crawl(ExampleSpider, spider_stopper=spider_stopper, result_file=FILE_NAME)
    process.start()

    with open(FILE_NAME, 'r') as f:
        result_json = f.read()
    result = json.dumps(result_json)

    return result

if __name__ == '__main__':
    res = parse_instagram()
    print(res)