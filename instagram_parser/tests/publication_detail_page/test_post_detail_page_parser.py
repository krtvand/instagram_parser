# -*- coding: utf-8 -*-

import unittest
import json

from instagram_parser.tests.utils import (fake_scrapy_response_from_file,
                                                    load_text_from_file)

from instagram_parser.crawler.data_extractors.post_detail_page_data_extractor import (PostDetailPageDataExtractor)

class TestIndexPageParser(unittest.TestCase):

    def setUp(self):
        PAGE_SOURCE_FILE_NAME = 'publication_detail_page/source_data/post_detail_source.json'
        self.response = fake_scrapy_response_from_file(file_name=PAGE_SOURCE_FILE_NAME)
        self.page_data_as_dict = json.loads(load_text_from_file(PAGE_SOURCE_FILE_NAME))
        self.parser = PostDetailPageDataExtractor()

    def test_collect_data_from_post(self):
        expected_post_id = u'1724081323683765859'
        expected_post_data = {
            'edge_media_to_caption': u"\u041f\u0440\u043e\u0441\u0442\u043e \u0444\u043e\u0442\u043e \u0441 \u0418\u041d\u041a.\n\u041d\u0438\u043a\u0430\u043a\u043e\u0439 \u0441\u043c\u044b\u0441\u043b\u043e\u0432\u043e\u0439 \u043d\u0430\u0433\u0440\u0443\u0437\u043a\u0438",
            'owner_username': u'etsu_real',
        }
        expected = {expected_post_id: expected_post_data}

        post_info = self.parser.collect_data_from_post(self.page_data_as_dict)
        self.assertEqual(expected, post_info)