# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class CcgpItem(scrapy.Item):
    # define the fields for your item here like:

    href = scrapy.Field()
    content = scrapy.Field()
    time = scrapy.Field()

    proxy= scrapy.Field()
    service= scrapy.Field()

    title = scrapy.Field() # 标题
    publish = scrapy.Field()  # 发布时间
    budget = scrapy.Field() # 预算金额
    project = scrapy.Field()# 采购项目名称
    type = scrapy.Field() #品目
    company = scrapy.Field() #采购单位
    administrative = scrapy.Field() #行政区域
    noticeTime = scrapy.Field() #公告时间
    priceTime = scrapy.Field() #获取招标问价时间
    openTime = scrapy.Field() #开标时间
    address = scrapy.Field() #开标地点
