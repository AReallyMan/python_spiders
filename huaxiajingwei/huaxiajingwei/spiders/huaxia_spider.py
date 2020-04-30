# -*- coding: utf-8 -*-
import re
import datetime
import time

import scrapy
from ..items import HuaxiajingweiItem
from ..settings import ELASTICSEARCH_TYPE


# 华夏经纬新闻
class HuaxiaSpiderSpider(scrapy.Spider):
    name = 'huaxia_spider'
    allowed_domains = ['huaxia.com']
    start_urls = ['http://www.huaxia.com/xw/dlxw/index.html', 'http://www.huaxia.com/xw/twxw/index.html',
                  'http://www.huaxia.com/xw/gaxw/index.html', 'http://www.huaxia.com/xw/gjxw/index.html',
                  'http://www.huaxia.com/xw/zhxw/index.html', 'http://www.huaxia.com/xw/zdxw/index.html',
                  'http://www.huaxia.com/xw/xwsb/index.html', 'http://www.huaxia.com/xw/mttt/index.html',
                  'http://www.huaxia.com/xw/gjrd/index.html']
    basic_url = "http://www.huaxia.com"
    now_date = datetime.date.today()
    today = str(now_date)
    page = 1

    def start_requests(self):
        for url in self.start_urls:
            yield scrapy.Request(url=url, callback=self.getlist)

    def getlist(self, response):
        flag = 0
        node_list = response.xpath("//td [@height='23']")
        for node in node_list:
            flag += 1
            t = node.xpath("./span/font/text()").extract_first()
            t = "2020-" + re.findall(r'\d+', t)[0] + "-" + re.findall(r'\d+', t)[1]
            if t == self.today:
                url = node.xpath("./a/@href").extract_first()
                yield scrapy.Request(url=self.basic_url + url, callback=self.getmsg)
                if flag == 54:
                    self.page += 1
                    yield scrapy.Request(url=response.url[:-5] + "_" + str(self.page) + ".html", callback=self.getlist)

    def getmsg(self, response):
        item = HuaxiajingweiItem()
        url = response.url
        if self.duplicate.redis_db.hexists(self.duplicate.redis_data_dict, url):
            print("该连接已被爬取")
        else:
            item['title'] = response.xpath("//div[@class='Ftitle']/strong/text()").extract_first()
            from_time = response.xpath("//td[@valign='top']/font/text()").extract_first()
            publishtime = re.findall(r'\d+', from_time)
            fromwhere = re.findall(u"[\u4e00-\u9fa5]+", from_time)
            item['publishtime'] = '-'.join(publishtime)
            item['fromwhere'] = ''.join(fromwhere)
            content = response.xpath("//td[@id='oImg']").xpath('string(.)').extract_first()
            content = re.findall(u"[\u4e00-\u9fa5]+", content)
            item['content'] = ''.join(content)
            item['url'] = response.url
            item['spiderName'] = ELASTICSEARCH_TYPE
            item['spiderDesc'] = '华夏经纬新闻'
            item['siteType'] = '新闻'
            item['source'] = '华夏经纬新闻'
            item['publicTimeStamp'] = int(time.mktime(self.now_date.timetuple()))
            item['insertTimeStamp'] = int(time.time() * 1000)
            yield item
