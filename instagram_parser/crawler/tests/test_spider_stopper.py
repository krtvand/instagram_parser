from instagram_parser.crawler.crawler.spider_stopper import ItemsCountSpiderStopper

import unittest


class TestItemsCountSpiderStopper(unittest.TestCase):

    def setUp(self):
        self.spider_stopper = ItemsCountSpiderStopper()
        self.items = []

    def test_do_we_must_stop_spider(self):
        should_stop = self.spider_stopper.should_we_stop_spider(self.items)
        self.assertTrue(should_stop)