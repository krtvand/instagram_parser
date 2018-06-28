# -*- coding: utf-8 -*-

import re
import json
from urllib import urlencode
from urlparse import urljoin
import logging

import requests

from instagram_parser.crawler.utils.headers_manager import PaginationHeadersManager

class PaginationException(Exception):
    """
    Ошибки пагинации
    """

class Paginator(object):
    """
    Пагинация
    """
    pagination_url = '/graphql/query/'

    def __init__(self, base_url, location_id):
        self.base_url = base_url
        self.location_id = location_id

    def get_last_post_id(self, shared_data):
        """
        Получение id последнего поста на текущей странице, для того, чтобы сформировать
        запрос на следующую страниццу в пагинации
        """
        raise NotImplementedError

    def pagination_has_next_page(self, shared_data):
        """
        Проверка пагинации на предмет наличия следующей страницы
        """
        raise NotImplementedError

    def get_url_for_next_page(self, response, shared_data):
        query_hash = self._get_query_hash(response)
        response.request.meta['query_hash'] = query_hash
        variables = self._get_variables_for_pagination_uri(shared_data)
        params = urlencode([('query_hash', query_hash), ('variables', variables)])
        url = urljoin(self.base_url, self.pagination_url) + '?' + params

        return url

    def get_headers(self, shared_data, rhx_gis):
        variables = self._get_variables_for_pagination_uri(shared_data)
        headers = PaginationHeadersManager(rhx_gis=rhx_gis, pagination_uri_variables=variables).get_headers()
        return headers

    def _get_variables_for_pagination_uri(self, shared_data):
        raise NotImplementedError

    def _get_query_hash(self, response):
        """
        :param response: индексная страница для постов в заданной локации
        :return:
        """
        raise NotImplementedError


class PaginatorInFirstPage(Paginator):

    def _get_query_hash(self, response):
        """
        :param response: индексная страница для постов в заданной локации
        :return:
        """
        try:
            js_relative_url = self.get_link_for_js_file_with_queryhash(response)
            js_with_query_hash = requests.get(urljoin(self.base_url, js_relative_url))
            query_hash = self.get_queryhash_from_js_source(js_with_query_hash.text)
        except PaginationException:
            logging.error('Can not parse query_hash from js source, using default value')
            query_hash = self.get_default_query_hash()

        return query_hash

    def get_link_for_js_file_with_queryhash(self, response):
        raise NotImplementedError

    def get_queryhash_from_js_source(self, page_source):
        pattern = r'(?P<text_before>locationPosts\.byLocationId\.get\(e\)\.pagination},queryId:\")(?P<query_hash>.*?)(\",queryParams)'
        match = re.search(pattern, page_source)
        if match:
            query_hash = match.group('query_hash')
        else:
            raise PaginationException('Can not extract query_hash from js_source')
        return query_hash

    def get_default_query_hash(self):
        raise NotImplementedError


class PaginatorInNextPage(Paginator):

    def _get_query_hash(self, response):
        query_hash = response.request.meta.get('query_hash')
        if not query_hash:
            raise PaginationException('Can not get query_hash from response.request.meta. '
                                      'It should be set in the first page paginator')
        return query_hash
