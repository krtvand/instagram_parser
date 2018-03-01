import scrapy
from scrapy import Request

from instagram_parser.crawler.crawler.pagination import (PaginatorInFirstPage,)
from instagram_parser.crawler.crawler.data_extractor import (FirstPageParser)


class ExampleSpider(scrapy.Spider):
    name = 'example'
    location_id = '224829075'
    base_url = 'https://www.instagram.com'
    pagination_url = '/graphql/query/'
    start_urls = ['{}/explore/locations/{}/'.format(base_url, location_id)]
    index_page_parser = FirstPageParser()
    index_page_paginator = PaginatorInFirstPage(base_url, location_id)

    def parse(self, response):
        posts_info = []
        shared_data = self.index_page_parser.extract_shared_data(response)
        posts_list = self.index_page_parser.get_post_objects(shared_data)
        for post in posts_list:
            posts_info.append(self.index_page_parser.collect_data_from_post(post))

        # pagination
        if self.index_page_paginator.pagination_has_next_page(shared_data):
            next_page_url = self.index_page_paginator.get_url_for_next_page(response, shared_data)
            headers = {'x-requested-with': 'XMLHttpRequest'}
            yield Request(next_page_url, headers=headers, meta={'posts_info': posts_info},
                          callback=self.parse_next_page)
        else:
            yield {'posts_info': posts_info}

    def parse_next_page(self, response):
        with open('next_page', 'w') as f:
            f.write(response.text)


        posts_info = response.request.meta['posts_info']
        yield {'posts_info': posts_info}
