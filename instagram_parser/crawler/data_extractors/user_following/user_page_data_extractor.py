# -*- coding: utf-8 -*-

from instagram_parser.crawler.data_extractors.concret_extractors import (
    SharedDataExtractorFromBodyScript
)


class UserPageDataExtractor(object):
    """
    Парсинг главной страницы пользователя
    """
    def __init__(self):
        self.shared_data_extractor = SharedDataExtractorFromBodyScript()

    def get_page_info_from_json(self, response):
        """Получаем shared_data как dict

        shared_data - это json объект из исходного кода страницы, который содержит всю
        информацию о постах, пагинации и т.д.
        """
        return self.shared_data_extractor.get_page_info_from_json(response)

    def get_rhx_gis(self, shared_data):
        return shared_data.get('rhx_gis')
#     def
