# -*- coding: utf-8 -*-

import json
import datetime

from scrapy.crawler import CrawlerProcess
from instagram_parser.crawler.spiders.instagram_posts_spider import InstagramPostsSpider
from instagram_parser.crawler.utils.posts_filter import (PublicationDatePostFilter,
                                                         DummyPostFilter)
from instagram_parser.crawler.utils.spider_stopper import (PostPublicationDateStopper,
                                                           ItemsCountSpiderStopper)


def parse_instagram(location_id, date_from, date_till, max_items=None):
    process = CrawlerProcess(
        {
            'LOG_FILE': 'parser_logs.log',
            'LOG_LEVEL': 'DEBUG',
            'DOWNLOAD_DELAY': 1,
            'USER_AGENT': 'Firefox 20.0 (Win 8 32)" useragent="Mozilla/5.0 (Windows NT 6.2; rv:20.0) Gecko/20121202 Firefox/20.0'
        }
    )
    if max_items:
        spider_stopper = ItemsCountSpiderStopper({'max_items_count': max_items})
        posts_filter = DummyPostFilter()
    else:
        spider_stopper = PostPublicationDateStopper({'oldest_publication_date': date_from})
        posts_filter = PublicationDatePostFilter(date_from, date_till)


    result = {}
    process.crawl(InstagramPostsSpider, spider_stopper=spider_stopper, posts_filter=posts_filter,
                  result=result, location_id=location_id)
    process.start()

    return result

if __name__ == '__main__':
    date_from = datetime.datetime.utcnow() - datetime.timedelta(minutes=40)
    date_till = datetime.datetime.utcnow() - datetime.timedelta(minutes=10)
    location_id = '224829075'

    result = parse_instagram(location_id=location_id, date_from=date_from, date_till=date_till, max_items=40)
    # result = parse_instagram(location_id=location_id, date_from=date_from, date_till=date_till)
    print(json.dumps(result))

    with open('parsing_results', 'w') as f:
        f.write(json.dumps(result))
