# -*- coding: utf-8 -*-
import scrapy
from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor
import time
import datetime
from ..items import BjbdbItem

from ..settings import ELASTICSEARCH_INDEX, ELASTICSEARCH_TYPE


class BdbspiderSpider(CrawlSpider):
    name = 'bdbspider'
    allowed_domains = ['bj.bendibao.com']
    start_urls = ['http://bj.bendibao.com/news/list1.htm']
    today = datetime.date.today()
    current_time = time.strftime("%Y%#m%#d", time.localtime(time.time()))

    # def __init__(self, spiderName=None, *a, **kw):
    #     self.proxy = "http://106.46.136.115:4237"
    #     self.duplicate = Duplicate(self.name)
    #     self.sentiment = SentimentAnalysis()
    #     self.duplicate.find_all_url(index=ELASTICSEARCH_INDEX, doc_type=ELASTICSEARCH_TYPE, source='url')
    # 1.scrapy请求start_urls ， 获取到response
    # 2.使用LinkExtractors中allow的内容去匹配response，获取到url
    # 3.请求这个url ， response交给，callback指向的方法处理
    rules = {
        Rule(LinkExtractor(allow='http://bj.bendibao.com/news/list[1-9]\.htm'), follow=True),
        Rule(LinkExtractor(allow='http://bj.bendibao.com/news/' + current_time + '/\d{6}\.shtm'), callback='parse_item')
    }

    def parse_item(self, response):
        item = BjbdbItem()
        url = response.url
        if self.duplicate.redis_db.hexists(self.duplicate.redis_data_dict, url):
            print("该连接已被爬取")
        else:
            item['title'] = response.xpath("//div[@class='title daoyu']/h1/strong/text()").extract_first()
            item['publishtime'] = response.xpath("//span[@class='time']/text()").extract_first()
            item['introduction'] = response.xpath("//div[@class='leading']/p/text()").extract_first()
            item['content'] = response.xpath("//div[@id='bo']").xpath('string(.)').extract_first()
            item['url'] = response.url
            item['spiderName'] = ELASTICSEARCH_TYPE
            item['spiderDesc'] = '北京本地宝'
            item['siteType'] = '资讯网站'
            item['source'] = '北京本地宝'
            item['publicTimeStamp'] = int(time.mktime(self.today.timetuple()))
            item['insertTimeStamp'] = int(time.time() * 1000)
            yield item
