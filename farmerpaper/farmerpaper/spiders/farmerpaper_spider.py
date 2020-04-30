# -*- coding: utf-8 -*-
import scrapy
import time
from ..items import FarmerpaperItem
import datetime
from ..settings import ELASTICSEARCH_INDEX, ELASTICSEARCH_TYPE


class FarmerpaperSpiderSpider(scrapy.Spider):
    name = 'farmerpaper_spider'
    allowed_domains = ['szb.farmer.com.cn']
    current_time = time.strftime("%Y%m%d", time.localtime())
    today = datetime.date.today()
    basic_url = 'http://szb.farmer.com.cn/2020/'+current_time+'/'
    start_urls = ['http://szb.farmer.com.cn/2020/'+current_time+'/'+current_time+'_plist.htm']

    def parse(self, response):
        node_list = response.xpath("//div[@class='bancititle']/a")
        for node in node_list:
            end_url = node.xpath("./@href").extract_first().split("./")[1]
            url = self.basic_url + end_url
            yield scrapy.Request(url=url, callback=self.getlist)

    def getlist(self, response):
        node_list = response.xpath("//map[@name='map_of_yyb']/area")
        for node in node_list:
            end_url = node.xpath("./@href").extract_first().split("../")[1]
            url = self.basic_url + end_url
            if self.duplicate.redis_db.hexists(self.duplicate.redis_data_dict, url):
                print("该连接已被爬取")
            else:
                yield scrapy.Request(url=url, callback=self.getmsg)

    def getmsg(self, response):
        item = FarmerpaperItem()
        item['url'] = response.url
        item['title'] = response.xpath("//h1/text()").extract_first()
        item['author'] = response.xpath("//td/div/table/tbody/tr/td/table/tbody/tr[4]/td/text()").extract_first()
        item['content'] = response.xpath("//td[@class='font6']/span").xpath('string(.)').extract_first()
        item['publishtime'] = self.current_time
        item['fromwhere'] = "农民日报"
        item['spiderName'] = ELASTICSEARCH_TYPE
        item['spiderDesc'] = '农民日报'
        item['siteType'] = '纸媒'
        item['source'] = '农民日报'
        item['publicTimeStamp'] = int(time.mktime(self.today.timetuple()))
        item['insertTimeStamp'] = int(time.time() * 1000)
        yield item
