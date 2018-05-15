# -*- coding: utf-8 -*-

from instagram_parser.crawler.data_extractors.concret_extractors import (
    ResponseIsSharedDataExtractor,
    PublicationsByTagNextPagePostsListExtractor,
    PublicationsByLocationPostDataExtractor
)

from instagram_parser.crawler.data_extractors.base import PublicationsPageDataExtractor

class PublicationsByTagNextPageDataExtractor(PublicationsPageDataExtractor):
    """
    Парсер данных со страницы, полученной после запроса следующей страницы из пагинации
    """
    def set_concret_extractors(self):
        self.shared_data_extractor = ResponseIsSharedDataExtractor()
        self.posts_list_extractor = PublicationsByTagNextPagePostsListExtractor()
        self.post_data_extractor = PublicationsByLocationPostDataExtractor()
