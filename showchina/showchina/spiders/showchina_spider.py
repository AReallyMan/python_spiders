# -*- coding: utf-8 -*-
import scrapy
from scrapy.spiders import Rule, CrawlSpider
from scrapy.linkextractors import LinkExtractor
import time
from ..items import ShowchinaItem
import datetime
from ..settings import ELASTICSEARCH_TYPE


# 看中国
class ShowchinaSpiderSpider(CrawlSpider):
    name = 'showchina_spider'
    allowed_domains = ['showchina.org']
    start_urls = ['http://www.showchina.org/zx/index.html']
    current_time = time.strftime("%Y/%m/%d")
    today = datetime.date.today()
    rules = {
        Rule(LinkExtractor(allow='index-[2-9]\.html')),
        Rule(LinkExtractor(allow='http://www.showchina.org/' + current_time + '/[a-z\d]+\.html'), callback='getlist'),
    }

    def getlist(self, response):
        item = ShowchinaItem()
        if self.duplicate.redis_db.hexists(self.duplicate.redis_data_dict, response.url):
            print("该连接已被爬取")
        else:
            item['title'] = response.xpath("//p[@class='titleV']/text()").extract_first()
            item['publishtime'] = response.xpath("//span[@class='date']/text()").extract_first()
            item['fromwhere'] = response.xpath("//span[@class='from']/text()").extract_first()
            item['content'] = response.xpath("//div[@class='content']").xpath('string(.)').extract_first()
            item['url'] = response.url
            item['spiderName'] = ELASTICSEARCH_TYPE
            item['spiderDesc'] = '看中国'
            item['siteType'] = '新闻'
            item['source'] = '看中国'
            item['publicTimeStamp'] = int(time.mktime(self.today.timetuple()))
            item['insertTimeStamp'] = int(time.time() * 1000)
            yield item

