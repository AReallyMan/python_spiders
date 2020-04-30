# -*- coding: utf-8 -*-
import re

import scrapy
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import Rule, CrawlSpider
import time
import datetime
from ..items import XizangItem
from ..settings import ELASTICSEARCH_TYPE


# 中国西藏网
class XizangSpiderSpider(CrawlSpider):
    name = 'xizang_spider'
    #allowed_domains = ['tibet.cn']
    start_urls = ['http://www.tibet.cn/cn/news/', 'http://www.tibet.cn/cn/politics/',
                  'http://www.tibet.cn/cn/bwsp/', 'http://www.tibet.cn/cn/Instant/']
    today = datetime.date.today()
    current_time = time.strftime("%Y%m%d")
    rules = {
        Rule(LinkExtractor(allow='http://www.tibet.cn/cn/[a-z]+/[a-z]+/'+current_time[:6]+'/t'+current_time+'_\d+\.html'),
             callback='parse_item'),
        Rule(LinkExtractor(allow='http://www.tibet.cn/cn/[a-z]+/'+current_time[:6]+'/t'+current_time+'_\d+\.html'),
             callback='parse_item'),
    }

    def parse_item(self, response):
        item = XizangItem()
        if self.duplicate.redis_db.hexists(self.duplicate.redis_data_dict, response.url):
            print("该连接已被爬取")
        else:
            item['title'] = response.xpath("//div[@class='title_box']/h2/text()").extract_first()
            item['publishtime'] = response.xpath("//div[@class='info']/span[2]/text()").extract_first()
            item['fromwhere'] = response.xpath("//div[@class='info']/span[3]/text()").extract_first()
            author = response.xpath("//div[@class='info']/span[1]/text()[2]").extract_first()
            author = re.findall(u"[\u4e00-\u9fa5]+", author)
            if author:
                item['author'] = ''.join(author)
            else:
                item['author'] = ''
            content = response.xpath("//div[@class='Custom_UnionStyle']").xpath('string(.)').extract_first()
            if content:
                content = re.findall(u"[\u4e00-\u9fa5]+", content)
                item['content'] = ''.join(content)
            else:
                c = response.xpath("//div[@id='text']").xpath('string(.)').extract_first()
                c = re.findall(u"[\u4e00-\u9fa5]+", c)
                item['content'] = ''.join(c)
            item['url'] = response.url
            item['spiderName'] = ELASTICSEARCH_TYPE
            item['spiderDesc'] = '中国西藏网'
            item['siteType'] = '新闻'
            item['source'] = '中国西藏网'
            item['publicTimeStamp'] = int(time.mktime(self.today.timetuple()))
            item['insertTimeStamp'] = int(time.time() * 1000)
            yield item
