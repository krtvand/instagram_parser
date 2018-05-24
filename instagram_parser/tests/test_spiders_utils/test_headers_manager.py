
import unittest
from mock import MagicMock
import json

import requests_mock

from instagram_parser.tests.utils import (fake_scrapy_response_from_file,
                                                    load_text_from_file)
from instagram_parser.crawler.utils.headers_manager import PaginationHeadersManager


class TestHeadersManager(unittest.TestCase):

    def test_get_headers(self):
        pagination_uri_variables = '{"id":"213526478","first":12,"after":"1718895412364831673"}'
        rhx_gis = '510a7a8c35c8837193fbc929e20e1824'
        expected_headers = {
            'x-requested-with': 'XMLHttpRequest',
            'x-instagram-gis': '302b579bfc5fa8c3e409761834bc895e'
        }
        headers = PaginationHeadersManager(rhx_gis, pagination_uri_variables).get_headers()
        self.assertEqual(expected_headers, headers)