# -*- coding: utf-8 -*-

#TODO 429 http error - to many requests

import scrapy

from instagram_parser.crawler.spiders.base_spider import (
    IndexPageParser,
    NextPageParser,
    PostDetailPageParser
)
from instagram_parser.crawler.paginators.publications_by_location_paginators import (
    PublicationsByLocationPaginatorInFirstPage,
    PublicationsByLocationPaginatorInNextPage
)
from instagram_parser.crawler.data_extractors.publications_by_location.next_page_data_extractor \
    import PublicationsByLocationNextPageDataExtractor
from instagram_parser.crawler.data_extractors.publications_by_location.first_page_data_extractor \
    import FirstPageDataExtractor


class PublicationsByLocationSpider(scrapy.Spider):
    name = 'publications_by_location_spider'
    base_url = 'https://www.instagram.com'

    def __init__(self, location_id, spider_stopper, posts_filter,
                 result, *args, **kwargs):
        """
        :param spider_stopper: Остановщик парсера
        :param posts_filter: Фильтровщик постов (например по дате публикации)
        :param result: Результат работы парсера сохраняем в аргумент, переданный при запуске
        """
        super(PublicationsByLocationSpider, self).__init__(*args, **kwargs)
        self.location_id = location_id
        self.start_urls = ['{}/explore/locations/{}/'.format(self.base_url, self.location_id)]
        self.posts_info = result
        self.spider_stoper = spider_stopper
        self.post_filter = posts_filter

    def parse(self, response):
        page_parser = PublicationsByLocationIndexPageParser(location_id=self.location_id,
                                 spider_stopper=self.spider_stoper,
                                 posts_filter=self.post_filter,
                                 result=self.posts_info,
                                 detail_page_parser=self.parse_post_detail_page,
                                 next_page_parser=self.parse_next_page,
                                 base_url=self.base_url)
        return page_parser.parse(response)

    def parse_next_page(self, response):
        page_parser = PublicationsByLocationNextPageParser(location_id=self.location_id,
                                 spider_stopper=self.spider_stoper,
                                 posts_filter=self.post_filter,
                                 result=self.posts_info,
                                 detail_page_parser=self.parse_post_detail_page,
                                 next_page_parser=self.parse_next_page,
                                 base_url=self.base_url)
        return page_parser.parse(response)

    def parse_post_detail_page(self, response):
        """
        Парсинг информации со страницы с детальной информацией о посте
        """
        page_parser = PostDetailPageParser(result=self.posts_info)
        return page_parser.parse(response)


class PublicationsByLocationIndexPageParser(IndexPageParser):

    def __init__(self, location_id, *args, **kwargs):
        self.location_id = location_id
        super(PublicationsByLocationIndexPageParser, self).__init__(*args, **kwargs)

    def get_paginator(self):
        return PublicationsByLocationPaginatorInFirstPage(self.base_url, self.location_id)

    def get_page_data_extractor(self):
        return FirstPageDataExtractor()


class PublicationsByLocationNextPageParser(NextPageParser):

    def __init__(self, location_id, *args, **kwargs):
        self.location_id = location_id
        super(PublicationsByLocationNextPageParser, self).__init__(*args, **kwargs)

    def get_paginator(self):
        return PublicationsByLocationPaginatorInNextPage(self.base_url, self.location_id)

    def get_page_data_extractor(self):
        return PublicationsByLocationNextPageDataExtractor()