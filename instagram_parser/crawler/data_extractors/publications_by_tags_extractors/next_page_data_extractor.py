# -*- coding: utf-8 -*-

import json

from instagram_parser.crawler.data_extractors.concret_extractors import (
    SharedDataExtractorFromBodyScript,
    PublicationsByLocationIndexPagePostsListExtractor,
    PublicationsByLocationPostDataExtractor
)

from instagram_parser.crawler.data_extractors.base import (PublicationsPageDataExtractor,
                                                           DataExtractorException)


class PublicationsByTagNextPageDataExtractor(PublicationsPageDataExtractor):
    """
    Парсер данных со страницы, полученной после запроса следующей страницы из пагинации
    """
    def set_concret_extractors(self):
        # self.shared_data_extractor = SharedDataExtractorFromBodyScript()
        # self.posts_list_extractor = PublicationsByLocationIndexPagePostsListExtractor()
        self.post_data_extractor = PublicationsByLocationPostDataExtractor()

    def get_page_info_from_json(self, response):
        """
        Следующая страница при пагинации запрашивается через ajax запрос и в ответ
        приходит чистый json
        """
        next_page__data_as_dict = json.loads(response.text)

        return next_page__data_as_dict

    def get_post_objects(self, shared_data):
        try:
            posts_list = shared_data.get('data', {}).get('hashtag', {}).\
                get('edge_hashtag_to_media', {}).get('edges', [])
            if not posts_list:
                raise Exception
        except Exception:
            raise DataExtractorException('Can not get posts from next_page')

        return posts_list

    def get_owner_id_from_post(self, post):
        owner_id = post.get('node', {}).get('owner', {}).get('id')
        if not owner_id:
            raise DataExtractorException('Can not get owner id from post')
        return owner_id

    def get_post_id_from_post(self, post):
        post_id = post.get('node', {}).get('id')
        if not post_id:
            raise DataExtractorException('Can not get post id from post')
        return post_id

    def get_shortcode_from_post(self, post):
        shortcode = post.get('node', {}).get('shortcode')
        if not shortcode:
            raise DataExtractorException('Can not get shortcode from post')
        return shortcode

    def get_publication_date(self, post):
        publication_date_in_epoch = post.get('node', {}).get('taken_at_timestamp')
        if not publication_date_in_epoch:
            raise DataExtractorException('Can not get publication date from post')
        return publication_date_in_epoch
