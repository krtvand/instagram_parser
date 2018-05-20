# -*- coding: utf-8 -*-

from instagram_parser.crawler.data_extractors.concret_extractors import (
    SharedDataExtractorFromBodyScript,
    PublicationsByLocationIndexPagePostsListExtractor,
    PublicationsByLocationPostDataExtractor
)

from instagram_parser.crawler.data_extractors.base import (PublicationsPageDataExtractor)


class FirstPageDataExtractor(PublicationsPageDataExtractor):
    """
    Парсинг индексной (первой) страницы с постами
    """

    def set_concret_extractors(self):
        self.shared_data_extractor = SharedDataExtractorFromBodyScript()
        self.posts_list_extractor = PublicationsByLocationIndexPagePostsListExtractor()
        self.post_data_extractor = PublicationsByLocationPostDataExtractor()
