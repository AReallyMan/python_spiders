# -*- coding: utf-8 -*-
import scrapy
import datetime
import time
from ..items import JfjbmapItem
from ..settings import ELASTICSEARCH_INDEX, ELASTICSEARCH_TYPE


class JfjbSpiderSpider(scrapy.Spider):
    name = 'jfjb_spider'
    allowed_domains = ['81.cn']
    today = datetime.date.today()
    current_time = time.strftime("%Y-%m/%d", time.localtime())
    start_urls = ['http://www.81.cn/jfjbmap/content/' + current_time + '/node_2.htm']  # 开始url链接（解放军报）
    basic_url = 'http://www.81.cn/jfjbmap/content/' + current_time + '/'  # 公共链接部分）

    def parse(self, response):
        url_node = response.xpath("//div[@class='col-md-4-10 channel-list']/ul[@class='list-unstyled']/li/a")  # 每个板报里的对应的条例的末尾数据

        for url_end in url_node:
            if len(url_end.xpath("./@href").extract_first().split("./")[0]) == 0:  # 判断是否是第一个节点链接，True则取索引1，False取0
                url = self.basic_url + url_end.xpath("./@href").extract_first().split("./")[
                    1]
            else:
                url = self.basic_url + url_end.xpath("./@href").extract_first().split("./")[
                    0]
            yield scrapy.Request(url=url, callback=self.detail_page)

    def detail_page(self, response):
        detail_page_urlend = response.xpath("//div[@class='newslist-item current']/ul[@class='list-unstyled']/li/a")
        for detail_url in detail_page_urlend:
            url = self.basic_url + detail_url.xpath("./@href").extract_first()
            yield scrapy.Request(url=url, callback=self.getitem)

    def getitem(self, response):
        item = JfjbmapItem()
        url = response.url
        if self.duplicate.redis_db.hexists(self.duplicate.redis_data_dict, url):
            print("该连接已被爬取")
        else:
            item['title'] = response.xpath("//h2[@id='APP-Title']/text()").extract_first()
            item['content'] = response.xpath("//div[@class='article-content']/founder-content").xpath('string(.)').extract_first()
            item['publishtime'] = self.current_time
            item['url'] = response.url
            item['spiderName'] = ELASTICSEARCH_TYPE
            item['spiderDesc'] = '解放军报'
            item['siteType'] = '纸媒'
            item['source'] = '解放军报'
            item['publicTimeStamp'] = int(time.mktime(self.today.timetuple()))
            item['insertTimeStamp'] = int(time.time() * 1000)
            yield item
