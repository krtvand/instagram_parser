import os
import unittest

import requests_mock

from instagram_parser.crawler.crawler.spiders.example import ExampleSpider
from instagram_parser.crawler.tests.utils import fake_scrapy_response_from_file

class TestQueryHashExtractor(unittest.TestCase):

    def setUp(self):
        PAGE_SOURCE = 'source_data/instagram_publications_by_location.html'
        JS_FILE_WITH_QUERYHASH = 'source_data/LocationPageContainer.js'
        self.response = fake_scrapy_response_from_file(file_name=PAGE_SOURCE)
        self.source_of_js_with_queryhash = self._load_shared_data(JS_FILE_WITH_QUERYHASH)

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