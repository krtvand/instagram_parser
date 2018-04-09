# -*- coding: utf-8 -*-

import datetime


class PostFilter(object):
    """
    Определение того, какие посты требуется парсить (получать детальную
    информацию и включать в выходной результат), а какие нет.
    """

    def must_be_discarded(self, post):
        raise NotImplementedError


class PublicationDatePostFilter(PostFilter):
    """
    Фильтрация по дате публикации
    """

    def __init__(self, date_from=None, date_till=None):
        self.date_from = date_from
        self.date_till = date_till

    def must_be_discarded(self, post):
        (post_id, post_info), = post.items()
        publication_date_in_epoch = post_info['publication_date']
        post_publication_date = datetime.datetime.utcfromtimestamp(publication_date_in_epoch)
        if not self.date_from <= post_publication_date <= self.date_till:
            return True
        else:
            return False

class DummyPostFilter(PostFilter):
    def must_be_discarded(self, post):
        return False
