# -*- coding: utf-8 -*-

import unittest

from instagram_parser.crawler.data_extractors.user_following.user_page_data_extractor import \
    UserPageDataExtractor
from instagram_parser.tests.utils import (
    fake_scrapy_response_from_file
)


class TestUserPageDataExtracor(unittest.TestCase):
    def setUp(self):
        page_source = 'user_following/source_data/user_page_source.html'
        self.response = fake_scrapy_response_from_file(file_name=page_source)

    def test_get_shared_data(self):
        shared_data = UserPageDataExtractor().get_page_info_from_json(self.response)
        self.assertTrue(isinstance(shared_data, dict))
        self.assertTrue('entry_data' in shared_data)