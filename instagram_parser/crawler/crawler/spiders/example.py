import scrapy
from scrapy import Request

from instagram_parser.crawler.crawler.pagination import (PaginatorInFirstPage, PaginatorInNextPage)
from instagram_parser.crawler.crawler.data_extractor import (FirstPageParser, NextPageParser)


class ExampleSpider(scrapy.Spider):
    name = 'example'
    location_id = '224829075'
    base_url = 'https://www.instagram.com'
    start_urls = ['{}/explore/locations/{}/'.format(base_url, location_id)]
    index_page_parser = FirstPageParser()
    next_page_parser = NextPageParser()
    index_page_paginator = PaginatorInFirstPage(base_url, location_id)
    next_page_paginator = PaginatorInNextPage(base_url, location_id)
    posts_info = []

    def parse(self, response):
        shared_data = self.index_page_parser.extract_shared_data(response)
        posts_list = self.index_page_parser.get_post_objects(shared_data)
        for post in posts_list:
            self.posts_info.append(self.index_page_parser.collect_data_from_post(post))

        # pagination
        if self.index_page_paginator.pagination_has_next_page(shared_data):
            next_page_url = self.index_page_paginator.get_url_for_next_page(response, shared_data)
            headers = {'x-requested-with': 'XMLHttpRequest'}
            yield Request(next_page_url, headers=headers, callback=self.parse_next_page)
        else:
            yield {'posts_info': self.posts_info}

    def parse_next_page(self, response):
        shared_data = self.next_page_parser.extract_shared_data(response)
        posts_list = self.next_page_parser.get_post_objects(shared_data)
        for post in posts_list:
            self.posts_info.append(self.next_page_parser.collect_data_from_post(post))

        # pagination
        if self.next_page_paginator.pagination_has_next_page(shared_data):
            next_page_url = self.next_page_paginator.get_url_for_next_page(response, shared_data)
            headers = {'x-requested-with': 'XMLHttpRequest'}
            yield Request(next_page_url, headers=headers, callback=self.end)
        else:
            yield {'posts_info': self.posts_info}

    def end(self, response):
        yield {'posts_info': self.posts_info}

