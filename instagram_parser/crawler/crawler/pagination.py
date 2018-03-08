import re
import json
from urllib.parse import urlencode, urljoin
from collections import OrderedDict

import requests
import scrapy

class PaginationException(Exception):
    """
    Ошибки пагинации
    """

class Paginator:
    """
    Пагинация
    """
    pagination_url = '/graphql/query/'

    def __init__(self, base_url, location_id):
        self.base_url = base_url
        self.location_id = location_id

    def get_last_post_id(self, shared_data: dict) -> str:
        """
        Получение id последнего поста на текущей странице, для того, чтобы сформировать
        запрос на следующую страниццу в пагинации
        """
        raise NotImplementedError

    def pagination_has_next_page(self, shared_data: dict) -> bool:
        """
        Проверка пагинации на предмет наличия следующей страницы
        """
        raise NotImplementedError

    def get_url_for_next_page(self, response: scrapy.http.Response,
                              shared_data: dict) -> scrapy.http.Request:
        if 'query_hash' not in response.request.meta:
            query_hash = self.get_query_hash(response)
            response.request.meta['query_hash'] = query_hash
        else:
            query_hash = response.request.meta['query_hash']
        after = self.get_last_post_id(shared_data)
        params_as_dict = OrderedDict([("id", self.location_id), ("first", 12), ("after", after)])
        variables = json.dumps(params_as_dict).replace(' ', '')
        params = urlencode([('query_hash', query_hash), ('variables', variables)])
        url = urljoin(self.base_url, self.pagination_url) + '?' + params

        return url

    def get_query_hash(self, response: scrapy.http.Response):
        """
        :param response: индексная страница для постов в заданной локации
        :return:
        """
        js_relative_url = self.get_link_for_js_file_with_queryhash(response)
        js_with_query_hash = requests.get(urljoin(self.base_url, js_relative_url))
        query_hash = self.get_queryhash_from_js_source(js_with_query_hash.text)

        return query_hash

    def get_link_for_js_file_with_queryhash(self, response: scrapy.http.Response):
        link = response.xpath(
            '//link[contains(@href, "/static/bundles/LocationPageContainer.js")]/@href').extract_first()

        return link

    def get_queryhash_from_js_source(self, page_source: str):
        # TODO Заглушка. убрать.
        query_hash = '951c979213d7e7a1cf1d73e2f661cbd1'
        return query_hash
        pattern = r'(?P<text_before>locationPosts\.byLocationId\.get\(e\)\.pagination},queryId:\")(?P<query_hash>.*?)(\",queryParams)'
        match = re.match(pattern, page_source)
        if match:
            query_hash = match.group('query_hash')
        else:
            with open('debug', 'w') as f:
                f.write(page_source)
            raise PaginationException('Can not extract query_hash from js_source')
        return query_hash


class PaginatorInFirstPage(Paginator):

    def get_last_post_id(self, shared_data: dict) -> str:
        try:
            last_post_id = shared_data.get('entry_data', {}).get('LocationsPage', )[0].get(
                'location', {}).get('media', {}).get('page_info', {}).get('end_cursor')
            if not last_post_id:
                raise Exception
        except Exception:
            raise PaginationException('Can not get last post id (end_cursor) from shared_data')
        return last_post_id

    def pagination_has_next_page(self, shared_data: dict) -> bool:
        try:
            pagination_has_next_page = shared_data.get('entry_data', {}).get('LocationsPage', )[
                0].get('location', {}).get('media', {}).get('page_info', {}).get('has_next_page')
            if pagination_has_next_page is None:
                raise Exception
        except Exception:
            raise PaginationException(
                'Can not get value for next_has_page attribute from shared_data')
        return pagination_has_next_page


class PaginatorInNextPage(Paginator):

    def get_last_post_id(self, shared_data: dict) -> str:
        try:
            last_post_id = shared_data.get('data', {}).get('location', {}).get(
                'edge_location_to_media', {}).get('page_info', {}).get('end_cursor')
            if not last_post_id:
                raise Exception
        except Exception:
            raise PaginationException('Can not get last post id (end_cursor) from shared_data')
        return last_post_id

    def pagination_has_next_page(self, shared_data: dict) -> bool:
        try:
            pagination_has_next_page = shared_data.get('data', {}).get('location', {}).get(
                'edge_location_to_media', {}).get('page_info', {}).get('has_next_page')
            if pagination_has_next_page is None:
                raise Exception
        except Exception:
            raise PaginationException(
                'Can not get value for next_has_page attribute from shared_data')
        return pagination_has_next_page