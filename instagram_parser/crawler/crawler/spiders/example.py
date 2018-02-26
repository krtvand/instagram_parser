from urllib.parse import urlencode, urljoin

import scrapy
from scrapy import Request
import requests

from instagram_parser.crawler.crawler.data_extractor import (extract_shared_data,
                                                             get_post_objects,
                                                             get_owner_ids_from_posts_list,
                                                             get_last_post_id,
                                                             pagination_has_next_page)
from instagram_parser.crawler.crawler.query_hash_extractor import (get_link_for_js_file_with_queryhash,
                                                                   get_queryhash_from_js_source)


class ExampleSpider(scrapy.Spider):
    name = 'example'
    # allowed_domains = ['example.com']
    location_id = '224829075'
    base_url = 'https://www.instagram.com'
    pagination_url = '/graphql/query/'
    start_urls = ['{}/explore/locations/{}/'.format(base_url, location_id)]

    def parse(self, response):
        shared_data = extract_shared_data(response)
        posts_list = get_post_objects(shared_data)
        owner_ids_list = get_owner_ids_from_posts_list(posts_list)

        # pagination
        if pagination_has_next_page(shared_data):
            next_page_url = self.get_url_for_next_page(response, shared_data)
            yield Request(next_page_url, meta={'owner_ids_list': owner_ids_list},
                          callback=self.parse_next_page)
        else:
            yield {'owner_ids_list': owner_ids_list}

    def get_url_for_next_page(self, response: scrapy.http.Response, shared_data: dict) -> scrapy.http.Request:
        query_hash = self.get_query_hash(response)
        after = get_last_post_id(shared_data)
        params = urlencode({'query_hash': query_hash,
                            'variables': {"id": self.location_id, "first": 12, "after": after}})

        return urljoin(self.base_url, self.pagination_url, params)

    def get_query_hash(self, response: scrapy.http.Response):
        """
        :param response: индексная страница для постов в заданной локации
        :return:
        """
        js_relative_url = get_link_for_js_file_with_queryhash(response)
        js_with_query_hash = requests.get(urljoin(self.base_url, js_relative_url))
        query_hash = get_queryhash_from_js_source(js_with_query_hash.text)

        return query_hash

    def parse_next_page(self, response):
        with open('next_page', 'w') as f:
            f.write(response.text)

        yield response.request.meta['owner_ids_list']
