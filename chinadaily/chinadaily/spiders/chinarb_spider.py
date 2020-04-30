# -*- coding: utf-8 -*-
import re

import scrapy
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule
import time
import datetime
from ..items import ChinadailyItem
from ..settings import ELASTICSEARCH_TYPE


class ChinarbSpiderSpider(CrawlSpider):
    name = 'chinarb_spider'
    current_time = time.strftime("%Y%m/%d", time.localtime())
    today = datetime.date.today()
    #里边乱入了language标签 http://language.chinadaily.com.cn/
    #a/202004/13/WS5e939f6fa3105d50a3d15993.html，发现他是标签 http://cn.chinadaily.com.cn/a/202004/13/WS5e93ba38a310c00b73c767b7.html进去之后返回的结果，还不太明白
    start_urls = ['http://cn.chinadaily.com.cn/yuanchuang/', 'http://china.chinadaily.com.cn/',
                  'http://world.chinadaily.com.cn/', 'http://caijing.chinadaily.com.cn/']

    rules = {
        Rule(LinkExtractor(allow='yuanchuang/page_[1-9]\.html'), follow=True),
        Rule(LinkExtractor(allow='[a-z]{2,5}\.chinadaily\.com\.cn\/a\/'+current_time+'\/[a-zA-Z\d]{26}\.html'),
             callback='getlist'),

    }

    def getlist(self, response):
        item = ChinadailyItem()
        if "language" in response.url:
            print("language不需要")
        if self.duplicate.redis_db.hexists(self.duplicate.redis_data_dict, response.url):
            print("该连接已被爬取")
        else:
            item['title'] = response.xpath("//h1[@class='dabiaoti']/text()").extract_first()
            item['publishtime'] = response.xpath("//div[@class='xinf-le'][2]/text()").extract_first()
            fromwhere = response.xpath("//div[@class='xinf-le']/a[2]/text()").extract_first()
            if fromwhere:
                item['fromwhere'] = fromwhere
            else:
                item['fromwhere'] = response.xpath("//div[@class='xinf-le']/a/text()").extract_first()
            editor = response.xpath("//div[@class='xinf-le'][1]/text()[1]").extract_first()
            if editor:
                item['editor'] = editor[0:12]
            else:
                item['editor'] = ''
            item['url'] = response.url
            content = response.xpath("//div[@class='article']").xpath('string(.)').extract_first()

            if content:
                content = re.findall(u"[\u4e00-\u9fa5]+", content)
                item['content'] = ''.join(content)
            else:
                c = response.xpath("//div[@id='Content']").xpath('string(.)').extract_first()
                c = re.findall(u"[\u4e00-\u9fa5]+", c)
                item['content'] = ''.join(c)
            item['spiderName'] = ELASTICSEARCH_TYPE
            item['spiderDesc'] = '中国日报中文网'
            item['siteType'] = '纸媒'
            item['source'] = '中国日报中文网'
            item['publicTimeStamp'] = int(time.mktime(self.today.timetuple()))
            item['insertTimeStamp'] = int(time.time() * 1000)
            yield item


