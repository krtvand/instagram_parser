import re
import json

import scrapy

from instagram_parser.crawler.data_extractors.base import (LocationPageDataExtractor,
                                                           DataExtractorException)


class FirstPageDataExtractor(LocationPageDataExtractor):
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

    def get_publication_date(self, post: dict) -> str:
        publication_date_in_epoch = post.get('date')
        if not publication_date_in_epoch:
            raise DataExtractorException('Can not get publication date from post')
        return publication_date_in_epoch

