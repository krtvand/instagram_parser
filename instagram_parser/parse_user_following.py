# -*- coding: utf-8 -*-

import json
import datetime

from scrapy.crawler import CrawlerProcess
from instagram_parser.crawler.spiders.user_following_spider import UserFollowingSpider


def parse_user_following(login, password, username):
    process = CrawlerProcess(
        {
            'LOG_LEVEL': 'DEBUG',
            'DOWNLOAD_DELAY': 1,
            'USER_AGENT': 'Firefox 20.0 (Win 8 32)" useragent="Mozilla/5.0 (Windows NT 6.2; rv:20.0) Gecko/20121202 Firefox/20.0'
        }
    )
    result = {}
    process.crawl(UserFollowingSpider, login=login, password=password, result=result, target_username=username)
    process.start()

    return result


if __name__ == '__main__':
    username = 'mordovian_air'

    login = ''
    password = ''
    if not login:
        raise Exception('Login empty')

    result = parse_user_following(login=login, password=password, username=username)
    print(json.dumps(result))
    print(len(result))
