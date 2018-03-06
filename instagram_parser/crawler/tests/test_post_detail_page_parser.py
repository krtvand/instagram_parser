import unittest
import os
import re
import json

from scrapy.http import HtmlResponse, Request
from instagram_parser.crawler.tests.utils import fake_scrapy_response_from_file

from instagram_parser.crawler.crawler.post_detail_page_parser import (PostDetailPageParser)

class TestIndexPageParser(unittest.TestCase):

    def setUp(self):
        PAGE_SOURCE_FILE_NAME = 'source_data/post_detail_source.json'
        self.response = fake_scrapy_response_from_file(file_name=PAGE_SOURCE_FILE_NAME)
        self.page_data_as_dict = json.loads(self._load_shared_data(PAGE_SOURCE_FILE_NAME))
        self.parser = PostDetailPageParser()

    def _load_shared_data(self, file_name):
        if not file_name[0] == '/':
            responses_dir = os.path.dirname(os.path.realpath(__file__))
            file_path = os.path.join(responses_dir, file_name)
        else:
            file_path = file_name
        with open(file_path, 'r') as f:
            file_content = f.read()
            return file_content

    def test_get_owner_username(self):
        post_owner_username = self.parser.get_owner_username(self.page_data_as_dict)
        expected = 'etsu_real'
        self.assertEqual(expected, post_owner_username)

    def test_collect_data_from_post(self):
        expected_post_id = '1724081323683765859'
        expected_post_data = {
            'owner_username': 'etsu_real',
        }
        expected = {expected_post_id: expected_post_data}

        post_info = self.parser.collect_data_from_post(self.page_data_as_dict)
        self.assertEqual(expected, post_info)