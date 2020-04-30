# -*- coding: utf-8 -*-
import re

import scrapy


from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import Rule, CrawlSpider
import datetime
import time
from ..items import XiandailypaperItem
from ..settings import ELASTICSEARCH_TYPE


# 西安日报
class XiandailypaperSpiderSpider(CrawlSpider):
    name = 'xianDailyPaper_spider'
    allowed_domains = ['epaper.xiancn.com']
    current_time = time.strftime("%Y-%m/%d", time.localtime())
    start_urls = ['http://epaper.xiancn.com/newxarb/html/'+current_time+'/node_23.htm']
    today = datetime.date.today()
    rules = {
        Rule(LinkExtractor(allow='node_\d+\.htm')),
        Rule(LinkExtractor(allow='content_\d+\.*'), callback='parse_item'),
    }

    def parse_item(self, response):
        item = XiandailypaperItem()
        if self.duplicate.redis_db.hexists(self.duplicate.redis_data_dict, response.url):
            print("该连接已被爬取")
        else:
            item['url'] = response.url
            item['title'] = response.xpath("//div[@id='print-main']/h1/text()").extract_first()
            content = response.xpath("//div[@class='main01']").xpath('string(.)').extract_first()
            if content:
                content = re.findall(u"[\u4e00-\u9fa5]+", content)
                item['content'] = ''.join(content)
            item['publishtime'] = self.current_time
            item['fromwhere'] = "西安日报"

            item['spiderName'] = ELASTICSEARCH_TYPE
            item['spiderDesc'] = '西安日报'
            item['siteType'] = '纸媒'
            item['source'] = '西安日报'
            item['publicTimeStamp'] = int(time.mktime(self.today.timetuple()))
            item['insertTimeStamp'] = int(time.time() * 1000)
            yield item