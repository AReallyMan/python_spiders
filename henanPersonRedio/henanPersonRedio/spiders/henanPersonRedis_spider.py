# -*- coding: utf-8 -*-
import re

import scrapy
from scrapy.spiders import Rule, CrawlSpider
from scrapy.linkextractors import LinkExtractor
import time
from ..items import HenanpersonredioItem
from ..settings import ELASTICSEARCH_TYPE
from datetime import date


# 河南人民广播电台
class HenanpersonredisSpiderSpider(CrawlSpider):
    name = 'henanPersonRedis_spider'
    # allowed_domains = ['hnr.cn']
    start_urls = ['http://news.hnr.cn/xwrd/', 'http://news.hnr.cn/djn/',
                  'http://news.hnr.cn/mxw/', 'http://news.hnr.cn/rxw/',
                  'http://news.hnr.cn/ixw/']
    current_time = time.strftime("%Y%m/%d", time.localtime())
    today = date.today()
    print(current_time)
    rules = {
        Rule(LinkExtractor(allow='\/[2-9]\.html')),
        Rule(LinkExtractor(allow='http://news.hnr.cn/'+current_time+'/\d+\.html'), callback='parse_item'),
    }

    def parse_item(self, response):
        item = HenanpersonredioItem()
        url = response.url
        if self.duplicate.redis_db.hexists(self.duplicate.redis_data_dict, url):
            print("该连接已被爬取")
        else:
            title = response.xpath("//h2[@class='f32 lh48 mrg_t_30']/text()").extract_first()
            if title:
                item['title'] = title
            else:
                item['title'] = response.xpath("//section[@id='article']/h1/text()").extract_first()
            publishtime = response.xpath("//p[@class='left']/span[1]/text()").extract_first()
            if publishtime:
                item['publishtime'] = publishtime
            else:
                item['publishtime'] = response.xpath("//div[@class='time txt_center']/text()").extract_first()
            fromwhere = response.xpath("//p[@class='left']/span[2]/text()").extract_first()
            content = response.xpath("//div[@id='text_fix']").xpath('string(.)').extract_first()
            if content:
                content = content
            else:
                content = response.xpath("//div[@class='editor']").xpath('string(.)').extract_first()
            content = re.findall(u"[\u4e00-\u9fa5]+", content)
            if fromwhere:
                item['fromwhere'] = fromwhere
            else:
                item['fromwhere'] = re.findall("来源.*", content)[0]
            item['content'] = ''.join(content)
            editor = response.xpath("//span[@class='right']/text()").extract_first()
            if editor:
                item['editor'] = editor
            else:
                item['editor'] = ''
            item['url'] = url
            item['spiderName'] = ELASTICSEARCH_TYPE
            item['spiderDesc'] = '河南人民广播电台'
            item['siteType'] = '新闻'
            item['source'] = '河南人民广播电台'
            item['publicTimeStamp'] = int(time.mktime(self.today.timetuple()))
            item['insertTimeStamp'] = int(time.time() * 1000)
            yield item
