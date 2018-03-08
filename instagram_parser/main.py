import json
import datetime

from scrapy.crawler import CrawlerProcess
from instagram_parser.crawler.crawler.spiders.example import ExampleSpider
from instagram_parser.crawler.crawler.posts_filter import PublicationDatePostFilter
from instagram_parser.crawler.crawler.spider_stopper import (PostPublicationDateStopper)


def parse_instagram(location_id: str, date_from: datetime.datetime, date_till: datetime.datetime):
    process = CrawlerProcess(
        {
            'LOG_LEVEL': 'INFO',
            'DOWNLOAD_DELAY': 1,
            'USER_AGENT': 'Firefox 20.0 (Win 8 32)" useragent="Mozilla/5.0 (Windows NT 6.2; rv:20.0) Gecko/20121202 Firefox/20.0'
        }
    )

    spider_stopper = PostPublicationDateStopper({'oldest_publication_date': date_from})
    posts_filter = PublicationDatePostFilter(date_from, date_till)
    result = {}
    process.crawl(ExampleSpider, spider_stopper=spider_stopper, posts_filter=posts_filter,
                  result=result, location_id=location_id)
    process.start()

    return result

if __name__ == '__main__':
    date_from = datetime.datetime.utcnow() - datetime.timedelta(minutes=40)
    date_till = datetime.datetime.utcnow() - datetime.timedelta(minutes=10)
    location_id = '224829075'

    result = parse_instagram(location_id=location_id, date_from=date_from, date_till=date_till)
    print(json.dumps(result))

    with open('parsing_results', 'w') as f:
        f.write(json.dumps(result))
