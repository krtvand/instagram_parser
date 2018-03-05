#TODO 429 http error - to many requests

import scrapy
from scrapy import Request
from scrapy.exceptions import CloseSpider

from instagram_parser.crawler.crawler.pagination import (Paginator, PaginatorInFirstPage, PaginatorInNextPage)
from instagram_parser.crawler.crawler.data_extractor import (FirstPageParser, NextPageParser)
from instagram_parser.crawler.crawler.spider_stopper import SpiderStopper
from instagram_parser.crawler.crawler.post_detail_page_parser import PostDetailPageParser

class ExampleSpider(scrapy.Spider):
    name = 'example'
    location_id = '224829075'
    base_url = 'https://www.instagram.com'
    start_urls = ['{}/explore/locations/{}/'.format(base_url, location_id)]
    index_page_parser = FirstPageParser()
    next_page_parser = NextPageParser()
    next_page_paginator = PaginatorInNextPage(base_url, location_id)
    posts_info = {}
    paginator = None
    page_parser = None

    def __init__(self, spider_stopper: SpiderStopper, *args, **kwargs):
        self.spider_stoper = spider_stopper

        super().__init__(*args, **kwargs)

    def set_paginator(self, paginator_type):
        paginators = {
            'index_page_paginator': PaginatorInFirstPage(self.base_url, self.location_id),
            'next_page_paginator': PaginatorInNextPage(self.base_url, self.location_id)
        }
        self.paginator = paginators[paginator_type]

    def set_page_parser(self, parser_type):
        parsers = {
            'index_page_parser': FirstPageParser(),
            'next_page_parser': NextPageParser()
        }
        self.page_parser = parsers[parser_type]

    def parse(self, response):
        self.set_paginator('index_page_paginator')
        self.set_page_parser('index_page_parser')
        shared_data = self.page_parser.get_page_info_from_json(response)
        posts_list = self.page_parser.get_post_objects(shared_data)
        for post in posts_list:
            post_data = self.page_parser.collect_data_from_post(post)
            self.posts_info.update(post_data)
            headers = {'x-requested-with': 'XMLHttpRequest'}
            (k, v), = post_data.items()
            yield Request(url='{}/p/{}/?__a=1'.format(self.base_url, v['shortcode']),
                          headers=headers, callback=self.parse_post_detail_page)
        if self.spider_stoper.should_we_stop_spider(self.posts_info):
            yield self.posts_info
            raise CloseSpider('Work done!')

        # pagination
        if self.paginator.pagination_has_next_page(shared_data):
            next_page_url = self.paginator.get_url_for_next_page(response, shared_data)
            headers = {'x-requested-with': 'XMLHttpRequest'}
            meta = response.request.meta
            yield Request(next_page_url, headers=headers, meta=meta, callback=self.parse_next_page)
        else:
            yield self.posts_info
            raise CloseSpider('Work done!')

    def parse_next_page(self, response):
        self.set_paginator('next_page_paginator')
        self.set_page_parser('next_page_parser')
        shared_data = self.page_parser.get_page_info_from_json(response)
        posts_list = self.page_parser.get_post_objects(shared_data)
        for post in posts_list:
            post_data = self.page_parser.collect_data_from_post(post)
            self.posts_info.update(post_data)
            headers = {'x-requested-with': 'XMLHttpRequest'}
            (k, v), = post_data.items()
            yield Request(url='{}/p/{}/?__a=1'.format(self.base_url, v['shortcode']),
                          headers=headers, callback=self.parse_post_detail_page)

        if self.spider_stoper.should_we_stop_spider(self.posts_info):
            yield self.posts_info
            raise CloseSpider('Work done!')

        # pagination
        if self.paginator.pagination_has_next_page(shared_data):
            next_page_url = self.paginator.get_url_for_next_page(response, shared_data)
            headers = {'x-requested-with': 'XMLHttpRequest'}
            meta = response.request.meta
            yield Request(next_page_url, headers=headers, meta=meta, callback=self.parse_next_page)
        else:
            yield self.posts_info
            raise CloseSpider('Work done!')

    def parse_post_detail_page(self, response):
        parser = PostDetailPageParser()
        page_data = parser.get_page_data_as_dict(response)
        post_data = parser.collect_data_from_post(page_data)
        (post_id, post_info), = post_data.items()
        self.posts_info[post_id].update(post_info)
