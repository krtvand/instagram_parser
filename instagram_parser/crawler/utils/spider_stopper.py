import datetime

class SpiderStopperException(Exception):
    """
    Ошибка остановщика парсера
    """

class SpiderStopper:
    def __init__(self, params: dict):
        """Инициализация параметров остановщика

        :param params: словарь, в котором содержатся параметры, согласно котороым можно
        сделать вывод о том, что парсинг пора остановить
        """

    def should_we_stop_spider(self, **kargs) -> bool:
        raise NotImplementedError


class ItemsCountSpiderStopper(SpiderStopper):
    """
    Завершение работы по количеству собранных требуемых элементов
    """
    def __init__(self, params: dict):
        super().__init__(params)
        self.max_items_count = params.get('max_items_count', 0)

    def should_we_stop_spider(self, **kwargs) -> bool:
        if 'items' not in kwargs:
            raise SpiderStopperException('items not found in arguments')
        else:
            items = kwargs['items']
        if len(items) >= self.max_items_count:
            return True
        else:
            return False


class PostPublicationDateStopper(SpiderStopper):
    """
    Завершение работы по дате публикации поста
    """

    def __init__(self, params: dict):
        super().__init__(params)
        self.oldest_publication_date = params.get('oldest_publication_date')

    def should_we_stop_spider(self, **kwargs) -> bool:
        if 'publication_date_in_epoch' not in kwargs:
            raise SpiderStopperException('publication_date_in_epoch not found in arguments')
        else:
            publication_date_in_epoch = kwargs['publication_date_in_epoch']
        publication_date = datetime.datetime.utcfromtimestamp(publication_date_in_epoch)
        if publication_date <= self.oldest_publication_date:
            return True
        else:
            return False