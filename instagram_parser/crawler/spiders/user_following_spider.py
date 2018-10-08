# -*- coding: utf-8 -*-

from urllib import urlencode
from urlparse import urljoin

import scrapy
from scrapy import Request, FormRequest

from instagram_parser.crawler.constants import INSTAGRAM_BASE_URL, STORIES_UA, LOGIN_URL
from instagram_parser.crawler.data_extractors.user_following.user_page_data_extractor import \
    UserPageDataExtractor
from instagram_parser.crawler.utils.headers_manager import PaginationHeadersManager


class UserFollowingSpider(scrapy.Spider):
    name = 'user_following_spider'

    def __init__(self, username, spider_stopper, result, *args, **kwargs):
        """
        :param spider_stopper: Остановщик парсера
        :param result: Результат работы парсера сохраняем в аргумент, переданный при запуске
        """
        self.username = username
        self.start_urls = [INSTAGRAM_BASE_URL]
        self.result = result
        self.spider_stoper = spider_stopper

        super(UserFollowingSpider, self).__init__(*args, **kwargs)


    def parse(self, response):
        shared_data = UserPageDataExtractor().get_page_info_from_json(response)
        response.request.meta['rhx_gis'] = UserPageDataExtractor().get_rhx_gis(shared_data)

        login_data = {'username': '89271805343', 'password': 'i8-9271821473'}
        csrftoken = response.headers.getlist('Set-Cookie')[-1].split(';')[0].split('=')[1]

        headers = {
            'Referer': INSTAGRAM_BASE_URL,
            'user-agent': STORIES_UA,
            'X-CSRFToken': csrftoken
        }

        return FormRequest(LOGIN_URL, headers=headers, formdata=login_data,
                           meta=response.request.meta, callback=self.after_login,
                           errback=self.error)


    def after_login(self, response):
        variables = '{"id":"291729641","include_reel":true,"fetch_mutual":false,"first":24}'
        params = urlencode([('query_hash', 'ae21d996d1918b725a934c0ed7f59a74'), ('variables', variables)])
        next_page_url = urljoin(INSTAGRAM_BASE_URL, '/graphql/query/') + '?' + params

        headers = PaginationHeadersManager(response.request.meta['rhx_gis'], variables).get_headers()

        return Request(next_page_url, headers=headers, meta=response.request.meta,
                       callback=self.first_page_following, errback=self.error)



    def error(self, response):
        print('error: {}'.format(response))



    def first_page_following(self, response):
       print(response)