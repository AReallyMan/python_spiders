# -*- coding: utf-8 -*-
import re
import time

import scrapy
from scrapy.spiders import Rule, CrawlSpider
from scrapy.linkextractors import LinkExtractor
from ..items import SouthcnItem
import datetime
from ..settings import ELASTICSEARCH_TYPE


# 南方网
class SouthcnSpiderSpider(CrawlSpider):
    name = 'southCn_spider'
    # allowed_domains = ['news.southcn.com']
    current_time = time.strftime("%Y-%m/%d")
    today = datetime.date.today()
    start_urls = ['http://www.southcn.com/pc2018/yw/node_384370.htm', 'http://news.southcn.com/gd/',
                  'http://news.southcn.com/china/default.htm', 'http://news.southcn.com/international/default.htm',
                  'http://economy.southcn.com/', 'http://news.southcn.com/community/', 'http://kb.southcn.com/default.htm']
    rules = {
        Rule(LinkExtractor(allow='_[2-5]\.htm')),
        Rule(LinkExtractor(allow='http://news.southcn.com/[a-z]+/content/'+current_time+'/content_\d+\.htm'), callback='parse_item'),

        Rule(LinkExtractor(allow='http://economy.southcn.com/e/'+current_time+'/content_\d+\.htm'), callback='parse_item'),
        Rule(LinkExtractor(allow='http://kb.southcn.com/content/'+current_time+'/content_\d+\.htm'), callback='parse_item'),

    }

    def parse_item(self, response):
        item = SouthcnItem()
        item['title'] = response.xpath("//h2[@id='article_title']/text()").extract_first()
        item['publishtime'] = response.xpath("//span[@id='pubtime_baidu']/text()").extract_first()
        item['fromwhere'] = response.xpath("//span[@id='source_baidu']/text()").extract_first()
        item['editor'] = response.xpath("//div[@class='m-editor']/text()").extract_first()
        content = response.xpath("//div[@id='content']").xpath('string(.)').extract_first()
        if content:
            content = re.findall(u"[\u4e00-\u9fa5]+", content)
            item['content'] = ''.join(content)
        else:
            item['content'] = ''
        item['url'] = response.url

        item['spiderName'] = ELASTICSEARCH_TYPE
        item['spiderDesc'] = '南方网'
        item['siteType'] = '新闻'
        item['source'] = '南方网'
        item['publicTimeStamp'] = int(time.mktime(self.today.timetuple()))
        item['insertTimeStamp'] = int(time.time() * 1000)
        yield item