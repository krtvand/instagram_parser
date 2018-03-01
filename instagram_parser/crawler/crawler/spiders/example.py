from urllib.parse import urlencode, urljoin
import json
from collections import OrderedDict

import scrapy
from scrapy import Request
import requests

from instagram_parser.crawler.crawler.data_extractor import (get_post_objects,
                                                             get_owner_ids_from_posts_list,
                                                             get_last_post_id,
                                                             pagination_has_next_page,
                                                             FirstPageParser)
from instagram_parser.crawler.crawler.query_hash_extractor import (get_link_for_js_file_with_queryhash,
                                                                   get_queryhash_from_js_source)


class ExampleSpider(scrapy.Spider):
    name = 'example'
    location_id = '224829075'
    base_url = 'https://www.instagram.com'
    pagination_url = '/graphql/query/'
    start_urls = ['{}/explore/locations/{}/'.format(base_url, location_id)]
    index_page_parser = FirstPageParser()

    def parse(self, response):
        posts_info = []
        shared_data = self.index_page_parser.extract_shared_data(response)
        posts_list = self.index_page_parser.get_post_objects(shared_data)
        for post in posts_list:
            posts_info.append(self.index_page_parser.collect_data_from_post(post))

        # pagination
        if pagination_has_next_page(shared_data):
            next_page_url = self.get_url_for_next_page(response, shared_data)
            headers = {'x-requested-with': 'XMLHttpRequest'}
            yield Request(next_page_url, headers=headers, meta={'posts_info': posts_info},
                          callback=self.parse_next_page)
        else:
            yield {'posts_info': posts_info}

    def get_url_for_next_page(self, response: scrapy.http.Response, shared_data: dict) -> scrapy.http.Request:
        query_hash = self.get_query_hash(response)
        after = get_last_post_id(shared_data)
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
        js_relative_url = get_link_for_js_file_with_queryhash(response)
        js_with_query_hash = requests.get(urljoin(self.base_url, js_relative_url))
        query_hash = get_queryhash_from_js_source(js_with_query_hash.text)

        return query_hash

    def parse_next_page(self, response):
        with open('next_page', 'w') as f:
            f.write(response.text)


        posts_info = response.request.meta['posts_info']
        yield {'posts_info': posts_info}
