# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class ScrapeExternalLinksItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    page_url = scrapy.Field()
    internal_links = scrapy.Field()
    external_links = scrapy.Field()
    link_anchor = scrapy.Field()
    link_type = scrapy.Field()
    link_status = scrapy.Field()
