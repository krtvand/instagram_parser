import re
import json

import scrapy

class DataExtractorException(Exception):
    """
    Исключение при проблемах сбора информации со страницы сайта.
    Например не найден необходимый елемент.
    """


def extract_shared_data(response: scrapy.http.Response) -> dict:
    """Вся информация о публикациях находится в json объекте в исходном коде страницы.

    """
    elem_with_shared_data = response.xpath('//body/script[starts-with(text(), "window._sharedData")]/text()').extract_first()
    shared_data_str = re.sub(r'(.*?)(\{.*\})(.*)', r'\2', elem_with_shared_data)
    shared_data_dict = json.loads(shared_data_str)

    return shared_data_dict

def get_post_objects(shared_data: dict) -> list:
    try:
        posts_list = shared_data.get('entry_data', {}).get('LocationsPage', ).pop().get('location', {}).get('media', {}).get('nodes', [])
        if not posts_list:
            raise Exception
    except Exception:
        raise DataExtractorException('Can not get nodes (posts) from shared_data')

    return posts_list

def _get_owner_id_from_post(post:dict) -> str:
    owner_id = post.get('owner', {}).get('id')
    if not owner_id:
        raise DataExtractorException('Can not get owner id from post')

    return owner_id

def get_owner_ids_from_posts_list(post_list: list) -> str:
    result = []
    for post in post_list:
        result.append(_get_owner_id_from_post(post))

    return result