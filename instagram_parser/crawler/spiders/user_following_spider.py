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


class UserFollowingSpider(scrapy.Spider):
    name = 'user_following_spider'
    base_url = 'https://www.instagram.com'

    def __init__(self, user_name, result, *args, **kwargs):
        """
        :param result: Результат работы парсера сохраняем в аргумент, переданный при запуске
        """
        self.user_name = user_name
        self.start_urls = ['{}/{}/'.format(self.base_url, self.user_name)]
        self.posts_info = result

        super(UserFollowingSpider, self).__init__(*args, **kwargs)

    def parse(self, response):
        page_parser = UserFollowingIndexPageParser(tag=self.user_name,
                                                       spider_stopper=self.spider_stoper,
                                                       posts_filter=self.post_filter,
                                                       result=self.posts_info,
                                                       detail_page_parser=self.parse_post_detail_page,
                                                       next_page_parser=self.parse_next_page,
                                                       base_url=self.base_url)
        return page_parser.parse(response)

    def parse_next_page(self, response):
        page_parser = UserFollowingNextPageParser(tag=self.user_name,
                                                      spider_stopper=self.spider_stoper,
                                                      posts_filter=self.post_filter,
                                                      result=self.posts_info,
                                                      detail_page_parser=self.parse_post_detail_page,
                                                      next_page_parser=self.parse_next_page,
                                                      base_url=self.base_url)
        return page_parser.parse(response)




class UserFollowingIndexPageParser(IndexPageParser):

    def __init__(self, tag, *args, **kwargs):
        self.tag = tag
        super(UserFollowingIndexPageParser, self).__init__(*args, **kwargs)

    def get_paginator(self):
        return PublicationsByTagPaginatorInFirstPage(self.base_url, self.tag)

    def get_page_data_extractor(self):
        return IndexPageDataExtractor()


class UserFollowingNextPageParser(NextPageParser):

    def __init__(self, tag, *args, **kwargs):
        self.tag = tag
        super(UserFollowingNextPageParser, self).__init__(*args, **kwargs)

    def get_paginator(self):
        return PublicationsByTagPaginatorInNextPage(self.base_url, self.tag)

    def get_page_data_extractor(self):
        return PublicationsByTagNextPageDataExtractor()
