# -*- coding: utf-8 -*-

import unittest
from mock import MagicMock
import json

import requests_mock

from instagram_parser.tests.utils import (fake_scrapy_response_from_file,
                                                    load_text_from_file)
from instagram_parser.crawler.paginators.publications_by_tag_paginators import (
    PublicationsByTagPaginatorInFirstPage,
    PublicationsByTagPaginatorInNextPage
)


class TestPublicationsByTagPaginatorInFirstPage(unittest.TestCase):
    tag = 'bostondynamics'
    base_url = 'https://www.instagram.com'

    def setUp(self):
        self.SHARED_DATA_FILE = 'publications_by_tag/source_data/shared_data_from_index_page.json'
        PAGE_SOURCE = 'publications_by_tag/source_data/index_page_source.html'
        JS_FILE_WITH_QUERYHASH = 'publications_by_tag/source_data/TagPageContainer.js'
        self.shared_data = load_text_from_file(self.SHARED_DATA_FILE)
        self.shared_data_as_dict = json.loads(self.shared_data)
        self.response = fake_scrapy_response_from_file(file_name=PAGE_SOURCE)
        self.response_for_js_with_queryhash = fake_scrapy_response_from_file(
            file_name=JS_FILE_WITH_QUERYHASH)
        self.source_of_js_with_queryhash = load_text_from_file(JS_FILE_WITH_QUERYHASH)
        self.response = fake_scrapy_response_from_file(file_name=PAGE_SOURCE)
        self.source_of_js_with_queryhash = load_text_from_file(JS_FILE_WITH_QUERYHASH)
        self.last_post_id = '1718895412364831673'
        self.paginator = PublicationsByTagPaginatorInFirstPage(self.base_url, tag=self.tag)

    @requests_mock.Mocker()
    def test_get_queryhash(self, m):
        m.get('https://www.instagram.com/static/bundles/base/TagPageContainer.js/903e7d59db3f.js',
              text=self.source_of_js_with_queryhash.decode('utf-8'))
        EXPECTED_QUERYHASH = u'ded47faa9a1aaded10161a2ff32abb6b'
        query_hash = self.paginator._get_query_hash(self.response)
        self.assertEqual(EXPECTED_QUERYHASH, query_hash)

    def test_get_url_for_next_page(self):
        self.paginator._get_query_hash = MagicMock(return_value='ded47faa9a1aaded10161a2ff32abb6b')
        self.paginator.get_last_post_id = MagicMock(return_value = self.last_post_id)
        expected_url = 'https://www.instagram.com/graphql/query/?query_hash=ded47faa9a1aaded10161a2ff32abb6b&variables=%7B%22tag_name%22%3A%22bostondynamics%22%2C%22first%22%3A12%2C%22after%22%3A%221718895412364831673%22%7D'
        url = self.paginator.get_url_for_next_page(self.response, self.shared_data_as_dict)
        self.assertEqual(expected_url, url)

    def test_get_link_for_js_file_with_queryhash(self):
        link = self.paginator.get_link_for_js_file_with_queryhash(self.response)
        self.assertTrue(isinstance(link, unicode))
        self.assertEqual("/static/bundles/base/TagPageContainer.js/903e7d59db3f.js", link)

    def test_get_queryhash_from_js_source(self):
        EXPECTED_QUERYHASH = 'ded47faa9a1aaded10161a2ff32abb6b'
        query_hash = self.paginator.get_queryhash_from_js_source(self.source_of_js_with_queryhash)
        self.assertEqual(EXPECTED_QUERYHASH, query_hash)

    def test_get_headers(self):
        rhx_gis = '510a7a8c35c8837193fbc929e20e1824'
        headers = self.paginator.get_headers(self.shared_data_as_dict, rhx_gis)
        expected_headers = {
            'x-requested-with': 'XMLHttpRequest',
            'x-instagram-gis': 'cab019530bc10fdf4dc15270435e98f5'
        }
        self.assertEqual(expected_headers, headers)

    def test_get_last_post_id(self):
        EXPECTED_ID = 'AQAIVeT_WycYs88OUizas0xz0-KsmqZpMh78QkLbwbhGL1RtzTYEPNdq5rxEt9jd4sC0aqr0xWActlBQVAoHgFF5Uy2ej0qTlyOy4_WbvAeWDQ'
        last_post_id = self.paginator.get_last_post_id(self.shared_data_as_dict)
        self.assertEqual(EXPECTED_ID, last_post_id)

    def test_pagination_has_next_page(self):
        EXPECTED = True
        has_next_page = self.paginator.pagination_has_next_page(self.shared_data_as_dict)
        self.assertEqual(EXPECTED, has_next_page)


class TestNextPagePaginator(unittest.TestCase):
    tag = 'bostondynamics'
    base_url = 'https://www.instagram.com'

    def setUp(self):
        self.NEXT_PAGE_SOURCE = 'publications_by_tag/source_data/next_page_data.json'
        self.paginator = PublicationsByTagPaginatorInNextPage(self.base_url, self.tag)
        self.shared_data = load_text_from_file(self.NEXT_PAGE_SOURCE)
        self.shared_data_as_dict = json.loads(self.shared_data)

    def test_get_headers(self):
        rhx_gis = '510a7a8c35c8837193fbc929e20e1824'
        headers = self.paginator.get_headers(self.shared_data_as_dict, rhx_gis)
        expected_headers = {
            'x-requested-with': 'XMLHttpRequest',
            'x-instagram-gis': '472c0cc7ec30913268a6b40216d8f494'
        }
        self.assertEqual(expected_headers, headers)

    def test_get_last_post_id(self):
        EXPECTED_ID = 'AQCHa2TvKcDEaI5vyQ_ihlF2NdG7sYdJTFKzFOmhUlSxVt6d_HTsCc9QqvFyjxKGryklmxkZkaQx_EcxO9mgbhQbDXD5TS5f9p5nT4e9Bph7lg'
        last_post_id = self.paginator.get_last_post_id(self.shared_data_as_dict)
        self.assertEqual(EXPECTED_ID, last_post_id)

    def test_pagination_has_next_page(self):
        EXPECTED = True
        has_next_page = self.paginator.pagination_has_next_page(self.shared_data_as_dict)
        self.assertEqual(EXPECTED, has_next_page)