# -*- coding: utf-8 -*-

#TODO 429 http error - to many requests

import scrapy
from scrapy import Request

from instagram_parser.crawler.utils.pagination import (PaginatorInFirstPage, PaginatorInNextPage)
from instagram_parser.crawler.data_extractors.publications_by_location.next_page_data_extractor import PublicationsByLocationNextPageDataExtractor
from instagram_parser.crawler.data_extractors.publications_by_location.first_page_data_extractor import FirstPageDataExtractor
from instagram_parser.crawler.data_extractors.post_detail_page_data_extractor import PostDetailPageDataExtractor


QUERY_LOCATION_VARS = '{{"id":"{0}","first":12,"after":"{1}"}}'


class InstagramPostsSpider(scrapy.Spider):
    name = 'instagram_posts_spider'
    base_url = 'https://www.instagram.com'

    def __init__(self, location_id, spider_stopper, posts_filter,
                 result, *args, **kwargs):
        """
        :param spider_stopper: Остановщик парсера
        :param posts_filter: Фильтровщик постов (например по дате публикации)
        :param result: Результат работы парсера сохраняем в аргумент, переданный при запуске
        """
        self.location_id = location_id
        self.start_urls = ['{}/explore/locations/{}/'.format(self.base_url, self.location_id)]
        self.posts_info = result
        self.spider_stoper = spider_stopper
        self.post_filter = posts_filter
        self.paginator = None
        self.page_parser = None
        self.rhx_gis = None

        super(InstagramPostsSpider, self).__init__(*args, **kwargs)

    def set_paginator(self, paginator_type):
        paginators = {
            'index_page_paginator': PaginatorInFirstPage(self.base_url, self.location_id),
            'next_page_paginator': PaginatorInNextPage(self.base_url, self.location_id)
        }
        self.paginator = paginators[paginator_type]

    def set_page_parser(self, parser_type):
        parsers = {
            'index_page_parser': FirstPageDataExtractor(),
            'next_page_parser': PublicationsByLocationNextPageDataExtractor()
        }
        self.page_parser = parsers[parser_type]

    def parse(self, response):
        self.set_paginator('index_page_paginator')
        self.set_page_parser('index_page_parser')
        shared_data = self.page_parser.get_page_info_from_json(response)
        posts_list = self.page_parser.get_post_objects(shared_data)
        for post in posts_list:
            post_data = self.page_parser.collect_data_from_post(post)
            (post_id, post_info), = post_data.items()
            if self.spider_stoper.should_we_stop_spider(publication_date_in_epoch=post_info['publication_date'],
                                                        items=self.posts_info):
                return
            if self.post_filter.must_be_discarded(post_data):
                continue
            self.posts_info.update(post_data)
            headers = {'x-requested-with': 'XMLHttpRequest'}

            yield Request(url='{}/p/{}/?__a=1'.format(self.base_url, post_info['shortcode']),
                          headers=headers, callback=self.parse_post_detail_page, meta={'download_timeout': 0})

        if self.paginator.pagination_has_next_page(shared_data):
            next_page_url = self.paginator.get_url_for_next_page(response, shared_data)
            headers = self.paginator.get_headers(shared_data)
            self.rhx_gis = shared_data['rhx_gis']
            meta = response.request.meta
            yield Request(next_page_url, headers=headers, meta=meta, callback=self.parse_next_page)
        else:
            return

    def parse_next_page(self, response):
        self.set_paginator('next_page_paginator')
        self.set_page_parser('next_page_parser')
        shared_data = self.page_parser.get_page_info_from_json(response)
        posts_list = self.page_parser.get_post_objects(shared_data)
        for post in posts_list:
            post_data = self.page_parser.collect_data_from_post(post)
            (post_id, post_info), = post_data.items()
            if self.spider_stoper.should_we_stop_spider(
                    publication_date_in_epoch=post_info['publication_date'],
                    items=self.posts_info):
                return
            if self.post_filter.must_be_discarded(post_data):
                continue
            self.posts_info.update(post_data)
            headers = {'x-requested-with': 'XMLHttpRequest'}

            yield Request(url='{}/p/{}/?__a=1'.format(self.base_url, post_info['shortcode']),
                          headers=headers, callback=self.parse_post_detail_page,
                          meta={'download_timeout': 0})

        if self.paginator.pagination_has_next_page(shared_data):
            next_page_url = self.paginator.get_url_for_next_page(response, shared_data)
            headers = self.paginator.get_headers(shared_data, self.rhx_gis)
            meta = response.request.meta
            yield Request(next_page_url, headers=headers, meta=meta, callback=self.parse_next_page)
        else:
            return

    def parse_post_detail_page(self, response):
        """
        Парсинг информации со страницы с детальной информацией о посте
        """
        parser = PostDetailPageDataExtractor()
        page_data = parser.get_page_data_as_dict(response)
        post_data = parser.collect_data_from_post(page_data)
        (post_id, post_info), = post_data.items()
        self.posts_info[post_id].update(post_info)
