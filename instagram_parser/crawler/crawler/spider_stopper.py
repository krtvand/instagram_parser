class SpiderStopper:
    def __init__(self, params: dict):
        """Инициализация параметров остановщика

        :param params: словарь, в котором содержатся параметры, согласно котороым можно
        сделать вывод о том, что парсинг пора остановить
        """

    def should_we_stop_spider(self, items: list) -> bool:
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