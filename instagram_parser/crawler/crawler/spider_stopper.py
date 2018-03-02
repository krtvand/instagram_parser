class SpiderStopper:
    def should_we_stop_spider(self, items: list) -> bool:
        raise NotImplementedError


class ItemsCountSpiderStopper(SpiderStopper):
    """
    Завершение работы по количеству собранных требуемых элементов
    """
    def should_we_stop_spider(self, items: list) -> bool:
        return None