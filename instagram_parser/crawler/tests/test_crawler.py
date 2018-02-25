import unittest
import os
import re
import json

from scrapy.http import HtmlResponse, Request

from instagram_parser.crawler.crawler.data_extractor import (extract_shared_data,
                                                             get_post_objects,
                                                             get_owner_ids_from_posts_list,
                                                             get_last_post_id,
                                                             pagination_has_next_page)

from instagram_parser.crawler.crawler.query_hash_extractor import (get_link_for_js_file_with_queryhash,
                                                                   get_queryhash_from_js_file)


class TestIndexPageParser(unittest.TestCase):

    def setUp(self):
        PAGE_SOURCE = 'source_data/instagram_publications_by_location.html'
        SHARED_DATA_FILE = 'source_data/shared_data.txt'
        POSTS_FILE = 'source_data/posts_from_index_page.json'
        self.response = fake_response_from_file(file_name=PAGE_SOURCE)
        self.shared_data = self._load_shared_data(SHARED_DATA_FILE)
        self.shared_data_as_dict = json.loads(self.shared_data)
        self.new_posts = self._load_shared_data(POSTS_FILE)

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
        shared_data = extract_shared_data(self.response)
        self.assertTrue(isinstance(shared_data, dict))
        self.assertTrue('entry_data' in shared_data)

    def test_shared_data_content(self):
        POSTS_NUMBER_ON_MAIN_PAGE = 24
        shared_data_as_dict = json.loads(self.shared_data)
        post_objects = get_post_objects(shared_data_as_dict)
        self.assertEqual(len(post_objects), POSTS_NUMBER_ON_MAIN_PAGE)
        self.assertDictEqual(json.loads(self.new_posts)[0], post_objects[0])

    def test_get_owner_id_list_from_post_list(self):
        EXPECTED_OWNERS = [
            '2085484199', '1231966111', '1417245904', '284839646', '802691449', '530212866',
            '329049773', '2137751105', '3014124104', '2773941655', '1497292555', '651318403',
            '1440226781', '558521835', '1356489834', '1442815924', '4797965638', '6231474342',
            '1967565848', '5544970385', '1175903498', '1410913241', '3688741311', '773536033']
        posts = json.loads(self.new_posts)
        id_list = get_owner_ids_from_posts_list(posts)
        self.assertEqual(EXPECTED_OWNERS, id_list)

    def test_get_last_post_id(self):
        EXPECTED_ID = '1718895412364831673'
        last_post_id = get_last_post_id(self.shared_data_as_dict)
        self.assertEqual(EXPECTED_ID, last_post_id)

    def test_pagination_has_next_page(self):
        EXPECTED = True
        has_next_page = pagination_has_next_page(self.shared_data_as_dict)
        self.assertEqual(EXPECTED, has_next_page)




class TestQueryHashExtractor(unittest.TestCase):

    def setUp(self):
        PAGE_SOURCE = 'source_data/instagram_publications_by_location.html'
        JS_FILE_WITH_QUERYHASH = 'source_data/LocationPageContainer.js'
        self.response = fake_response_from_file(file_name=PAGE_SOURCE)
        self.response_for_js_with_queryhash = fake_response_from_file(file_name=JS_FILE_WITH_QUERYHASH)

    def _load_shared_data(self, file_name):
        if not file_name[0] == '/':
            responses_dir = os.path.dirname(os.path.realpath(__file__))
            file_path = os.path.join(responses_dir, file_name)
        else:
            file_path = file_name
        with open(file_path, 'r') as f:
            file_content = f.read()
            return file_content

    def test_get_link_for_js_file_with_queryhash(self):
        link = get_link_for_js_file_with_queryhash(self.response)
        self.assertTrue(isinstance(link, str))
        self.assertEqual("/static/bundles/LocationPageContainer.js/0a8e5b85842a.js", link)

    def test_get_queryhash_from_js_file(self):
        EXPECTED_QUERYHASH = '951c979213d7e7a1cf1d73e2f661cbd1'
        query_hash = get_queryhash_from_js_file(self.response_for_js_with_queryhash)
        self.assertEqual(EXPECTED_QUERYHASH, query_hash)


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



