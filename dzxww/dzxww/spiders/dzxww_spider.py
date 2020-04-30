# -*- coding: utf-8 -*-
import time

import scrapy
from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor
from ..items import DzxwwItem
from ..settings import ELASTICSEARCH_INDEX, ELASTICSEARCH_TYPE
import datetime


class DzxwwSpiderSpider(CrawlSpider):
    name = 'dzxww_spider'
    allowed_domains = ['dzshbw.com']
    start_urls = ['http://www.dzshbw.com/news/zhongbang/', 'http://www.dzshbw.com/news/shizheng/',
                  'http://www.dzshbw.com/news/fazhi/', 'http://www.dzshbw.com/news/shehui/']
    current_time = time.strftime('%m%d', time.localtime(time.time()))
    today = datetime.date.today()
    # def __init__(self, spiderName=None, *a, **kw):
    #     self.proxy = "http://106.46.136.115:4237"
    #     self.duplicate = Duplicate(self.name)
    #     self.sentiment = SentimentAnalysis()
    #     self.duplicate.find_all_url(index=ELASTICSEARCH_INDEX, doc_type=ELASTICSEARCH_TYPE, source='url')
    rules = {
        Rule(LinkExtractor(allow='/[2-9]\.html'), follow=True),
        Rule(LinkExtractor(allow='http://www.dzshbw.com/news/2020/shizheng_'+current_time+'/[0-9]{6}\.html'), callback='getmessage'),
        Rule(LinkExtractor(allow='http://www.dzshbw.com/news/2020/fazhi_'+current_time+'/[0-9]{6}\.html'), callback='getmessage'),
        Rule(LinkExtractor(allow='http://www.dzshbw.com/news/2020/shehui_'+current_time+'/[0-9]{6}\.html'), callback='getmessage'),
        Rule(LinkExtractor(allow='http://www.dzshbw.com/news/2020/zhongbang_'+current_time+'/[0-9]{6}\.html'), callback='getmessage'),
    }

    def getmessage(self, response):
        item = DzxwwItem()
        url = response.url
        if self.duplicate.redis_db.hexists(self.duplicate.redis_data_dict, url):
            print("该连接已被爬取")
        else:
            item['title'] = response.xpath("//div[@id='readnewstitle']/text()").extract_first()
            item['content'] = response.xpath("//div[@id='newscontent']").xpath('string(.)').extract_first()
            item['time'] = response.xpath("//div[@id='newsinfo']/text()").extract_first()[0:22]
            item['fromwhere'] = response.xpath("//div[@id='newsinfo']/text()").extract_first()[23:]
            item['editor'] = response.xpath("//p[@style='text-align: right;']/text()").extract_first()
            item['url'] = response.url
            item['spiderName'] = ELASTICSEARCH_TYPE
            item['spiderDesc'] = '大众新闻网'
            item['siteType'] = '新闻网站'
            item['source'] = '大众新闻网'
            item['publicTimeStamp'] = int(time.mktime(self.today.timetuple()))
            item['insertTimeStamp'] = int(time.time() * 1000)
            yield item


