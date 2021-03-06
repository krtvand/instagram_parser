# -*- coding: utf-8 -*-

import unittest
import json

from instagram_parser.crawler.data_extractors.publications_by_location.next_page_data_extractor import (PublicationsByLocationNextPageDataExtractor)
from instagram_parser.crawler.data_extractors.publications_by_location.first_page_data_extractor import (FirstPageDataExtractor)
from instagram_parser.crawler.data_extractors.publications_by_tags_extractors.index_page_data_extractor import (
    IndexPageDataExtractor
)
from instagram_parser.crawler.data_extractors.publications_by_tags_extractors.next_page_data_extractor import (
    PublicationsByTagNextPageDataExtractor as PublicationByTagsNextPageDataExtractor
)
from instagram_parser.tests.utils import (
    load_text_from_file,
    fake_scrapy_response_from_file
)

class TestIndexPageParser(unittest.TestCase):

    def setUp(self):
        PAGE_SOURCE = 'publications_by_location/source_data/instagram_publications_by_location.html'
        SHARED_DATA_FILE = 'publications_by_location/source_data/shared_data.txt'
        POSTS_FILE = 'publications_by_location/source_data/posts_from_index_page.json'
        self.response = fake_scrapy_response_from_file(file_name=PAGE_SOURCE)
        self.shared_data = load_text_from_file(SHARED_DATA_FILE)
        self.shared_data_as_dict = json.loads(self.shared_data)
        self.new_posts = load_text_from_file(POSTS_FILE)
        self.parser = FirstPageDataExtractor()

    def test_shared_data_extractor(self):
        shared_data = self.parser.get_page_info_from_json(self.response)
        self.assertTrue(isinstance(shared_data, dict))
        self.assertTrue('entry_data' in shared_data)

    def test_get_post_objects(self):
        POSTS_NUMBER_ON_MAIN_PAGE = 24
        shared_data_as_dict = json.loads(self.shared_data)
        post_objects = self.parser.get_post_objects(shared_data_as_dict)
        self.assertEqual(len(post_objects), POSTS_NUMBER_ON_MAIN_PAGE)
        self.assertDictEqual(json.loads(self.new_posts)[0], post_objects[0])

    def test_collect_data_from_post(self):
        expected_post_id = '1754649737996730763'
        expected_post_data = {
            'owner_id': '1750329502',
            'shortcode': 'BhZxKPihwGL',
            # 22 February 2018 г., 16:39:23
            'publication_date': 1523390570
        }
        expected = {expected_post_id: expected_post_data}

        post = json.loads(self.new_posts)[0]
        data = self.parser.collect_data_from_post(post)

        self.assertDictEqual(expected, data)


class TestNextPageParser(unittest.TestCase):

    def setUp(self):
        NEXT_PAGE_SOURCE = 'publications_by_location/source_data/instagram_publications_by_location_next_page.json'
        NEXT_PAGE_POSTS = 'publications_by_location/source_data/posts_from_next_page.json'
        self.response = fake_scrapy_response_from_file(file_name=NEXT_PAGE_SOURCE)
        self.next_page_data_str = load_text_from_file(NEXT_PAGE_SOURCE)
        self.next_page_data_as_dict = json.loads(self.next_page_data_str)
        self.new_posts = load_text_from_file(NEXT_PAGE_POSTS)
        self.parser = PublicationsByLocationNextPageDataExtractor()

    def test_extract_data_from_next_page(self):
        next_page_data_dict = self.parser.get_page_info_from_json(self.response)
        self.assertTrue(isinstance(next_page_data_dict, dict))
        self.assertTrue('data' in next_page_data_dict)

    def test_get_post_objects(self):
        POSTS_NUMBER_FROM_NEXT_PAGE = 12
        post_objects = self.parser.get_post_objects(self.next_page_data_as_dict)
        self.assertEqual(len(post_objects), POSTS_NUMBER_FROM_NEXT_PAGE)
        self.assertDictEqual(json.loads(self.new_posts)[0], post_objects[0])

    def test_collect_data_from_post(self):
        expected_post_id = '1718847872394689700'
        expected_post_data = {
            'owner_id': '1156705436',
            'shortcode': 'Bfakwh5BXyk',
            'publication_date': 1519122655
        }
        expected = {expected_post_id: expected_post_data}

        post = json.loads(self.new_posts)[0]
        data = self.parser.collect_data_from_post(post)

        self.assertDictEqual(expected, data)