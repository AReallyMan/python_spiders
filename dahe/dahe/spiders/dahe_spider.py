# -*- coding: utf-8 -*-
import re

import scrapy
from scrapy.spiders import Rule, CrawlSpider
from scrapy.linkextractors import LinkExtractor
import time
from ..items import DaheItem
import datetime
from ..settings import ELASTICSEARCH_TYPE


#大河网
class DaheSpiderSpider(CrawlSpider):
    name = 'dahe_spider'
    allowed_domains = ['dahe.cn']
    start_urls = ['https://news.dahe.cn/hnyw/', 'https://news.dahe.cn/gn27/',
                  'https://news.dahe.cn/nxw/', 'https://news.dahe.cn/dysj/',
                  'https://news.dahe.cn/sh27/']
    current_time = time.strftime("%m-%d", time.localtime())
    today = datetime.date.today()
    rules = {
        Rule(LinkExtractor(allow='https://news.dahe.cn/2020/'+current_time+'/\d+\.html'),
             callback='parse_item'),

    }

    def parse_item(self, response):
        item = DaheItem()
        url = response.url
        if self.duplicate.redis_db.hexists(self.duplicate.redis_data_dict, url):
            print("该连接已被爬取")
        else:
            item['title'] = response.xpath("//h1[@id='4g_title']/text()").extract_first()
            item['publishtime'] = response.xpath("//p[@class='time fl']/text()").extract_first()
            content = response.xpath("//div[@id='mainCon']").xpath('string(.)').extract_first()
            content = re.findall(u"[\u4e00-\u9fa5]+", content)
            item['content'] = ''.join(content)
            item['editor'] = response.xpath("//p[@id='editor_baidu']/text()").extract_first()
            item['fromwhere'] = response.xpath("//p[@id='source_baidu']/text()").extract_first()
            item['url'] = url
            item['spiderName'] = ELASTICSEARCH_TYPE
            item['spiderDesc'] = '大河网'
            item['siteType'] = '新闻'
            item['source'] = '大河网'
            item['publicTimeStamp'] = int(time.mktime(self.today.timetuple()))
            item['insertTimeStamp'] = int(time.time() * 1000)
            yield item
