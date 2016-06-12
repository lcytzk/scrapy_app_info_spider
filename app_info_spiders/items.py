# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class AppItem(scrapy.Item):
    packageName = scrapy.Field()
    packageId = scrapy.Field()
    title = scrapy.Field()
    source = scrapy.Field()
    tag = scrapy.Field()
