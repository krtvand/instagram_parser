# -*- coding: utf-8 -*-

from urllib import urlencode
from urlparse import urljoin
import os.path

import scrapy
from scrapy import Request, FormRequest

from instagram_parser.crawler.constants import INSTAGRAM_BASE_URL, STORIES_UA, LOGIN_URL
from instagram_parser.crawler.data_extractors.user_following.user_page_data_extractor import \
    UserPageDataExtractor
from instagram_parser.crawler.data_extractors.concret_extractors import \
    ResponseIsSharedDataExtractor
from instagram_parser.crawler.utils.headers_manager import PaginationHeadersManager


class UserFollowingSpider(scrapy.Spider):
    """
    Сбор никнеймов, на которых подписан пользователь

    В случае если будет запрошен сбор данных с закрытого аккаунта, парсер вернет пустой результат
    """
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
        # self.start_urls = ['{}{}'.format(INSTAGRAM_BASE_URL, target_username)]
        self.result = result
        self.session_id = ''

        super(UserFollowingSpider, self).__init__(*args, **kwargs)

    def start_requests(self):
        try:
            if os.path.exists('session_id.txt'):
                with open('session_id.txt', 'r') as f:
                    self.session_id = f.readline()
        except Exception as e:
            print('Can not load session_id. Error: {}'.format(e))
        url = '{}{}'.format(INSTAGRAM_BASE_URL, self.username)
        return [Request(url, cookies={'sessionid': self.session_id}, callback=self.parse_user_page,
                        errback=self.error)]

    def parse_user_page(self, response):
        shared_data = UserPageDataExtractor().get_page_info_from_json(response)
        response.request.meta['rhx_gis'] = UserPageDataExtractor().get_rhx_gis(shared_data)
        response.request.meta['user_id'] = shared_data.get('entry_data', {}).get('ProfilePage', [{}])[0].get('graphql', {}).get('user', {}).get('id')
        user_logged_in = shared_data.get('activity_counts')

        login_data = {'username': self.login, 'password': self.password}
        csrftoken = response.headers.getlist('Set-Cookie')[-1].split(';')[0].split('=')[1]

        headers = {
            'Referer': INSTAGRAM_BASE_URL,
            'user-agent': STORIES_UA,
            'X-CSRFToken': csrftoken
        }

        if user_logged_in:
            user_id = response.request.meta['user_id']
            variables = '{{"id":"{user_id}","include_reel":true,"fetch_mutual":false,"first":12}}'.format(user_id=user_id)
            params = urlencode([('query_hash', 'c56ee0ae1f89cdbd1c89e2bc6b8f3d18'), ('variables', variables)])
            next_page_url = urljoin(INSTAGRAM_BASE_URL, '/graphql/query/') + '?' + params
            headers = PaginationHeadersManager(response.request.meta['rhx_gis'],
                                               variables).get_headers()
            return Request(next_page_url, headers=headers,
                           meta=response.request.meta, callback=self.parse_user_following,
                           errback=self.error)

        return FormRequest(LOGIN_URL, headers=headers, formdata=login_data,
                           meta=response.request.meta, callback=self.after_login,
                           errback=self.error)


    def after_login(self, response):
        user_id = response.request.meta['user_id']
        variables = '{{"id":"{user_id}","include_reel":true,"fetch_mutual":false,"first":12}}'.format(user_id=user_id)
        params = urlencode([('query_hash', 'c56ee0ae1f89cdbd1c89e2bc6b8f3d18'), ('variables', variables)])
        next_page_url = urljoin(INSTAGRAM_BASE_URL, '/graphql/query/') + '?' + params
        headers = PaginationHeadersManager(response.request.meta['rhx_gis'], variables).get_headers()

        session_id = response.headers.getlist('Set-Cookie')[-1].split(';')[0].split('=')[1]
        with open('session_id.txt', 'w') as f:
            f.write(session_id)

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
            user_id = response.request.meta['user_id']
            variables = '{{"id":"{user_id}","include_reel":true,"fetch_mutual":false,"first":48,"after":"{end_cursor}"}}'.format(user_id=user_id, end_cursor=end_cursor)
            params = urlencode(
                [('query_hash', 'c56ee0ae1f89cdbd1c89e2bc6b8f3d18'), ('variables', variables)])
            next_page_url = urljoin(INSTAGRAM_BASE_URL, '/graphql/query/') + '?' + params

            headers = PaginationHeadersManager(response.request.meta['rhx_gis'],
                                               variables).get_headers()
            return Request(next_page_url, headers=headers, meta=response.request.meta,
                           callback=self.parse_user_following, errback=self.error)

