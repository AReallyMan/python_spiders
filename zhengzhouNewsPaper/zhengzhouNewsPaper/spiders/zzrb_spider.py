# -*- coding: utf-8 -*-
import re
import scrapy
from scrapy.spiders import Rule, CrawlSpider
from scrapy.linkextractors import LinkExtractor
import datetime
import time
from ..items import ZhengzhounewspaperItem
from ..settings import ELASTICSEARCH_TYPE


# 郑州日报
class ZzrbSpiderSpider(CrawlSpider):
    name = 'zzrb_spider'
    allowed_domains = ['zzrb.zynews.cn']
    today = datetime.date.today()
    current_time = time.strftime("%Y-%m/%d", time.localtime())
    start_urls = ['https://zzrb.zynews.cn/html/'+current_time+'/node_3.htm']
    rules = {
        Rule(LinkExtractor(allow='node_\d\.htm')),
        Rule(LinkExtractor(allow='https://zzrb.zynews.cn/html/'+current_time+'/content_\d+\.htm'),
             callback='parse_item'),
    }

    def parse_item(self, response):
        item = ZhengzhounewspaperItem()
        url = response.url
        if self.duplicate.redis_db.hexists(self.duplicate.redis_data_dict, url):
            print("该连接已被爬取")
        else:
            item['title'] = response.xpath("//td[@class='font01']/text()").extract_first()
            item['publishtime'] = self.current_time
            content = response.xpath("//div[@id='ozoom']/founder-content").xpath('string(.)').extract_first()
            content = re.findall(u"[\u4e00-\u9fa5]+", content)
            item['content'] = ''.join(content)
            item['fromwhere'] = "郑州日报"
            item['url'] = url
            item['spiderName'] = ELASTICSEARCH_TYPE
            item['spiderDesc'] = '郑州日报'
            item['siteType'] = '纸媒'
            item['source'] = '郑州日报'
            item['publicTimeStamp'] = int(time.mktime(self.today.timetuple()))
            item['insertTimeStamp'] = int(time.time() * 1000)
            yield item
