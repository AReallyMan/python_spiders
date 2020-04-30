# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class TakungpaoItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    # url链接
    url = scrapy.Field()
    # 标题
    title = scrapy.Field()
    # 来源
    fromwhere = scrapy.Field()
    # 内容
    content = scrapy.Field()
    # 时间
    timetoday = scrapy.Field()
    #作者
    author = scrapy.Field()
    spiderName = scrapy.Field()
    spiderDesc = scrapy.Field()
    siteType = scrapy.Field()
    source = scrapy.Field()
    publicTimeStamp = scrapy.Field()
    insertTimeStamp = scrapy.Field()
    index = scrapy.Field()
