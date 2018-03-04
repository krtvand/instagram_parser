import json

import scrapy

from instagram_parser.crawler.crawler.data_extractor import DataExtractorException

class PostDetailPageParser:

    def get_page_data_as_dict(self, response: scrapy.http.Response):
        """
        Страница с детальной информацией о посте запрашивается через ajax запрос и в ответ
        приходит чистый json
        """
        page_data_as_dict = json.loads(response.text)
        return page_data_as_dict

    def get_owner_username(self, data: dict):
        username = data.get('graphql', {}).get('shortcode_media', {}).get('owner', {}).get('username')
        if not username:
            raise DataExtractorException('Can not get post id from post')

        return username

    def get_post_id_from_post(self, data: dict) -> str:
        post_id = data.get('id')
        if not post_id:
            raise DataExtractorException('Can not get post id from post detail page')
        return post_id

