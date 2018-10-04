# -*- coding: utf-8 -*-

import json
import datetime

from scrapy.crawler import CrawlerProcess
from instagram_parser.crawler.spiders.user_following_spider import UserFollowingSpider
from instagram_parser.crawler.utils.spider_stopper import ItemsCountSpiderStopper


def parse_user_following(username, max_items=None):
    process = CrawlerProcess(
        {
            'LOG_LEVEL': 'DEBUG',
            'DOWNLOAD_DELAY': 1,
            'COOKIES_DEBUG': True,
            'USER_AGENT': 'Firefox 20.0 (Win 8 32)" useragent="Mozilla/5.0 (Windows NT 6.2; rv:20.0) Gecko/20121202 Firefox/20.0'
        }
    )
    if max_items:
        spider_stopper = ItemsCountSpiderStopper({'max_items_count': max_items})

    result = {}
    process.crawl(UserFollowingSpider, spider_stopper=spider_stopper, result=result, username=username)
    process.start()

    return result

if __name__ == '__main__':
    username = 'kartaev1958'

    result = parse_user_following(username=username, max_items=80)
    print(json.dumps(result))
    print(len(result))

    with open('parsing_results', 'w') as f:
        f.write(json.dumps(result))
