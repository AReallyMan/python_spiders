# -*- coding: utf-8 -*-
import re

import scrapy
import time
import datetime

from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor
from ..items import WestItem
from ..settings import ELASTICSEARCH_TYPE


# 西部网
class WestSpiderSpider(CrawlSpider):
    name = 'west_spider'
    #allowed_domains = ['cnwest.com']
    current_time = time.strftime("%Y/%m/%d", time.localtime())
    today = datetime.date.today()
    start_urls = ['http://news.cnwest.com/szyw/index.html', 'http://news.cnwest.com/tianxia/index.html',
                  'http://news.cnwest.com/bwyc/index.html', 'http://news.cnwest.com/sxxw/index.html',
                  'http://news.cnwest.com/dishi/index.html', 'http://finance.cnwest.com/cjzx/index.html',
                  'http://gov.cnwest.com/zwyw/index.html']
    rules = {
        Rule(LinkExtractor(allow='\_[2-5]\.html')),
        Rule(LinkExtractor(allow='http://news.cnwest.com/[a-z]+/a/'+current_time+'/\d+\.html'),
             callback='parse_item'),
        Rule(LinkExtractor(allow='http://gov.cnwest.com/zwyw/a/'+current_time+'/\d+\.html'),
             callback='parse_item'),
        Rule(LinkExtractor(allow='http://finance.cnwest.com/cjzx/a/'+current_time+'/\d+\.html'),
             callback='parse_item')
    }

    def parse_item(self, response):
        item = WestItem()
        url = response.url
        if "rexian" in url:
            print()
        else:
            if self.duplicate.redis_db.hexists(self.duplicate.redis_data_dict, url):
                print("该连接已被爬取")
            else:
                item['title'] = response.xpath("//div[@class='layout']/h1/text()").extract_first()
                publishtime = response.xpath("//div[@class='layout-left']/p/text()").extract_first()
                if publishtime:
                    item['publishtime'] = re.findall("\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}", publishtime)[0]
                else:
                    item['publishtime'] = ""
                fromwhere = response.xpath("//div[@class='layout-left']/p/text()").extract_first()
                fromwhere = re.findall("来源.*", fromwhere)
                if fromwhere:
                    item['fromwhere'] = fromwhere[0]
                else:
                    item['fromwhere'] = ""
                content = response.xpath("//div[@id='conCon']").xpath('string(.)').extract_first()
                if content:
                    content = re.findall(u"[\u4e00-\u9fa5]+", content)
                    item['content'] = ''.join(content)
                else:
                    item['content'] = ""
                item['editor'] = response.xpath("//p[@class='bianji']/text()").extract_first()
                item['url'] = url
                item['spiderName'] = ELASTICSEARCH_TYPE
                item['spiderDesc'] = '西部网'
                item['siteType'] = '新闻'
                item['source'] = '西部网'
                item['publicTimeStamp'] = int(time.mktime(self.today.timetuple()))
                item['insertTimeStamp'] = int(time.time() * 1000)
                yield item
