# -*- coding: utf-8 -*-

from instagram_parser.crawler.data_extractors.concret_extractors import (
    ResponseIsSharedDataExtractor,
    PublicationsByLocationNextPagePostsListExtractor,
    PublicationsByLocationPostDataExtractor
)
from instagram_parser.crawler.data_extractors.base import PublicationsPageDataExtractor


class PublicationsByLocationNextPageDataExtractor(PublicationsPageDataExtractor):
    """
    Парсер данных со страницы, полученной после запроса следующей страницы из пагинации
    """
    def set_concret_extractors(self):
        self.shared_data_extractor = ResponseIsSharedDataExtractor()
        self.posts_list_extractor = PublicationsByLocationNextPagePostsListExtractor()
        self.post_data_extractor = PublicationsByLocationPostDataExtractor()
