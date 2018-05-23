# -*- coding: utf-8 -*-

import unittest
from mock import MagicMock
import json

import requests_mock

from instagram_parser.tests.utils import (fake_scrapy_response_from_file,
                                                    load_text_from_file)
from instagram_parser.crawler.utils.pagination import (PaginatorInFirstPage,
                                                       Paginator,
                                                       PaginatorInNextPage)


class TestPaginatorBase:
    LOCATION_ID = '213526478'
    base_url = 'https://www.instagram.com'
    SHARED_DATA_FILE = 'source_data/shared_data.txt'


class TestPaginator(TestPaginatorBase, unittest.TestCase):

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
        self.paginator = Paginator(self.base_url, location_id=self.LOCATION_ID)

    @requests_mock.Mocker()
    def test_get_queryhash(self, m):
        m.get('https://www.instagram.com/static/bundles/base/LocationPageContainer.js/0a8e5b85842a.js',
              text=self.source_of_js_with_queryhash.decode('utf-8'))
        EXPECTED_QUERYHASH = u'951c979213d7e7a1cf1d73e2f661cbd1'
        query_hash = self.paginator.get_query_hash(self.response)
        self.assertEqual(EXPECTED_QUERYHASH, query_hash)

    def test_get_url_for_next_page(self):
        self.paginator.get_query_hash = MagicMock()
        self.paginator.get_query_hash.return_value = '951c979213d7e7a1cf1d73e2f661cbd1'
        self.paginator.get_last_post_id = MagicMock()
        self.paginator.get_last_post_id.return_value = self.last_post_id
        expected_url = 'https://www.instagram.com/graphql/query/?query_hash=951c979213d7e7a1cf1d73e2f661cbd1&variables=%7B%22id%22%3A%22213526478%22%2C%22first%22%3A12%2C%22after%22%3A%221718895412364831673%22%7D'
        url = self.paginator.get_url_for_next_page(self.response, self.shared_data_as_dict)
        self.assertEqual(expected_url, url)

    def test_get_link_for_js_file_with_queryhash(self):
        link = self.paginator.get_link_for_js_file_with_queryhash(self.response)
        self.assertTrue(isinstance(link, unicode))
        self.assertEqual("/static/bundles/base/LocationPageContainer.js/0a8e5b85842a.js", link)

    def test_get_queryhash_from_js_source(self):
        EXPECTED_QUERYHASH = '951c979213d7e7a1cf1d73e2f661cbd1'
        query_hash = self.paginator.get_queryhash_from_js_source(self.source_of_js_with_queryhash)
        self.assertEqual(EXPECTED_QUERYHASH, query_hash)


class TestFirstPagePaginator(TestPaginatorBase, unittest.TestCase):
    def setUp(self):
        self.paginator = PaginatorInFirstPage(self.base_url, self.LOCATION_ID)
        self.shared_data = load_text_from_file(self.SHARED_DATA_FILE)
        self.shared_data_as_dict = json.loads(self.shared_data)

    def test_get_headers(self):
        rhx_gis = '1ccc3091227dd50beb2f959a13935d0c'
        headers = self.paginator.get_headers(self.shared_data_as_dict, rhx_gis)
        expected_headers = {
            'x-requested-with': 'XMLHttpRequest',
            'x-instagram-gis': '44da33c4e4f2e441da0b845bb0128161'
        }
        self.assertEqual(expected_headers, headers)

    def test_get_last_post_id(self):
        EXPECTED_ID = '1754578475498250894'
        last_post_id = self.paginator.get_last_post_id(self.shared_data_as_dict)
        self.assertEqual(EXPECTED_ID, last_post_id)

    def test_pagination_has_next_page(self):
        EXPECTED = True
        has_next_page = self.paginator.pagination_has_next_page(self.shared_data_as_dict)
        self.assertEqual(EXPECTED, has_next_page)


class TestNextPagePaginator(TestPaginatorBase, unittest.TestCase):

    NEXT_PAGE_SOURCE = 'source_data/instagram_publications_by_location_next_page.json'

    def setUp(self):
        self.paginator = PaginatorInNextPage(self.base_url, self.LOCATION_ID)
        self.shared_data = load_text_from_file(self.NEXT_PAGE_SOURCE)
        self.shared_data_as_dict = json.loads(self.shared_data)

    def test_get_headers(self):
        rhx_gis = '510a7a8c35c8837193fbc929e20e1824'
        headers = self.paginator.get_headers(self.shared_data_as_dict, rhx_gis)
        expected_headers = {
            'x-requested-with': 'XMLHttpRequest',
            'x-instagram-gis': 'ccd2dcb489e1bcf2ace613a28fb124a6'
        }
        self.assertEqual(expected_headers, headers)

    def test_get_last_post_id(self):
        EXPECTED_ID = '1718108885371697130'
        last_post_id = self.paginator.get_last_post_id(self.shared_data_as_dict)
        self.assertEqual(EXPECTED_ID, last_post_id)

    def test_pagination_has_next_page(self):
        EXPECTED = True
        has_next_page = self.paginator.pagination_has_next_page(self.shared_data_as_dict)
        self.assertEqual(EXPECTED, has_next_page)