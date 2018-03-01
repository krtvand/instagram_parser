import re
import json

import scrapy

class DataExtractorException(Exception):
    """
    Исключение при проблемах сбора информации со страницы сайта.
    Например не найден необходимый елемент.
    """


def extract_shared_data(response: scrapy.http.Response) -> dict:
    """
    Вся информация о публикациях находится в json объекте в исходном коде страницы.
    """
    elem_with_shared_data = response.xpath('//body/script[starts-with(text(), "window._sharedData")]/text()').extract_first()
    shared_data_str = re.sub(r'(.*?)(\{.*\})(.*)', r'\2', elem_with_shared_data)
    shared_data_dict = json.loads(shared_data_str)

    return shared_data_dict

def extract_data_from_next_page(response: scrapy.http.Response) -> dict:
    """
    Следующая страница при пагинации запрашивается через ajax запрос и в ответ приходит чистый json
    """
    next_page__data_as_dict = json.loads(response.text)

    return next_page__data_as_dict

def get_post_objects(shared_data: dict) -> list:
    try:
        posts_list = shared_data.get('entry_data', {}).get('LocationsPage')[0].get('location', {}).get('media', {}).get('nodes', [])
        if not posts_list:
            raise Exception
    except Exception:
        raise DataExtractorException('Can not get nodes (posts) from shared_data')

    return posts_list

def get_post_objects_from_next_page(shared_data: dict) -> list:
    try:
        posts_list = shared_data.get('data', {}).get('location', {}).get('edge_location_to_media', {}).get('edges', [])
        if not posts_list:
            raise Exception
    except Exception:
        raise DataExtractorException('Can not get posts from next_page')

    return posts_list


def _get_owner_id_from_post(post: dict) -> str:
    owner_id = post.get('owner', {}).get('id')
    if not owner_id:
        raise DataExtractorException('Can not get owner id from post')

    return owner_id

def get_owner_ids_from_posts_list(post_list: list) -> list:
    result = []
    for post in post_list:
        result.append(_get_owner_id_from_post(post))

    return result

def _get_owner_id_from_next_page_post(post: dict) -> str:
    owner_id = post.get('node', {}).get('owner', {}).get('id')
    if not owner_id:
        raise DataExtractorException('Can not get owner id from post')

    return owner_id

def collect_data_from_next_page_post(post: dict) -> dict:
    post_id = post.get('node', {}).get('id')
    owner_id = _get_owner_id_from_next_page_post(post)

    return {'post_id': post_id, 'owner_id': owner_id}

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