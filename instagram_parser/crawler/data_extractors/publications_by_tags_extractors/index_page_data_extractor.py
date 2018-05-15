# -*- coding: utf-8 -*-

import re
import json

from instagram_parser.crawler.data_extractors.concret_extractors import (
    SharedDataExtractorFromBodyScript,
    PublicationsByLocationIndexPagePostsListExtractor,
    PublicationsByLocationPostDataExtractor
)
from instagram_parser.crawler.data_extractors.base import (PublicationsPageDataExtractor,
                                                           DataExtractorException)


class IndexPageDataExtractor(PublicationsPageDataExtractor):
    """
    Парсинг индексной (первой) страницы с постами
    """
    def set_concret_extractors(self):
        # self.shared_data_extractor = SharedDataExtractorFromBodyScript()
        # self.posts_list_extractor = PublicationsByLocationIndexPagePostsListExtractor()
        self.post_data_extractor = PublicationsByLocationPostDataExtractor()

    def get_page_info_from_json(self, response):
        """
        Вся информация о публикациях находится в json объекте в исходном коде страницы.
        """
        elem_with_shared_data = response.xpath('//body/script[starts-with(text(), "window._sharedData")]/text()').extract_first()
        shared_data_str = re.sub(r'(.*?)(\{.*\})(.*)', r'\2', elem_with_shared_data)
        shared_data_dict = json.loads(shared_data_str)

        return shared_data_dict

    def get_post_objects(self, shared_data):
        try:
            posts_list = shared_data.get('entry_data', {}).get('TagPage')[0].get('graphql', {}).\
                get('hashtag', {}).get('edge_hashtag_to_media', {}).get('edges', [])
            if not posts_list:
                raise Exception
        except Exception:
            raise DataExtractorException('Can not get nodes (posts) from shared_data')

        return posts_list