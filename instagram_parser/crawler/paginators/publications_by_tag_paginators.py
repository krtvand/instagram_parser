import re

from instagram_parser.crawler.paginators.paginators_base import (PaginatorInFirstPage,
                                                                 PaginatorInNextPage,
                                                                 PaginationException)
from instagram_parser.crawler.utils.headers_manager import PaginationHeadersManager


class PublicationsByTagPaginatorInFirstPage(PaginatorInFirstPage):
    pagination_uri_variables_template = '{{"tag_name":"{tag_name}","first":12,"after":"{after}"}}'

    def __init__(self, base_url, tag):
        self.base_url = base_url
        self.tag = tag

    def get_last_post_id(self, shared_data):
        try:
            last_post_id = shared_data.get('entry_data', {}).get('TagPage')[0].get('graphql', {}). \
                get('hashtag', {}).get('edge_hashtag_to_media', {}).get('page_info', {}).get('end_cursor')
            if not last_post_id:
                raise Exception
        except Exception:
            raise PaginationException('Can not get last post id (end_cursor) from shared_data')
        return last_post_id

    def pagination_has_next_page(self, shared_data):
        try:
            pagination_has_next_page = shared_data.get('entry_data', {}).get('TagPage')[0].get('graphql', {}). \
                get('hashtag', {}).get('edge_hashtag_to_media', {}).get('page_info', {}).get('has_next_page')
            if pagination_has_next_page is None:
                raise Exception
        except Exception:
            raise PaginationException(
                'Can not get value for next_has_page attribute from shared_data')
        return pagination_has_next_page

    def get_link_for_js_file_with_queryhash(self, response):
        link = response.xpath(
            '//link[contains(@href, "/static/bundles/base/TagPageContainer.js")]/@href').extract_first()

        return link

    def _get_variables_for_pagination_uri(self, shared_data):
        after = self.get_last_post_id(shared_data)
        variables = self.pagination_uri_variables_template.format(tag_name=self.tag, after=after)
        return variables

    def get_queryhash_from_js_source(self, page_source):
        pattern = r'(?P<text_before>tagMedia\.byTagName\.get\(t\)\.pagination},queryId:\")(?P<query_hash>.*?)(\",queryParams)'
        match = re.search(pattern, page_source)
        if match:
            query_hash = match.group('query_hash')
        else:
            raise PaginationException('Can not extract query_hash from js_source')
        return query_hash


class PublicationsByTagPaginatorInNextPage(PaginatorInNextPage):

    pagination_uri_variables_template = '{{"tag_name":"{tag_name}","first":12,"after":"{after}"}}'

    def __init__(self, base_url, tag):
        self.base_url = base_url
        self.tag = tag

    def _get_variables_for_pagination_uri(self, shared_data):
        after = self.get_last_post_id(shared_data)
        variables = self.pagination_uri_variables_template.format(tag_name=self.tag, after=after)
        return variables

    def get_last_post_id(self, shared_data):
        try:
            last_post_id = shared_data.get('data', {}).get('hashtag', {}).get(
                'edge_hashtag_to_media', {}).get('page_info', {}).get('end_cursor')
            if not last_post_id:
                raise Exception
        except Exception:
            raise PaginationException('Can not get last post id (end_cursor) from shared_data')
        return last_post_id

    def pagination_has_next_page(self, shared_data):
        try:
            pagination_has_next_page = shared_data.get('data', {}).get('hashtag', {}).get(
                'edge_hashtag_to_media', {}).get('page_info', {}).get('has_next_page')
            if pagination_has_next_page is None:
                raise Exception
        except Exception:
            raise PaginationException(
                'Can not get value for next_has_page attribute from shared_data')
        return pagination_has_next_page