# -*- coding: utf-8 -*-
import scrapy
import datetime
import re
import time
from scrapy.spiders import Rule, CrawlSpider
from scrapy.linkextractors import LinkExtractor
from ..items import XiantvItem
from ..settings import ELASTICSEARCH_TYPE


# （读取西安网）西安人民广播电台和西安电视台里边都是视频信息，就只有一个西安网栏目是文字信息
class XiantvSpiderSpider(CrawlSpider):
    name = 'xianTV_spider'
    #allowed_domains = ['xantv.cn']
    current_time = time.strftime("%Y/%m/%d", time.localtime())
    today = datetime.date.today()
    start_urls = ['http://news.xiancity.cn/guonei/index.shtml', 'http://news.xiancity.cn/guoji/index.shtml',
                  'http://news.xiancity.cn/shanxi/index.shtml', 'http://news.xiancity.cn/xian/index.shtml',
                  ]
    rules = {
        Rule(LinkExtractor(allow='system/'+current_time+'/\d+\.shtml'), callback='parse_item'),
    }

    def parse_item(self, response):
        item = XiantvItem()
        if self.duplicate.redis_db.hexists(self.duplicate.redis_data_dict, response.url):
            print("该连接已被爬取")
        else:
            item['url'] = response.url
            item['title'] = response.xpath("//h2[@id='newstitle']/text()").extract_first()
            content = response.xpath("//div[@id='artical']").xpath('string(.)').extract_first()
            if content:
                content = re.findall(u"[\u4e00-\u9fa5]+", content)
                item['content'] = ''.join(content)
            item['publishtime'] = response.xpath("//div[@class='note']/span[2]/span/text()").extract_first()
            item['fromwhere'] = response.xpath("//div[@class='note']/span[1]/span/text()").extract_first()
            item['editor'] = response.xpath("//p[@class='f-name']/span/text()").extract_first()
            item['spiderName'] = ELASTICSEARCH_TYPE
            item['spiderDesc'] = '西安网'
            item['siteType'] = '新闻'
            item['source'] = '西安网'
            item['publicTimeStamp'] = int(time.mktime(self.today.timetuple()))
            item['insertTimeStamp'] = int(time.time() * 1000)
            yield item