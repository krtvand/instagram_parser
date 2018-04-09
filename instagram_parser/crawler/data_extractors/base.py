# -*- coding: utf-8 -*-
import datetime

import scrapy


class DataExtractorException(Exception):
    """
    Исключение при проблемах сбора информации со страницы сайта.
    Например не найден необходимый елемент.
    """

class LocationPageDataExtractor(object):
    def get_page_info_from_json(self, response):
        """Получаем shared_data как dict

        shared_data - это json объект из исходного кода страницы, который содержит всю
        информацию о постах, пагинации и т.д.
        """
        raise NotImplementedError

    def get_post_objects(self, shared_data):
        """
        Получение списка словарей с информацией о постах из shared_data объекта
        """
        return []

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
