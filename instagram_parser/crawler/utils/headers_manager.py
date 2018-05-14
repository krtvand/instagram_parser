import hashlib


class HeadersManager(object):
    def get_headers(self):
        raise NotImplementedError
#
# class HeaderClass(object):
#     def set_headers(self):
#         self.headers
#
# class AjaxHeadersClass(HeadersManager)


class PaginationHeadersManager(HeadersManager):
    def __init__(self, rhx_gis, pagination_uri_variables):
        self.rhx_gis = rhx_gis
        self.pagination_uri_variables = pagination_uri_variables
        self.headers = {}

    def get_headers(self):
        self._set_x_requested_with()
        self._set_x_instagram_gis()

        return self.headers

    def _set_x_requested_with(self):
        self.headers['x-requested-with'] = 'XMLHttpRequest'

    def _set_x_instagram_gis(self):
        data = self.rhx_gis + ":" + self.pagination_uri_variables
        x_instagram_gis = hashlib.md5(data).hexdigest()
        self.headers['x-instagram-gis'] = x_instagram_gis
