import scrapy


from instagram_parser.crawler.crawler.data_extractors import (FirstPageDataExtractor,
                                                              NextPageDataExtractor)

from instagram_parser.crawler.crawler.spider_stopper import SpiderStopper


class SearchResultPagePostsParser:
    """
    Парсинг постов со страницы результатов поиска по локации или тэгу
    """

    def __init__(self, spider_stopper: SpiderStopper):
        self.spider_stoper = spider_stopper
        self.data_extractor = self.create_data_extractor()

    def parse(self, response: scrapy.http.Response):
        parsed_posts_data = {}
        shared_data = self.data_extractor.get_page_info_from_json(response)
        posts_list = self.data_extractor.get_post_objects(shared_data)
        for post in posts_list:
            post_data = self.data_extractor.collect_data_from_post(post)
            parsed_posts_data.update(post_data)

        return parsed_posts_data

    def create_data_extractor(self):
        raise NotImplementedError


class FirstPageParser(SearchResultPagePostsParser):

    def create_data_extractor(self):
        return FirstPageDataExtractor()


class NextPageParser(SearchResultPagePostsParser):

    def create_data_extractor(self):
        return NextPageDataExtractor()