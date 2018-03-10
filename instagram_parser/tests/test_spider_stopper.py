from instagram_parser.crawler.utils.spider_stopper import ItemsCountSpiderStopper

import unittest


class TestItemsCountSpiderStopper(unittest.TestCase):

    def setUp(self):
        self.max_items_count = 10
        self.spider_stopper = ItemsCountSpiderStopper({'max_items_count': self.max_items_count})

    def test_do_we_must_stop_spider(self):
        items = list(range(self.max_items_count + 1))
        should_stop = self.spider_stopper.should_we_stop_spider(items=items)
        self.assertTrue(should_stop)