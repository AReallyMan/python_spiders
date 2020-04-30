# -*- coding: utf-8 -*-
import re

import scrapy
from scrapy.spiders import Rule, CrawlSpider
from scrapy.linkextractors import LinkExtractor
import time
import datetime
from ..items import InternationalzxItem
from ..settings import ELASTICSEARCH_TYPE


# 国际在线（滚动）http://news.cri.cn/roll
class GuojizxSpiderSpider(CrawlSpider):
    name = 'guojizx_spider'
    current_time = time.strftime("%Y%m%d", time.localtime())
    today = datetime.date.today()
    # start_urls = ['http://news.cri.cn/roll', 'http://news.cri.cn/roll-2', 'http://news.cri.cn/roll-3',
    #               'http://news.cri.cn/roll-4', 'http://news.cri.cn/roll-5', 'http://news.cri.cn/roll-6',
    #               'http://news.cri.cn/roll-7', 'http://news.cri.cn/roll-7', 'http://news.cri.cn/roll-8',
    #               'http://news.cri.cn/roll-9']
    start_urls = ['http://news.cri.cn/roll', 'http://news.cri.cn/roll-\d']

    rules = {
        Rule(LinkExtractor(
            allow='http://news.cri.cn/' + current_time + '/[a-z\d]{8}\-[a-z\d]{4}\-[a-z\d]{4}\-[a-z\d]{4}\-[a-z\d]{12}\.html'),
            callback='getlist'),

    }

    def getlist(self, response):
        item = InternationalzxItem()
        if self.duplicate.redis_db.hexists(self.duplicate.redis_data_dict, response.url):
            print("该连接已被爬取")
        else:
            item['title'] = response.xpath("//h1[@class='atitle']/text()").extract_first()
            item['publishtime'] = response.xpath("//span[@class='acreatedtime']/text()").extract_first()
            fromwhere = response.xpath("//span[@class='asource']/a/text()").extract_first()
            if fromwhere:
                item['fromwhere'] = fromwhere
            else:
                item['fromwhere'] = response.xpath("//span[@class='asource']/text()").extract_first()
            item['editor'] = response.xpath("//span[@class='aeditor']/text()").extract_first()
            item['url'] = response.url
            contents = response.xpath("//div[@class='abody']").xpath('string(.)').extract_first()
            if contents:
                contents = re.findall(u"[\u4e00-\u9fa5]+", contents)
                item['content'] = ''.join(contents)
            else:
                item['content'] = ''

            item['spiderName'] = ELASTICSEARCH_TYPE
            item['spiderDesc'] = '国际在线'
            item['siteType'] = '新闻'
            item['source'] = '国际在线'
            item['publicTimeStamp'] = int(time.mktime(self.today.timetuple()))
            item['insertTimeStamp'] = int(time.time() * 1000)
            yield item
