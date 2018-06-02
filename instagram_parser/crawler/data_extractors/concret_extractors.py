# -*- coding: utf-8 -*-

import json
import re

from instagram_parser.crawler.data_extractors.exceptions import DataExtractorException


class SharedDataExtractor(object):
    def get_page_info_from_json(self, response):
        raise NotImplementedError

class SharedDataExtractorFromBodyScript(SharedDataExtractor):
    def get_page_info_from_json(self, response):
        """
        Вся информация о публикациях находится в json объекте в исходном коде страницы.
        """
        elem_with_shared_data = response.xpath(
            '//body/script[starts-with(text(), "window._sharedData")]/text()').extract_first()
        shared_data_str = re.sub(r'(.*?)(\{.*\})(.*)', r'\2', elem_with_shared_data)
        shared_data_dict = json.loads(shared_data_str)

        return shared_data_dict

class ResponseIsSharedDataExtractor(SharedDataExtractor):
    def get_page_info_from_json(self, response):
        """
        Следующая страница при пагинации запрашивается через ajax запрос и в ответ
        приходит чистый json
        """
        next_page__data_as_dict = json.loads(response.text)
        return next_page__data_as_dict


class PostsListExtractor(object):
    def get_post_objects(self, shared_data):
        try:
            posts_list = self._fetch_posts(shared_data)
            if not posts_list:
                raise Exception
        except Exception:
            raise DataExtractorException('Can not get nodes (posts) from shared_data')

        return posts_list

    def _fetch_posts(self, shared_data):
        raise NotImplementedError


class PublicationsByLocationIndexPagePostsListExtractor(PostsListExtractor):
    def _fetch_posts(self, shared_data):
        posts_list = shared_data.get('entry_data', {}).get('LocationsPage')[0].get('graphql', {}). \
            get('location', {}).get('edge_location_to_media', {}).get('edges', [])
        return posts_list

class PublicationsByLocationNextPagePostsListExtractor(PostsListExtractor):
    def _fetch_posts(self, shared_data):
        posts_list = shared_data.get('data', {}).get('location', {}).get(
            'edge_location_to_media', {}).get('edges', [])
        return posts_list

class PublicationsByTagIndexPagePostsListExtractor(PostsListExtractor):
    def _fetch_posts(self, shared_data):
        posts_list = shared_data.get('entry_data', {}).get('TagPage')[0].get('graphql', {}). \
            get('hashtag', {}).get('edge_hashtag_to_media', {}).get('edges', [])
        return posts_list

class PublicationsByTagNextPagePostsListExtractor(PostsListExtractor):
    def _fetch_posts(self, shared_data):
        posts_list = shared_data.get('data', {}).get('hashtag', {}). \
            get('edge_hashtag_to_media', {}).get('edges', [])
        return posts_list


class PostDataExtractor(object):
    def collect_data_from_post(self, post):
        """
        Шаблонный метод для сбора необходимой информации из поста
        """
        post_data = {}
        post_id = self.get_post_id_from_post(post)
        if not post_id:
            raise DataExtractorException('Can not get post id')
        owner_id = self.get_owner_id_from_post(post)
        if owner_id:
            post_data.update({'owner_id': owner_id})
        shortcode = self.get_shortcode_from_post(post)
        if shortcode:
            post_data.update({'shortcode': shortcode})
        username = self.get_owner_username(post)
        if username:
            post_data.update({'owner_username': username})
        publication_date = self.get_publication_date(post)
        if publication_date:
            post_data.update({'publication_date': publication_date})
        edge_media_to_caption = self.get_edge_media_to_caption(post)
        if edge_media_to_caption:
            post_data.update({'edge_media_to_caption': edge_media_to_caption})

        result = {post_id: post_data}

        return result

    def get_owner_id_from_post(self, post):
        """
        Id автора поста
        """
        return None

    def get_owner_username(self, data):
        """
        Username автора поста
        """
        return None

    def get_post_id_from_post(self, post):
        """
        Id поста
        """
        return None

    def get_shortcode_from_post(self, post):
        """Уникальный код поста.

        С помощью данного кода можно получить более подробную
        информацию о посте (например ник автора) через отдельный ajax запрос.
        """
        return None

    def get_publication_date(self, post):
        """
        Дата публикации поста
        """

    def get_edge_media_to_caption(self, post):
        """
        Подпись к публикации (заголовок)
        """

class PublicationsByLocationPostDataExtractor(PostDataExtractor):
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


class PostDetailPagePostDataExtractor(PostDataExtractor):
    def get_owner_username(self, data):
        username = data.get('graphql', {}).get('shortcode_media', {}).get('owner', {}).get('username')
        if not username:
            raise DataExtractorException('Can not get post id from post')

        return username

    def get_post_id_from_post(self, data):
        post_id = data.get('graphql', {}).get('shortcode_media', {}).get('id')
        if not post_id:
            raise DataExtractorException('Can not get post id from post detail page')
        return post_id

    def get_edge_media_to_caption(self, post):
        text = None
        try:
            edges = post.get('graphql', {}).get('shortcode_media', {})\
                .get('edge_media_to_caption', {}).get('edges', [{}])
            if edges:
                text = edges[0].get('node', {}).get('text')
        except Exception as e:
            raise DataExtractorException('Can not get edge_media_to_caption '
                                         'from post detail page. {}'.format(e))
        return text
