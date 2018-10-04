# -*- coding: utf-8 -*-

import scrapy
from scrapy import Request, FormRequest
import re
import json
from urllib import urlencode
from urlparse import urljoin
import logging

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

from instagram_parser.crawler.constants import INSTAGRAM_BASE_URL
from instagram_parser.crawler.data_extractors.concret_extractors import SharedDataExtractorFromBodyScript
from instagram_parser.crawler.utils.headers_manager import PaginationHeadersManager
from instagram_parser.crawler.data_extractors.user_following.user_page_data_extractor import UserPageDataExtractor


class UserFollowingSpider(scrapy.Spider):
    name = 'user_following_spider'

    def __init__(self, username, spider_stopper, result, *args, **kwargs):
        """
        :param spider_stopper: Остановщик парсера
        :param result: Результат работы парсера сохраняем в аргумент, переданный при запуске
        """
        self.username = username
        self.start_urls = ['{}/{}/'.format(INSTAGRAM_BASE_URL, username)]
        self.result = result
        self.spider_stoper = spider_stopper

        super(UserFollowingSpider, self).__init__(*args, **kwargs)

    def login(self, response):
        BASE_URL = 'https://www.instagram.com/'
        LOGIN_URL = BASE_URL + 'accounts/login/ajax/'
        login_data = {'username': '89271805343', 'password': 'i8-9271821473'}
        csrftoken = response.headers.getlist('Set-Cookie')[-1].split(';')[0].split('=')[1]
        headers = {'x-csrftoken': csrftoken}

        return FormRequest(LOGIN_URL, headers=headers, formdata=login_data,
                           callback=self.first_page_following, errback=self.error)



    def error(self, response):
        print('error: {}'.format(response))

    def parse(self, response):
        shared_data = UserPageDataExtractor().get_page_info_from_json(response)
        rhx_gis = UserPageDataExtractor().get_rhx_gis(shared_data)

        query_hash = 'ae21d996d1918b725a934c0ed7f59a74'
        response.request.meta['query_hash'] = query_hash
        variables =  '{"id":"291729641","include_reel":true,"fetch_mutual":false,"first":24}'
        params = urlencode([('query_hash', query_hash), ('variables', variables)])
        next_page_url = urljoin(INSTAGRAM_BASE_URL, '/graphql/query/') + '?' + params

        headers = PaginationHeadersManager(rhx_gis, variables).get_headers()
        return Request(next_page_url, headers=headers, meta={'rhx_gis': rhx_gis},
                       callback=self.login)

    def first_page_following(self, response):
        print(response)
