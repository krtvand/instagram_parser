# -*- coding: utf-8 -*-

#TODO 429 http error - to many requests

import scrapy


from instagram_parser.crawler.spiders.base_spider import (
    IndexPageParser,
    NextPageParser,
    PostDetailPageParser
)
from instagram_parser.crawler.paginators.publications_by_tag_paginators import (
    PublicationsByTagPaginatorInFirstPage,
    PublicationsByTagPaginatorInNextPage
)
from instagram_parser.crawler.data_extractors.publications_by_tags_extractors.next_page_data_extractor \
    import PublicationsByTagNextPageDataExtractor
from instagram_parser.crawler.data_extractors.publications_by_tags_extractors.index_page_data_extractor \
    import IndexPageDataExtractor
from instagram_parser.crawler.data_extractors.post_detail_page_data_extractor import \
    PostDetailPageDataExtractor


class PublicationsByTagSpider(scrapy.Spider):
    name = 'publications_by_tag_spider'
    base_url = 'https://www.instagram.com'

    def __init__(self, tag, spider_stopper, posts_filter,
                 result, *args, **kwargs):
        """
        :param spider_stopper: Остановщик парсера
        :param posts_filter: Фильтровщик постов (например по дате публикации)
        :param result: Результат работы парсера сохраняем в аргумент, переданный при запуске
        """
        self.tag = tag
        self.start_urls = ['{}/explore/tags/{}/'.format(self.base_url, self.tag)]
        self.posts_info = result
        self.spider_stoper = spider_stopper
        self.post_filter = posts_filter

        super(PublicationsByTagSpider, self).__init__(*args, **kwargs)

    def parse(self, response):
        page_parser = PublicationsByTagIndexPageParser(tag=self.tag,
                                 spider_stopper=self.spider_stoper,
                                 posts_filter=self.post_filter,
                                 result=self.posts_info,
                                 detail_page_parser=self.parse_post_detail_page,
                                 next_page_parser=self.parse_next_page,
                                 base_url=self.base_url)
        return page_parser.parse(response)

    def parse_next_page(self, response):
        page_parser = PublicationsByTagNextPageParser(tag=self.tag,
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


class PublicationsByTagIndexPageParser(IndexPageParser):

    def __init__(self, tag, *args, **kwargs):
        self.tag = tag
        super(PublicationsByTagIndexPageParser, self).__init__(*args, **kwargs)

    def get_paginator(self):
        return PublicationsByTagPaginatorInFirstPage(self.base_url, self.tag)

    def get_page_data_extractor(self):
        return IndexPageDataExtractor()


class PublicationsByTagNextPageParser(NextPageParser):

    def __init__(self, tag, *args, **kwargs):
        self.tag = tag
        super(PublicationsByTagNextPageParser, self).__init__(*args, **kwargs)

    def get_paginator(self):
        return PublicationsByTagPaginatorInNextPage(self.base_url, self.tag)

    def get_page_data_extractor(self):
        return PublicationsByTagNextPageDataExtractor()
