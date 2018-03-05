import unittest
import os
import re
import json

from scrapy.http import HtmlResponse, Request

from instagram_parser.crawler.crawler.data_extractor import (NextPageParser,
                                                             FirstPageParser)

class TestIndexPageParser(unittest.TestCase):

    def setUp(self):
        PAGE_SOURCE = 'source_data/instagram_publications_by_location.html'
        SHARED_DATA_FILE = 'source_data/shared_data.txt'
        POSTS_FILE = 'source_data/posts_from_index_page.json'
        self.response = fake_response_from_file(file_name=PAGE_SOURCE)
        self.shared_data = self._load_shared_data(SHARED_DATA_FILE)
        self.shared_data_as_dict = json.loads(self.shared_data)
        self.new_posts = self._load_shared_data(POSTS_FILE)
        self.parser = FirstPageParser()

    def _load_shared_data(self, file_name):
        if not file_name[0] == '/':
            responses_dir = os.path.dirname(os.path.realpath(__file__))
            file_path = os.path.join(responses_dir, file_name)
        else:
            file_path = file_name
        with open(file_path, 'r') as f:
            file_content = f.read()
            return file_content

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
        expected_post_id = '1720482878935489581'
        expected_post_data = {
            'owner_id': '2085484199',
            'shortcode': 'BfgYhAZF1wt'
        }
        expected = {expected_post_id: expected_post_data}

        post = json.loads(self.new_posts)[0]
        data = self.parser.collect_data_from_post(post)

        self.assertDictEqual(expected, data)


def fake_response_from_file(file_name, url=None):
    """
    Create a Scrapy fake HTTP response from a HTML file
    @param file_name: The relative filename from the responses directory,
                      but absolute paths are also accepted.
    @param url: The URL of the response.
    returns: A scrapy HTTP response which can be used for unittesting.
    """
    if not url:
        url = 'http://www.example.com'

    request = Request(url=url)
    if not file_name[0] == '/':
        responses_dir = os.path.dirname(os.path.realpath(__file__))
        file_path = os.path.join(responses_dir, file_name)
    else:
        file_path = file_name
    with open(file_path, 'rb') as f:
        file_content = f.read()

    response = HtmlResponse(url=url,
        request=request,
        body=file_content)
    return response


class TestNextPageParser(unittest.TestCase):

    def setUp(self):
        NEXT_PAGE_SOURCE = 'source_data/instagram_publications_by_location_next_page.json'
        NEXT_PAGE_POSTS = 'source_data/posts_from_next_page.json'
        self.response = fake_response_from_file(file_name=NEXT_PAGE_SOURCE)
        self.next_page_data_str = self._load_shared_data(NEXT_PAGE_SOURCE)
        self.next_page_data_as_dict = json.loads(self.next_page_data_str)
        self.new_posts = self._load_shared_data(NEXT_PAGE_POSTS)
        self.parser = NextPageParser()

    def _load_shared_data(self, file_name):
        if not file_name[0] == '/':
            responses_dir = os.path.dirname(os.path.realpath(__file__))
            file_path = os.path.join(responses_dir, file_name)
        else:
            file_path = file_name
        with open(file_path, 'r') as f:
            file_content = f.read()
            return file_content

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
            'shortcode': 'Bfakwh5BXyk'
        }
        expected = {expected_post_id: expected_post_data}

        post = json.loads(self.new_posts)[0]
        data = self.parser.collect_data_from_post(post)

        self.assertDictEqual(expected, data)