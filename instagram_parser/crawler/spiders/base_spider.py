# -*- coding: utf-8 -*-

from scrapy import Request


class SpiderException(Exception):
    """
    Ошибки парсера
    """


class PageParser(object):

    def __init__(self, spider_stopper, posts_filter,
                 result, detail_page_parser, next_page_parser, base_url, *args, **kwargs):
        """
        :param spider_stopper: Остановщик парсера
        :param posts_filter: Фильтровщик постов (например по дате публикации)
        :param result: Результат работы парсера сохраняем в аргумент, переданный при запуске
        """
        self.detail_page_parser = detail_page_parser
        self.next_page_parser = next_page_parser
        self.base_url = base_url
        self.posts_info = result
        self.spider_stoper = spider_stopper
        self.post_filter = posts_filter
        self.paginator = self.get_paginator()
        self.page_data_extractor = self.get_page_data_extractor()
        self.shared_data = None
        self.response = None

    def get_paginator(self):
        raise NotImplementedError

    def get_page_data_extractor(self):
        raise NotImplementedError

    def parse(self, response):
        self.response = response
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
            return Request(next_page_url, headers=headers, meta=response.request.meta,
                          callback=next_page_parser)
        else:
            return

    def set_rhx_gis_to_request_meta(self, request_meta):
        raise NotImplementedError

    def get_rhx_gis(self):
        raise NotImplementedError


class IndexPageParser(PageParser):

    def set_rhx_gis_to_request_meta(self, request_meta):
        request_meta['rhx_gis'] = self.get_rhx_gis()

    def get_rhx_gis(self):
        return self.page_data_extractor.get_rhx_gis(self.shared_data)


class NextPageParser(PageParser):

    def set_rhx_gis_to_request_meta(self, request_meta):
        """
        На этом этапе у нас уже задана переменная rhx_gis в мета
        """
        pass

    def get_rhx_gis(self):
        rhx_gis = self.response.request.meta.get('rhx_gis')
        if not rhx_gis:
            raise SpiderException('Can not get rhx_gis from response.request in NextPageParser')
        return rhx_gis


