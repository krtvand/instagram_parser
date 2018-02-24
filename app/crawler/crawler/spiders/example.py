import re

import scrapy

from app.crawler.crawler.data_extractor import (extract_shared_data,
                                                get_post_objects,
                                                get_owner_ids_from_posts_list)


class ExampleSpider(scrapy.Spider):
    name = 'example'
    # allowed_domains = ['example.com']
    start_urls = ['https://www.instagram.com/explore/locations/224829075/']

    def parse(self, response):
        shared_data = extract_shared_data(response)
        posts_list = get_post_objects(shared_data)
        owner_ids_list = get_owner_ids_from_posts_list(posts_list)
        yield {'owner_ids_list': owner_ids_list}
