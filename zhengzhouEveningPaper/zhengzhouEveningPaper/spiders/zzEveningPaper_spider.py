# -*- coding: utf-8 -*-
import datetime
import re
import time
from ..items import ZhengzhoueveningpaperItem
import scrapy
from scrapy.spiders import Rule, CrawlSpider
from scrapy.linkextractors import LinkExtractor
from ..settings import ELASTICSEARCH_TYPE


# 郑州晚报
class ZzeveningpaperSpiderSpider(CrawlSpider):
    name = 'zzEveningPaper_spider'
    allowed_domains = ['zzwb.zynews.cn']
    today = datetime.date.today()
    current_time = time.strftime("%Y-%m/%d", time.localtime())
    start_urls = ['https://zzwb.zynews.cn/html/2020-04/27/node_102.htm']
    rules = {
        Rule(LinkExtractor(allow='node_\d+\.htm')),
        Rule(LinkExtractor(allow='https://zzwb.zynews.cn/html/'+current_time+'/content_\d+\.htm'),
             callback='parse_item'),
    }

    def parse_item(self, response):
        item = ZhengzhoueveningpaperItem()
        url = response.url
        if self.duplicate.redis_db.hexists(self.duplicate.redis_data_dict, url):
            print("该连接已被爬取")
        else:
            item['title'] = response.xpath("//td[@class='font01']/text()").extract_first()
            item['publishtime'] = self.current_time
            content = response.xpath("//div[@id='ozoom']/founder-content").xpath('string(.)').extract_first()
            content = re.findall(u"[\u4e00-\u9fa5]+", content)
            item['content'] = ''.join(content)
            item['fromwhere'] = "郑州晚报"
            item['url'] = url
            item['spiderName'] = ELASTICSEARCH_TYPE
            item['spiderDesc'] = '郑州晚报'
            item['siteType'] = '纸媒'
            item['source'] = '郑州晚报'
            item['publicTimeStamp'] = int(time.mktime(self.today.timetuple()))
            item['insertTimeStamp'] = int(time.time() * 1000)
            yield item