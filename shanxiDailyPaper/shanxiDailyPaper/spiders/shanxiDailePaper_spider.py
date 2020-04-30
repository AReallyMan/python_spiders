# -*- coding: utf-8 -*-
import re

import scrapy
from scrapy.spiders import Rule, CrawlSpider
from scrapy.linkextractors import LinkExtractor
import time
import datetime
from ..items import ShanxidailypaperItem
from ..settings import ELASTICSEARCH_TYPE


# 陕西日报
class ShanxidailepaperSpiderSpider(CrawlSpider):
    name = 'shanxiDailePaper_spider'
    #allowed_domains = ['esb.sxdaily.com.cn']
    today = datetime.date.today()
    current_time = time.strftime("%Y%m/%d", time.localtime())
    start_urls = ['http://esb.sxdaily.com.cn/pc/layout/'+current_time+'/node_01.html']
    rules = {
        Rule(LinkExtractor(allow='node_\d+\.html')),
        Rule(LinkExtractor(allow='http://esb.sxdaily.com.cn/pc/content/'+current_time+'/content_\d+\.html'),
             callback='parse_item'),
    }

    def parse_item(self, response):
        item = ShanxidailypaperItem()
        if self.duplicate.redis_db.hexists(self.duplicate.redis_data_dict, response.url):
            print("该连接已被爬取")
        else:
            item['url'] = response.url
            item['title'] = response.xpath("//div[@class='bmnr_con_biaoti']/text()").extract_first()
            content = response.xpath("//div[@id='zoom']/founder-content").xpath('string(.)').extract_first()
            if content:
                content = re.findall(u"[\u4e00-\u9fa5]+", content)
                item['content'] = ''.join(content)
            item['publishtime'] = self.current_time
            item['fromwhere'] = "陕西日报"

            item['spiderName'] = ELASTICSEARCH_TYPE
            item['spiderDesc'] = '陕西日报'
            item['siteType'] = '纸媒'
            item['source'] = '陕西日报'
            item['publicTimeStamp'] = int(time.mktime(self.today.timetuple()))
            item['insertTimeStamp'] = int(time.time() * 1000)
            yield item

