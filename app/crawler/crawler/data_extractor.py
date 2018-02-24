import re
import json

import scrapy

class DataExtractorException(Exception):
    """
    Исключение при проблемах сбора информации со страницы сайта.
    Например не найден необходимый елемент.
    """


def extract_shared_data(response: scrapy.http.Response):
    """Вся информация о публикациях находится в json объекте в исходном коде страницы.

    :param response:
    :return:
    """
    elem_with_shared_data = response.xpath('//body/script[starts-with(text(), "window._sharedData")]/text()').extract_first()
    shared_data_str = re.sub(r'(.*?)(\{.*\})(.*)', r'\2', elem_with_shared_data)

    return shared_data_str

def get_post_objects_as_dict(shared_data: str):
    shared_data_dict = json.loads(shared_data)
    posts = shared_data_dict.get('entry_data', {}).get('LocationsPage', {}).get('location', {}).get('media', {}).get('nodes', {})
    if not posts:
        raise DataExtractorException('Can not get nodes (posts) from shared_data')

    return True
