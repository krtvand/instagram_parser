import os
import unittest
from unittest.mock import MagicMock
import json

import requests_mock

from instagram_parser.crawler.crawler.spiders.example import ExampleSpider
from instagram_parser.crawler.tests.utils import fake_scrapy_response_from_file

class TestPagination(unittest.TestCase):
    PAGE_SOURCE = 'source_data/instagram_publications_by_location.html'
    JS_FILE_WITH_QUERYHASH = 'source_data/LocationPageContainer.js'
    SHARED_DATA_FILE = 'source_data/shared_data.txt'
    LOCATION_ID = '213526478'

    def setUp(self):

        self.response = fake_scrapy_response_from_file(file_name=self.PAGE_SOURCE)
        self.source_of_js_with_queryhash = self._load_shared_data(self.JS_FILE_WITH_QUERYHASH)
        self.shared_data = self._load_shared_data(self.SHARED_DATA_FILE)
        self.shared_data_as_dict = json.loads(self.shared_data)

    def _load_shared_data(self, file_name):
        if not file_name[0] == '/':
            responses_dir = os.path.dirname(os.path.realpath(__file__))
            file_path = os.path.join(responses_dir, file_name)
        else:
            file_path = file_name
        with open(file_path, 'r') as f:
            file_content = f.read()
            return file_content

    @requests_mock.Mocker()
    def test_get_link_for_js_file_with_queryhash(self, m):
        m.get('https://www.instagram.com/static/bundles/LocationPageContainer.js/0a8e5b85842a.js',
              text=self.source_of_js_with_queryhash)
        EXPECTED_QUERYHASH = '951c979213d7e7a1cf1d73e2f661cbd1'
        query_hash = ExampleSpider().get_query_hash(self.response)
        self.assertTrue(isinstance(query_hash, str))
        self.assertEqual(EXPECTED_QUERYHASH, query_hash)

    def test_get_url_for_next_page(self):
        spider = ExampleSpider()
        spider.location_id = self.LOCATION_ID
        spider.get_query_hash = MagicMock()
        spider.get_query_hash.return_value = '951c979213d7e7a1cf1d73e2f661cbd1'
        expected_url = 'https://www.instagram.com/graphql/query/?query_hash=951c979213d7e7a1cf1d73e2f661cbd1&variables=%7B%22id%22%3A%22213526478%22%2C%22first%22%3A12%2C%22after%22%3A%221718895412364831673%22%7D'
        url = spider.get_url_for_next_page(self.response, self.shared_data_as_dict)
        self.assertEqual(expected_url, url)
