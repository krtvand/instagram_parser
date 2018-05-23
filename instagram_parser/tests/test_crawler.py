# -*- coding: utf-8 -*-

import unittest
from mock import MagicMock
import json
import datetime

from dateutil.parser import parse
import requests_mock

from instagram_parser.tests.utils import (fake_scrapy_response_from_file,
                                                    load_text_from_file)
from instagram_parser.crawler.utils.pagination import (PaginatorInFirstPage,
                                                       Paginator,
                                                       PaginatorInNextPage)
from instagram_parser.main import parse_instagram
import json
import datetime

from scrapy.crawler import CrawlerProcess
from instagram_parser.crawler.spiders.instagram_posts_spider import InstagramPostsSpider
from instagram_parser.crawler.utils.posts_filter import (PublicationDatePostFilter,
                                                         DummyPostFilter)
from instagram_parser.crawler.utils.spider_stopper import (PostPublicationDateStopper,
                                                           ItemsCountSpiderStopper)



class TestSpiderClientBase:
    LOCATION_ID = '213526478'
    base_url = 'https://www.instagram.com'
    SHARED_DATA_FILE = 'source_data/shared_data.txt'


class TestSpiderClient(TestSpiderClientBase, unittest.TestCase):
    """
    Не работает
    """

    def setUp(self):

        PAGE_SOURCE = 'source_data/instagram_publications_by_location.html'
        JS_FILE_WITH_QUERYHASH = 'source_data/LocationPageContainer.js'
        self.shared_data = load_text_from_file(self.SHARED_DATA_FILE)
        self.shared_data_as_dict = json.loads(self.shared_data)
        self.response = fake_scrapy_response_from_file(file_name=PAGE_SOURCE)
        self.response_for_js_with_queryhash = fake_scrapy_response_from_file(
            file_name=JS_FILE_WITH_QUERYHASH)
        self.source_of_js_with_queryhash = load_text_from_file(JS_FILE_WITH_QUERYHASH)
        self.source_of_js_with_queryhash = load_text_from_file(JS_FILE_WITH_QUERYHASH)
        self.last_post_id = '1718895412364831673'
        self.paginator = Paginator(self.base_url, location_id=self.LOCATION_ID)

    @requests_mock.Mocker()
    def test_get_queryhash(self, m):

        m.get('https://www.instagram.com/static/bundles/LocationPageContainer.js/0a8e5b85842a.js',
              text=self.source_of_js_with_queryhash.decode('utf-8'))

        date_from = parse('2018-04-10T20:02:50+00:00')
        date_till = parse('2018-04-10T20:02:00+00:00')
        result = {}

        spider_stopper = PostPublicationDateStopper({'oldest_publication_date': date_from})
        posts_filter = PublicationDatePostFilter(date_from, date_till)

        parser = InstagramPostsSpider(spider_stopper = spider_stopper, posts_filter = posts_filter,
                                      result = result, location_id = self.LOCATION_ID)
        parser.parse(self.response)
        print(result)
