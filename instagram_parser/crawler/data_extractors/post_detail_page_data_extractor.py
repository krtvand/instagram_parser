# -*- coding: utf-8 -*-

import json

from instagram_parser.crawler.data_extractors.concret_extractors import (
    SharedDataExtractorFromBodyScript,
    PublicationsByLocationIndexPagePostsListExtractor,
    PostDetailPagePostDataExtractor
)
from instagram_parser.crawler.data_extractors.first_page_data_extractor import DataExtractorException
from instagram_parser.crawler.data_extractors.first_page_data_extractor import PublicationsPageDataExtractor

class PostDetailPageDataExtractor(PublicationsPageDataExtractor):

    def set_concret_extractors(self):
        # self.shared_data_extractor = SharedDataExtractorFromBodyScript()
        # self.posts_list_extractor = PublicationsByLocationIndexPagePostsListExtractor()
        self.post_data_extractor = PostDetailPagePostDataExtractor()

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
