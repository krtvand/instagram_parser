import re

import scrapy


class ExampleSpider(scrapy.Spider):
    name = 'example'
    # allowed_domains = ['example.com']
    start_urls = ['https://www.instagram.com/explore/locations/224829075/']

    def parse(self, response):
        t = response.xpath('//body/script[starts-with(text(), "window._sharedData")]/text()').extract_first()
        t2 = re.sub(r'(.*?)(\{.*)', r'\2', t)
        yield {'t': t2}
