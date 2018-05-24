# -*- coding: utf-8 -*-

from instagram_parser.crawler.paginators.paginators_base import (
    PaginatorInNextPage,
    PaginatorInFirstPage,
    PaginationException
)


class PublicationsByLocationPaginatorInFirstPage(PaginatorInFirstPage):

    pagination_uri_variables_template = '{{"id":"{id}","first":12,"after":"{after}"}}'

    def get_last_post_id(self, shared_data):
        try:
            last_post_id = shared_data.get('entry_data', {}).get('LocationsPage')[0].get('graphql', {}).\
                get('location', {}).get('edge_location_to_media', {}).get('page_info', {}).get('end_cursor')
            if not last_post_id:
                raise Exception
        except Exception:
            raise PaginationException('Can not get last post id (end_cursor) from shared_data')
        return last_post_id

    def pagination_has_next_page(self, shared_data):
        try:
            pagination_has_next_page = shared_data.get('entry_data', {}).get('LocationsPage')[0].get('graphql', {}).\
                get('location', {}).get('edge_location_to_media', {}).get('page_info', {}).get('has_next_page')
            if pagination_has_next_page is None:
                raise Exception
        except Exception:
            raise PaginationException(
                'Can not get value for next_has_page attribute from shared_data')
        return pagination_has_next_page

    def _get_variables_for_pagination_uri(self, shared_data):
        after = self.get_last_post_id(shared_data)
        variables = self.pagination_uri_variables_template.format(id=self.location_id, after=after)
        return variables

    def get_link_for_js_file_with_queryhash(self, response):
        link = response.xpath(
            '//link[contains(@href, "/static/bundles/base/LocationPageContainer.js")]/@href').extract_first()

        return link


class PublicationsByLocationPaginatorInNextPage(PaginatorInNextPage):

    pagination_uri_variables_template = '{{"id":"{id}","first":12,"after":"{after}"}}'

    def _get_variables_for_pagination_uri(self, shared_data):
        after = self.get_last_post_id(shared_data)
        variables = self.pagination_uri_variables_template.format(id=self.location_id, after=after)
        return variables

    def get_last_post_id(self, shared_data):
        try:
            last_post_id = shared_data.get('data', {}).get('location', {}).get(
                'edge_location_to_media', {}).get('page_info', {}).get('end_cursor')
            if not last_post_id:
                raise Exception
        except Exception:
            raise PaginationException('Can not get last post id (end_cursor) from shared_data')
        return last_post_id

    def pagination_has_next_page(self, shared_data):
        try:
            pagination_has_next_page = shared_data.get('data', {}).get('location', {}).get(
                'edge_location_to_media', {}).get('page_info', {}).get('has_next_page')
            if pagination_has_next_page is None:
                raise Exception
        except Exception:
            raise PaginationException(
                'Can not get value for next_has_page attribute from shared_data')
        return pagination_has_next_page
