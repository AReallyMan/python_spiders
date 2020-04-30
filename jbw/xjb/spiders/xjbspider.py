# -*- coding: utf-8 -*-
import scrapy
from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor
import time
from ..items import XjbItem
import datetime
from ..settings import ELASTICSEARCH_INDEX, ELASTICSEARCH_TYPE


class XjbspiderSpider(CrawlSpider):
    name = 'jbwspider'
    allowed_domains = ['bjd.com.cn']
    start_urls = ['http://www.bjd.com.cn/']
    current_date = time.strftime('%Y%m/%d', time.localtime(time.time()))
    today = datetime.date.today()

    rules = (
        Rule(LinkExtractor(allow='http://www.bjd.com.cn/[a-z]{2,4}$')),
        Rule(LinkExtractor(allow='page_[1-9]\.html')),
        Rule(LinkExtractor(allow='http://www.bjd.com.cn/a/' + current_date + '/[a-zA-Z\d]{26}\.html'),
             callback='parse_item'),
    )

    def parse_item(self, response):
        item = XjbItem()
        url = response.url
        if self.start_urls[0] in url:
            if self.duplicate.redis_db.hexists(self.duplicate.redis_data_dict, url):
                print("该连接已被爬取")
            else:
                item['title'] = response.xpath("//span[@class='span1']/text()").extract_first()
                item['content'] = response.xpath("//div[@class='contentnews21']").xpath('string(.)').extract_first()
                item['time'] = response.xpath("//span[@class='span31']/text()").extract_first()
                item['fromWhere'] = response.xpath("//span[@class='span32']/text()").extract_first()
                item['author'] = response.xpath("//span[@class='span33'][1]/text()").extract_first()
                item['editor'] = response.xpath("//span[@class='span33'][2]/text()").extract_first()
                item['url'] = url
                item['spiderName'] = ELASTICSEARCH_TYPE
                item['spiderDesc'] = '京报网'
                item['siteType'] = '新闻网站'
                item['source'] = '京报网'
                item['publicTimeStamp'] = int(time.mktime(self.today.timetuple()))
                item['insertTimeStamp'] = int(time.time() * 1000)
                yield item
