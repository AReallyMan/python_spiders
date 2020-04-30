# -*- coding: utf-8 -*-
import re

import scrapy
from scrapy.spiders import Rule, CrawlSpider

from ..items import ZhengzhoutvItem
from scrapy.linkextractors import LinkExtractor
import time
from datetime import date
from ..settings import ELASTICSEARCH_TYPE


# 郑州电视台
class ZztvSpiderSpider(CrawlSpider):
    name = 'zztv_spider'
    #allowed_domains = ['zztv.tv']
    start_urls = ['http://www.zhengzhou.siteyun.hoge.cn/folder129/folder137/']
    today = date.today()
    current_time = time.strftime("%Y-%m-%d", time.localtime())
    rules = {
        Rule(LinkExtractor(allow='http://www.zhengzhou.siteyun.hoge.cn/folder129/folder137/'+current_time+'/\d+\.html'),
             callback='parse_item')
    }

    def parse_item(self, response):
        item = ZhengzhoutvItem()
        if self.duplicate.redis_db.hexists(self.duplicate.redis_data_dict, response.url):
            print("该连接已被爬取")
        else:
            item['title'] = response.xpath("//div[@class='article-title pull-left']/h1/text()").extract_first()
            item['publishtime'] = response.xpath("//span[@class='time']/text()").extract_first()
            content = response.xpath("//div[@class='article-main']").xpath('string(.)').extract_first()
            item['content'] = content
            item['fromwhere'] = re.findall("来源.*", content)[0]
            item['url'] = response.url
            item['spiderName'] = ELASTICSEARCH_TYPE
            item['spiderDesc'] = '郑州电视台'
            item['siteType'] = '新闻'
            item['source'] = '郑州电视台'
            item['publicTimeStamp'] = int(time.mktime(self.today.timetuple()))
            item['insertTimeStamp'] = int(time.time() * 1000)
            yield item
