
import unittest
from mock import MagicMock
import json

import requests_mock

from instagram_parser.tests.utils import (fake_scrapy_response_from_file,
                                                    load_text_from_file)
from instagram_parser.crawler.utils.headers_manager import FirstPagePaginationHeadersManager

class TestPaginatorBase:
    LOCATION_ID = '213526478'
    base_url = 'https://www.instagram.com'
    SHARED_DATA_FILE = 'source_data/shared_data.txt'


class TestHeadersManager(TestPaginatorBase, unittest.TestCase):

    def setUp(self):

        PAGE_SOURCE = 'source_data/instagram_publications_by_location.html'
        JS_FILE_WITH_QUERYHASH = 'source_data/LocationPageContainer.js'
        self.shared_data = load_text_from_file(self.SHARED_DATA_FILE)
        self.shared_data_as_dict = json.loads(self.shared_data)
        self.response = fake_scrapy_response_from_file(file_name=PAGE_SOURCE)
        self.response_for_js_with_queryhash = fake_scrapy_response_from_file(
            file_name=JS_FILE_WITH_QUERYHASH)
        self.source_of_js_with_queryhash = load_text_from_file(JS_FILE_WITH_QUERYHASH)
        self.response = fake_scrapy_response_from_file(file_name=PAGE_SOURCE)
        self.source_of_js_with_queryhash = load_text_from_file(JS_FILE_WITH_QUERYHASH)
        self.last_post_id = '1718895412364831673'


    def test_get_headers(self):
        pagination_uri_variables = '{"id":"213526478","first":12,"after":"1718895412364831673"}'
        rhx_gis = '510a7a8c35c8837193fbc929e20e1824'
        expected_headers = {
            'x-requested-with': 'XMLHttpRequest',
            'x-instagram-gis': '302b579bfc5fa8c3e409761834bc895e'
        }
        headers = FirstPagePaginationHeadersManager(rhx_gis, pagination_uri_variables).get_headers()
        self.assertEqual(expected_headers, headers)