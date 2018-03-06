import datetime

class SpiderStopper:
    def __init__(self, params: dict):
        """Инициализация параметров остановщика

        :param params: словарь, в котором содержатся параметры, согласно котороым можно
        сделать вывод о том, что парсинг пора остановить
        """

    def should_we_stop_spider(self, *args) -> bool:
        raise NotImplementedError


class ItemsCountSpiderStopper(SpiderStopper):
    """
    Завершение работы по количеству собранных требуемых элементов
    """
    def __init__(self, params: dict):
        super().__init__(params)
        self.max_items_count = params.get('max_items_count', 0)

    def should_we_stop_spider(self, items: list) -> bool:
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

    def should_we_stop_spider(self, post_publication_date: datetime.datetime) -> bool:
        if post_publication_date <= self.oldest_publication_date:
            return True
        else:
            return False