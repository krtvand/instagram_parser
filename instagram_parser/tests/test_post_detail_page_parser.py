# -*- coding: utf-8 -*-

import unittest
import json

from instagram_parser.tests.utils import (fake_scrapy_response_from_file,
                                                    load_text_from_file)

from instagram_parser.crawler.data_extractors.post_detail_page_data_extractor import (PostDetailPageDataExtractor)

class TestIndexPageParser(unittest.TestCase):

    def setUp(self):
        PAGE_SOURCE_FILE_NAME = 'source_data/post_detail_source.json'
        self.response = fake_scrapy_response_from_file(file_name=PAGE_SOURCE_FILE_NAME)
        self.page_data_as_dict = json.loads(load_text_from_file(PAGE_SOURCE_FILE_NAME))
        self.parser = PostDetailPageDataExtractor()

    def test_collect_data_from_post(self):
        expected_post_id = '1724081323683765859'
        expected_post_data = {
            'owner_username': 'etsu_real',
        }
        expected = {expected_post_id: expected_post_data}

        post_info = self.parser.collect_data_from_post(self.page_data_as_dict)
        self.assertEqual(expected, post_info)