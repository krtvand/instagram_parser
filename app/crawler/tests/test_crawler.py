import unittest
import os
import re
import json

from scrapy.http import HtmlResponse, Request, Response

from app.crawler.crawler.data_extractor import extract_shared_data, get_post_objects


class TestIndexPageParser(unittest.TestCase):

    def setUp(self):
        PAGE_SOURCE = 'source_data/instagram_publications_by_location.html'
        SHARED_DATA_FILE = 'source_data/shared_data.txt'
        self.response = fake_response_from_file(file_name=PAGE_SOURCE)
        self.shared_data = self._load_shared_data(SHARED_DATA_FILE)

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
        self.assertTrue(isinstance(shared_data, str))
        self.assertIsNotNone(re.match(r'^\{.*\}$', shared_data))
        self.assertTrue(self._is_json(shared_data))

    def _is_json(self, json_obj):
        try:
            json.loads(json_obj)
        except Exception:
            return None
        return True

    def test_shared_data_content(self):
        post_objects = get_post_objects(self.shared_data)
        self.assertTrue(post_objects)

    # def _test_item_results(self, results, expected_length):
    #     count = 0
    #     permalinks = set()
    #     for item in results:
    #         self.assertIsNotNone(item['content'])
    #         self.assertIsNotNone(item['title'])
    #     self.assertEqual(count, expected_length)
    #
    # def test_parse(self):
    #     results = self.spider.parse(fake_response_from_file('osdir/sample.html'))
    #     self._test_item_results(results, 10)


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
    # response.encoding = 'utf-8'
    return response



