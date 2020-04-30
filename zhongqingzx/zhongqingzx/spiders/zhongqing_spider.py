# -*- coding: utf-8 -*-
import re

import scrapy
from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor
from ..items import ZhongqingzxItem
import datetime
import time
from ..settings import ELASTICSEARCH_INDEX, ELASTICSEARCH_TYPE


#中青在线
class ZhongqingSpiderSpider(CrawlSpider):
    name = 'zhongqing_spider'
    allowed_domains = ['cyol.com']
    start_urls = ['http://news.cyol.com/node_67044.htm', 'http://news.cyol.com/node_67040.htm', 'http://news.cyol.com/node_67038.htm', 'http://news.cyol.com/node_67037.htm', 'http://news.cyol.com/node_67036.htm', 'http://news.cyol.com/node_67035.htm', 'http://news.cyol.com/app/node_66774.htm?tid=82&title=%E8%88%86%E6%83%85']
    current_time = time.strftime("%Y-%m/%d", time.localtime())
    today = datetime.date.today()
    rules = {
        Rule(LinkExtractor(allow='node_\d{5}_[2-4]\.htm')),
        Rule(LinkExtractor(allow=''+current_time+'/content_\d{8}\.htm')),
        Rule(LinkExtractor(allow='http://news.cyol.com/content/'+current_time+'/content_\d{8}\.htm'), callback='parse_item'),

    }

    def parse_item(self, response):
        item = ZhongqingzxItem()
        url = response.url
        if self.duplicate.redis_db.hexists(self.duplicate.redis_data_dict, url):
            print("该连接已被爬取")
        else:
            item['title'] = response.xpath("//div[@class='lline']/h1/text()").extract_first()
            item['fromwhere'] = response.xpath("//div[@class='lline']/div/text()").extract_first()
            item['content'] = response.xpath("//div[@class='content']").xpath('string(.)').extract_first()
            item['editor'] = response.xpath("//div[@class='zb']/text()").extract_first()
            item['url'] = response.url
            publishtime= response.xpath("//div[@class='year']/span/text()").extract_first() + response.xpath("//div[@class='month']/text()").extract_first() + response.xpath("//div[@class='oclock']/text()").extract_first()
            publishtime = [re.sub(r"\xa0|\s", "", i) for i in publishtime]
            publishtime = [i for i in publishtime if len(i) > 0]
            publishtime = "".join(publishtime)
            item['publishtime'] = publishtime
            item['spiderName'] = ELASTICSEARCH_TYPE
            item['spiderDesc'] = '中青在线'
            item['siteType'] = '新闻网站'
            item['source'] = '中青在线'
            item['publicTimeStamp'] = int(time.mktime(self.today.timetuple()))
            item['insertTimeStamp'] = int(time.time() * 1000)
            yield item





