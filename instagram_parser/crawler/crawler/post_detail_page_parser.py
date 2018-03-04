import json

import scrapy

from instagram_parser.crawler.crawler.data_extractor import DataExtractorException

#TODO Унаследоваться от PageParser
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
        post_id = data.get('graphql', {}).get('shortcode_media', {}).get('id')
        if not post_id:
            raise DataExtractorException('Can not get post id from post detail page')
        return post_id

    def get_owner_id_from_post(self, post):
        pass

    def get_shortcode_from_post(self, post):
        pass

    def collect_data_from_post(self, post: dict) -> dict:
        """
        Шаблонный метод для сбора необходимой информации из поста
        """
        result = {}
        post_id = self.get_post_id_from_post(post)
        if post_id:
            result.update({'post_id': post_id})
        owner_id = self.get_owner_id_from_post(post)
        if owner_id:
            result.update({'owner_id': owner_id})
        shortcode = self.get_shortcode_from_post(post)
        if shortcode:
            result.update({'shortcode': shortcode})
        username = self.get_owner_username(post)
        if username:
            result.update({'owner_username': username})

        return result

