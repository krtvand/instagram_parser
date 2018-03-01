import re
import json

import scrapy

class DataExtractorException(Exception):
    """
    Исключение при проблемах сбора информации со страницы сайта.
    Например не найден необходимый елемент.
    """

class LocationPageParser:
    def extract_shared_data(self, response: scrapy.http.Response) -> dict:
        """Получаем shared_data как dict

        shared_data - это json объект из исходного кода страницы, который содержит всю
        информацию о постах, пагинации и т.д.
        """
        raise NotImplementedError

    def get_post_objects(self, shared_data: dict) -> list:
        """
        Получение списка словарей с информацией о постах из shared_data объекта
        """
        raise NotImplementedError

    def collect_data_from_post(self, post: dict) -> dict:
        """
        Шаблонный метод для сбора необходимой информации из поста
        """
        post_id = self.get_post_id_from_post(post)
        owner_id = self.get_owner_id_from_post(post)
        shortcode = self.get_shortcode_from_post(post)
        if not all([post_id, owner_id, shortcode]):
            raise DataExtractorException('Can not get data from post')

        return {'post_id': post_id, 'owner_id': owner_id, 'shortcode': shortcode}

    def get_owner_id_from_post(self, post: dict) -> str:
        """
        Id автора поста
        """
        raise NotImplementedError

    def get_post_id_from_post(self, post: dict) -> str:
        """
        Id поста
        """
        raise NotImplementedError

    def get_shortcode_from_post(self, post: dict) -> str:
        """Уникальный код поста.

        С помощью данного кода можно получить более подробную
        информацию о посте (например ник автора) через отдельный ajax запрос.
        """
        raise NotImplementedError


class FirstPageParser(LocationPageParser):
    """
    Парсинг индексной (первой) страницы с постами
    """

    def extract_shared_data(self, response: scrapy.http.Response) -> dict:
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


class NextPageParser(LocationPageParser):
    """
    Парсер данных со страницы, полученной после запроса следующей страницы из пагинации
    """
    def extract_shared_data(self, response: scrapy.http.Response) -> dict:
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


class Pagination:
    """
    Пагинация
    """

    def get_last_post_id(shared_data: dict) -> str:
        """
        Получение id последнего поста на текущей странице, для того, чтобы сформировать
        запрос на следующую страниццу в пагинации
        """
        raise NotImplementedError

    def pagination_has_next_page(shared_data: dict) -> bool:
        """
        Проверка пагинации на предмет наличия следующей страницы
        """
        raise NotImplementedError

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