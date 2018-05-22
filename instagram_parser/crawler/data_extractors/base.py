# -*- coding: utf-8 -*-

from instagram_parser.crawler.data_extractors.exceptions import DataExtractorException
from instagram_parser.crawler.data_extractors.concret_extractors import (
    SharedDataExtractor,
    PostsListExtractor,
    PostDataExtractor
)

class PublicationsPageDataExtractor(object):

    def __init__(self):
        self.set_concret_extractors()

    def set_concret_extractors(self):
        # Инициализация только для IDE
        self.shared_data_extractor = SharedDataExtractor()
        self.posts_list_extractor = PostsListExtractor()
        self.post_data_extractor = PostDataExtractor()

    def get_page_info_from_json(self, response):
        """Получаем shared_data как dict

        shared_data - это json объект из исходного кода страницы, который содержит всю
        информацию о постах, пагинации и т.д.
        """
        return self.shared_data_extractor.get_page_info_from_json(response)

    def get_post_objects(self, shared_data):
        """
        Получение списка словарей с информацией о постах из shared_data объекта
        """
        return self.posts_list_extractor.get_post_objects(shared_data)

    def collect_data_from_post(self, post):
        """
        Шаблонный метод для сбора необходимой информации из поста
        """
        return self.post_data_extractor.collect_data_from_post(post)

    def get_rhx_gis(self, shared_data):
        return shared_data.get('rhx_gis')
