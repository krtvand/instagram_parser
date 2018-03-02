import scrapy
from scrapy import Request

from instagram_parser.crawler.crawler.pagination import (Paginator, PaginatorInFirstPage, PaginatorInNextPage)
from instagram_parser.crawler.crawler.data_extractor import (FirstPageParser, NextPageParser)


class ExampleSpider(scrapy.Spider):
    name = 'example'
    location_id = '224829075'
    base_url = 'https://www.instagram.com'
    start_urls = ['{}/explore/locations/{}/'.format(base_url, location_id)]
    index_page_parser = FirstPageParser()
    next_page_parser = NextPageParser()
    next_page_paginator = PaginatorInNextPage(base_url, location_id)
    posts_info = []
    paginator = None
    page_parser = None

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
        shared_data = self.page_parser.extract_shared_data(response)
        posts_list = self.page_parser.get_post_objects(shared_data)
        for post in posts_list:
            self.posts_info.append(self.page_parser.collect_data_from_post(post))

        # pagination
        if self.paginator.pagination_has_next_page(shared_data):
            next_page_url = self.paginator.get_url_for_next_page(response, shared_data)
            headers = {'x-requested-with': 'XMLHttpRequest'}
            meta = response.request.meta
            yield Request(next_page_url, headers=headers, meta=meta, callback=self.parse_next_page)
        else:
            yield {'posts_info': self.posts_info}

    def parse_next_page(self, response):
        self.set_paginator('next_page_paginator')
        self.set_page_parser('next_page_parser')
        shared_data = self.page_parser.extract_shared_data(response)
        posts_list = self.page_parser.get_post_objects(shared_data)
        for post in posts_list:
            self.posts_info.append(self.page_parser.collect_data_from_post(post))

        # pagination
        if self.paginator.pagination_has_next_page(shared_data):
            next_page_url = self.paginator.get_url_for_next_page(response, shared_data)
            headers = {'x-requested-with': 'XMLHttpRequest'}
            meta = response.request.meta
            yield Request(next_page_url, headers=headers, meta=meta, callback=self.end)
        else:
            yield {'posts_info': self.posts_info}

    def end(self, response):
        yield {'posts_info': self.posts_info}

