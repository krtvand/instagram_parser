import re
import json
import datetime

import scrapy


class DataExtractorException(Exception):
    """
    Исключение при проблемах сбора информации со страницы сайта.
    Например не найден необходимый елемент.
    """

class LocationPageParser:
    def get_page_info_from_json(self, response: scrapy.http.Response) -> dict:
        """Получаем shared_data как dict

        shared_data - это json объект из исходного кода страницы, который содержит всю
        информацию о постах, пагинации и т.д.
        """
        raise NotImplementedError

    def get_post_objects(self, shared_data: dict) -> list:
        """
        Получение списка словарей с информацией о постах из shared_data объекта
        """
        return []

    def collect_data_from_post(self, post: dict) -> dict:
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

    def get_owner_id_from_post(self, post: dict) -> str or None:
        """
        Id автора поста
        """
        return None

    def get_owner_username(self, data: dict) -> str or None:
        """
        Username автора поста
        """
        return None

    def get_post_id_from_post(self, post: dict) -> str or None:
        """
        Id поста
        """
        return None

    def get_shortcode_from_post(self, post: dict) -> str or None:
        """Уникальный код поста.

        С помощью данного кода можно получить более подробную
        информацию о посте (например ник автора) через отдельный ajax запрос.
        """
        return None

    def get_publication_date(self, post: dict) -> datetime.datetime:
        """
        Дата публикации поста
        """


class FirstPageParser(LocationPageParser):
    """
    Парсинг индексной (первой) страницы с постами
    """

    def get_page_info_from_json(self, response: scrapy.http.Response) -> dict:
        """
        Вся информация о публикациях находится в json объекте в исходном коде страницы.
        """
        elem_with_shared_data = response.xpath('//body/script[starts-with(text(), "window._sharedData")]/text()').extract_first()
        shared_data_str = re.sub(r'(.*?)(\{.*\})(.*)', r'\2', elem_with_shared_data)
        shared_data_dict = json.loads(shared_data_str)

        return shared_data_dict

    def get_post_objects(self, shared_data: dict) -> list:
        try:
            posts_list = shared_data.get('entry_data', {}).get('LocationsPage')[0].get('location',
                                                                                       {}).get(
                'media', {}).get('nodes', [])
            if not posts_list:
                raise Exception
        except Exception:
            raise DataExtractorException('Can not get nodes (posts) from shared_data')

        return posts_list

    def get_owner_id_from_post(self, post: dict) -> str:
        owner_id = post.get('owner', {}).get('id')
        if not owner_id:
            raise DataExtractorException('Can not get owner id from post')
        return owner_id

    def get_post_id_from_post(self, post: dict) -> str:
        post_id = post.get('id')
        if not post_id:
            raise DataExtractorException('Can not get post id from post')
        return post_id

    def get_shortcode_from_post(self, post: dict) -> str:
        shortcode = post.get('code')
        if not shortcode:
            raise DataExtractorException('Can not get shortcode from post')
        return shortcode

    def get_publication_date(self, post: dict) -> datetime.datetime:
        publication_date_in_epoch = post.get('date')
        if not publication_date_in_epoch:
            raise DataExtractorException('Can not get publication date from post')
        publication_date = datetime.datetime.utcfromtimestamp(int(publication_date_in_epoch))
        return publication_date

class NextPageParser(LocationPageParser):
    """
    Парсер данных со страницы, полученной после запроса следующей страницы из пагинации
    """
    def get_page_info_from_json(self, response: scrapy.http.Response) -> dict:
        """
        Следующая страница при пагинации запрашивается через ajax запрос и в ответ
        приходит чистый json
        """
        next_page__data_as_dict = json.loads(response.text)

        return next_page__data_as_dict

    def get_post_objects(self, shared_data: dict) -> list:
        try:
            posts_list = shared_data.get('data', {}).get('location', {}).get(
                'edge_location_to_media', {}).get('edges', [])
            if not posts_list:
                raise Exception
        except Exception:
            raise DataExtractorException('Can not get posts from next_page')

        return posts_list

    def get_owner_id_from_post(self, post: dict) -> str:
        owner_id = post.get('node', {}).get('owner', {}).get('id')
        if not owner_id:
            raise DataExtractorException('Can not get owner id from post')
        return owner_id

    def get_post_id_from_post(self, post: dict) -> str:
        post_id = post.get('node', {}).get('id')
        if not post_id:
            raise DataExtractorException('Can not get post id from post')
        return post_id

    def get_shortcode_from_post(self, post: dict) -> str:
        shortcode = post.get('node', {}).get('shortcode')
        if not shortcode:
            raise DataExtractorException('Can not get shortcode from post')
        return shortcode


def get_last_post_id(shared_data: dict) -> str:
    try:
        last_post_id = shared_data.get('entry_data', {}).get('LocationsPage', )[0].get('location', {}).get('media', {}).get('page_info', {}).get('end_cursor')
        if not last_post_id:
            raise Exception
    except Exception:
        raise DataExtractorException('Can not get last post id (end_cursor) from shared_data')
    return last_post_id

def pagination_has_next_page(shared_data: dict) -> bool:
    try:
        pagination_has_next_page = shared_data.get('entry_data', {}).get('LocationsPage', )[0].get('location', {}).get('media', {}).get('page_info', {}).get('has_next_page')
        if pagination_has_next_page is None:
            raise Exception
    except Exception:
        raise DataExtractorException('Can not get value for next_has_page attribute from shared_data')
    return pagination_has_next_page