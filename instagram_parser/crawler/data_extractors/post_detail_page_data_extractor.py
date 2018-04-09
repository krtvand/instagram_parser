# -*- coding: utf-8 -*-

import json

import scrapy

from instagram_parser.crawler.data_extractors.first_page_data_extractor import DataExtractorException
from instagram_parser.crawler.data_extractors.first_page_data_extractor import LocationPageDataExtractor

class PostDetailPageDataExtractor(LocationPageDataExtractor):

    def get_page_info_from_json(self, response):
        """
        Cтраница детальной информации о посте запрашивается через ajax запрос и в ответ
        приходит чистый json
        """
        post_detail_as_dict = json.loads(response.text)

        return post_detail_as_dict

    def get_page_data_as_dict(self, response):
        """
        Страница с детальной информацией о посте запрашивается через ajax запрос и в ответ
        приходит чистый json
        """
        page_data_as_dict = json.loads(response.text)
        return page_data_as_dict

    def get_owner_username(self, data):
        username = data.get('graphql', {}).get('shortcode_media', {}).get('owner', {}).get('username')
        if not username:
            raise DataExtractorException('Can not get post id from post')

        return username

    def get_post_id_from_post(self, data):
        post_id = data.get('graphql', {}).get('shortcode_media', {}).get('id')
        if not post_id:
            raise DataExtractorException('Can not get post id from post detail page')
        return post_id

    def get_owner_id_from_post(self, post):
        pass

    def get_shortcode_from_post(self, post):
        pass
