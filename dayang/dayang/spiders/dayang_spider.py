# -*- coding: utf-8 -*-
import datetime
import re
import time
import scrapy
from scrapy.spiders import Rule, CrawlSpider
from scrapy.linkextractors import LinkExtractor
from ..items import DayangItem
from ..settings import ELASTICSEARCH_TYPE

# 大洋网
class DayangSpiderSpider(CrawlSpider):
    name = 'dayang_spider'
    #allowed_domains = ['dayoo.com']
    current_time = time.strftime("%Y%m/%d", time.localtime())
    today = datetime.date.today()
    start_urls = ['https://news.dayoo.com/guangzhou/150955.shtml', 'https://news.dayoo.com/guangzhou/150956.shtml',
                  'https://news.dayoo.com/society/140000.shtml', 'https://news.dayoo.com/finance/139999.shtml',
                  'https://news.dayoo.com/world/139998.shtml', 'https://news.dayoo.com/china/139997.shtml',
                  'https://news.dayoo.com/guangzhou/153828.shtml']
    rules = {
        Rule(LinkExtractor(allow='_\d\.shtml')),
        Rule(LinkExtractor(allow='https://news.dayoo.com/[a-z]+/'+current_time+'/\d+\_\d+\.htm'),
             callback='parse_item')

    }

    def parse_item(self, response):
        item = DayangItem()
        url = response.url
        if self.duplicate.redis_db.hexists(self.duplicate.redis_data_dict, url):
            print("该连接已被爬取")
        else:
            item['title'] = response.xpath("//div[@class='article-hd']/h1/text()").extract_first()
            item['publishtime'] = response.xpath("//span[@class='time']/text()").extract_first()
            content = response.xpath("//div[@id='text_content']/div").xpath('string(.)').extract_first()
            content = re.findall(u"[\u4e00-\u9fa5]+", content)
            item['content'] = ''.join(content)
            item['editor'] = response.xpath("//div[@class='editor']/text()").extract_first()
            item['fromwhere'] = response.xpath("//span[@class='source']/text()").extract_first()
            item['url'] = url
            item['spiderName'] = ELASTICSEARCH_TYPE
            item['spiderDesc'] = '大洋网'
            item['siteType'] = '新闻'
            item['source'] = '大洋网'
            item['publicTimeStamp'] = int(time.mktime(self.today.timetuple()))
            item['insertTimeStamp'] = int(time.time() * 1000)
            yield item
