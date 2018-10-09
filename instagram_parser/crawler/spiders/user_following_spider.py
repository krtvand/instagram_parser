# -*- coding: utf-8 -*-

from urllib import urlencode
from urlparse import urljoin

import scrapy
from scrapy import Request, FormRequest

from instagram_parser.crawler.constants import INSTAGRAM_BASE_URL, STORIES_UA, LOGIN_URL
from instagram_parser.crawler.data_extractors.user_following.user_page_data_extractor import \
    UserPageDataExtractor
from instagram_parser.crawler.data_extractors.concret_extractors import \
    ResponseIsSharedDataExtractor
from instagram_parser.crawler.utils.headers_manager import PaginationHeadersManager


class UserFollowingSpider(scrapy.Spider):
    name = 'user_following_spider'

    def __init__(self, login, password, target_username, result, *args, **kwargs):
        """
        :param login: логин аккаунта, от имени которого будет выполнена авторизация в instagram
        :param password: пароль аккаунта, от имени которого будет выполнена авторизация в instagram
        :param target_username: пользователь instagram, для которого необходимо собрать данные о подписках
        :param spider_stopper: Остановщик парсера
        :param result: Результат работы парсера сохраняем в аргумент, переданный при запуске
        """
        self.login = login
        self.password = password
        self.username = target_username
        self.start_urls = [INSTAGRAM_BASE_URL]
        self.result = result

        super(UserFollowingSpider, self).__init__(*args, **kwargs)


    def parse(self, response):
        shared_data = UserPageDataExtractor().get_page_info_from_json(response)
        response.request.meta['rhx_gis'] = UserPageDataExtractor().get_rhx_gis(shared_data)
        login_data = {'username': self.login, 'password': self.password}
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
        params = urlencode([('query_hash', 'c56ee0ae1f89cdbd1c89e2bc6b8f3d18'), ('variables', variables)])
        next_page_url = urljoin(INSTAGRAM_BASE_URL, '/graphql/query/') + '?' + params

        headers = PaginationHeadersManager(response.request.meta['rhx_gis'], variables).get_headers()

        return Request(next_page_url, headers=headers, meta=response.request.meta,
                       callback=self.parse_user_following, errback=self.error)

    def error(self, response):
        raise Exception('Error in spider')

    def parse_user_following(self, response):
        shared_data = ResponseIsSharedDataExtractor().get_page_info_from_json(response)
        users = shared_data.get('data', {}).get('user', {}). get('edge_follow', {}).get('edges', [])
        followings = {u['node']['id']: {'username': u['node']['username']} for u in users}
        self.result.update(followings)
        has_next_page = shared_data.get('data', {}).get('user', {}).get('edge_follow', {}).get('page_info', {}).get('has_next_page')
        if has_next_page:
            end_cursor = shared_data.get('data', {}).get('user', {}).get('edge_follow', {}).get('page_info', {}).get('end_cursor')
            variables = '{{"id":"291729641","include_reel":true,"fetch_mutual":false,"first":12,"after":"{end_cursor}"}}'.format(end_cursor=end_cursor)
            params = urlencode(
                [('query_hash', 'c56ee0ae1f89cdbd1c89e2bc6b8f3d18'), ('variables', variables)])
            next_page_url = urljoin(INSTAGRAM_BASE_URL, '/graphql/query/') + '?' + params

            headers = PaginationHeadersManager(response.request.meta['rhx_gis'],
                                               variables).get_headers()
            return Request(next_page_url, headers=headers, meta=response.request.meta,
                           callback=self.parse_user_following, errback=self.error)

