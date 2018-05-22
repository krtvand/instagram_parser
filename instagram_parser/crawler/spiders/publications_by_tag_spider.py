# -*- coding: utf-8 -*-

#TODO 429 http error - to many requests

import scrapy
from scrapy import Request

from instagram_parser.crawler.utils.pagination import (PublicationsByTagPaginatorInFirstPage, PublicationsByTagPaginatorInNextPage)
from instagram_parser.crawler.data_extractors.publications_by_tags_extractors.next_page_data_extractor import PublicationsByTagNextPageDataExtractor
from instagram_parser.crawler.data_extractors.publications_by_tags_extractors.index_page_data_extractor import IndexPageDataExtractor
from instagram_parser.crawler.data_extractors.post_detail_page_data_extractor import PostDetailPageDataExtractor


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
        self.paginator = None
        self.page_parser = None
        self.rhx_gis = None

        super(PublicationsByTagSpider, self).__init__(*args, **kwargs)

    def set_paginator(self, paginator_type):
        paginators = {
            'index_page_paginator': PublicationsByTagPaginatorInFirstPage(self.base_url, self.tag),
            'next_page_paginator': PublicationsByTagPaginatorInNextPage(self.base_url, self.tag)
        }
        self.paginator = paginators[paginator_type]

    def set_page_parser(self, parser_type):
        parsers = {
            'index_page_parser': IndexPageDataExtractor(),
            'next_page_parser': PublicationsByTagNextPageDataExtractor()
        }
        self.page_parser = parsers[parser_type]

    def parse(self, response):
        parser = IndexPageParser(tag=self.tag,
                                 spider_stopper=self.spider_stoper,
                                 posts_filter=self.post_filter,
                                 result=self.posts_info,
                                 detail_page_parser=self.parse_post_detail_page,
                                 next_page_parser=self.parse_next_page,
                                 base_url=self.base_url)
        return parser.parse(response)

        # for p in parser.parse(response):
        #     self.posts_info.update(p)
        # self.set_paginator('index_page_paginator')
        # self.set_page_parser('index_page_parser')
        # shared_data = self.page_parser.get_page_info_from_json(response)
        # posts_list = self.page_parser.get_post_objects(shared_data)
        # for post in posts_list:
        #     post_data = self.page_parser.collect_data_from_post(post)
        #     (post_id, post_info), = post_data.items()
        #     if self.spider_stoper.should_we_stop_spider(publication_date_in_epoch=post_info['publication_date'],
        #                                                 items=self.posts_info):
        #         return
        #     if self.post_filter.must_be_discarded(post_data):
        #         continue
        #     self.posts_info.update(post_data)
        #     headers = {'x-requested-with': 'XMLHttpRequest'}
        #
        #     yield Request(url='{}/p/{}/?__a=1'.format(self.base_url, post_info['shortcode']),
        #                   headers=headers, callback=self.parse_post_detail_page, meta={'download_timeout': 0})
        #
        # if self.paginator.pagination_has_next_page(shared_data):
        #     next_page_url = self.paginator.get_url_for_next_page(response, shared_data)
        #     headers = self.paginator.get_headers(shared_data)
        #     self.rhx_gis = shared_data['rhx_gis']
        #     meta = response.request.meta
        #     yield Request(next_page_url, headers=headers, meta=meta, callback=self.parse_next_page)
        # else:
        #     yield return

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
                          headers=headers, callback=self.parse_post_detail_page)

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


class PageParser(object):

    def __init__(self, tag, spider_stopper, posts_filter,
                 result, detail_page_parser, next_page_parser, base_url, *args, **kwargs):
        """
        :param spider_stopper: Остановщик парсера
        :param posts_filter: Фильтровщик постов (например по дате публикации)
        :param result: Результат работы парсера сохраняем в аргумент, переданный при запуске
        """
        self.detail_page_parser = detail_page_parser
        self.next_page_parser = next_page_parser
        self.tag = tag
        self.base_url = base_url
        self.start_urls = ['{}/explore/tags/{}/'.format(self.base_url, self.tag)]
        self.posts_info = result
        self.spider_stoper = spider_stopper
        self.post_filter = posts_filter
        self.paginator = self.get_paginator()
        self.page_data_extractor = self.get_page_data_extractor()
        self.shared_data = None

    def get_paginator(self):
        raise NotImplementedError

    def get_page_data_extractor(self):
        raise NotImplementedError

    def parse(self, response):
        self.shared_data = self.page_data_extractor.get_page_info_from_json(response)
        posts_list = self.page_data_extractor.get_post_objects(self.shared_data)

        for post in posts_list:
            post_data = self.page_data_extractor.collect_data_from_post(post)
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
                          headers=headers, callback=self.detail_page_parser,
                          meta=response.request.meta)

        yield self.go_to_next_page(response, self.shared_data, self.next_page_parser)

    def go_to_next_page(self, response, shared_data, next_page_parser):
        if self.paginator.pagination_has_next_page(shared_data):
            next_page_url = self.paginator.get_url_for_next_page(response, shared_data)
            rhx_gis = self.get_rhx_gis()
            self.set_rhx_gis_to_request_meta(response.request.meta)
            headers = self.paginator.get_headers(shared_data, rhx_gis)
            yield Request(next_page_url, headers=headers, meta=response.request.meta,
                          callback=next_page_parser)
        else:
            return

    def set_rhx_gis_to_request_meta(self, request_meta):
        raise NotImplementedError

    def get_rhx_gis(self):
        raise NotImplementedError

    # def next_page_parser(self, response):
    #     raise NotImplementedError


class IndexPageParser(PageParser):
    def get_paginator(self):
        return PublicationsByTagPaginatorInFirstPage(self.base_url, self.tag)

    def get_page_data_extractor(self):
        return IndexPageDataExtractor()

    def set_rhx_gis_to_request_meta(self, request_meta):
        request_meta['rhx_gis'] = self.get_rhx_gis()

    def get_rhx_gis(self):
        return self.page_data_extractor.get_rhx_gis()

    # def go_to_next_page(self, response, shared_data, next_page_parser):
    #     if self.paginator.pagination_has_next_page(shared_data):
    #         next_page_url = self.paginator.get_url_for_next_page(response, shared_data)
    #         rhx_gis = self.get_rhx_gis()
    #         self.set_rhx_gis_to_request_meta(response.request.meta)
    #         headers = self.paginator.get_headers(shared_data, rhx_gis)
    #         yield Request(next_page_url, headers=headers, meta=response.request.meta,
    #                       callback=next_page_parser)
    #     else:
    #         return

    def next_page_parser(self, response):
        raise NotImplementedError


class NextPageParser(PageParser):
    def get_paginator(self):
        return PublicationsByTagPaginatorInNextPage(self.base_url, self.tag)

    def get_page_data_extractor(self):
        return PublicationsByTagNextPageDataExtractor()

    def go_to_next_page(self, response, shared_data, next_page_parser):
        if self.paginator.pagination_has_next_page(shared_data):
            next_page_url = self.paginator.get_url_for_next_page(response, shared_data)
            headers = self.paginator.get_headers(shared_data)
            self.rhx_gis = shared_data['rhx_gis']
            meta = response.request.meta
            yield Request(next_page_url, headers=headers, meta=meta, callback=next_page_parser)
        else:
            return

    def next_page_parser(self, response):
        raise NotImplementedError

class Stop(Exception):
    def __init__(self, result):
        self.result = result