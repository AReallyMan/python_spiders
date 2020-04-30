# -*- coding: utf-8 -*-
import re
import scrapy
import datetime
import time
from ..items import ZzradioItem
from ..settings import ELASTICSEARCH_TYPE


# 郑州人民广播电台
class ZzradioSpiderSpider(scrapy.Spider):
    name = 'zzradio_spider'
    allowed_domains = ['zzradio.cn']
    start_urls = ['http://www.zzradio.cn/news/index.html?page=1']
    basic_url = "http://www.zzradio.cn/"
    # 控制分页变量
    num = 1
    today = datetime.date.today()

    def parse(self, response):
        page_num = 1
        node_list = response.xpath("//ul[@class='list']/li")
        for node in node_list:
            page_num += 1
            publishtime = node.xpath("./a/div/span/text()").extract_first()
            url = node.xpath("./a/@href").extract_first()
            flag = self.judgeTimeStamp(publishtime)
            if flag:
                yield scrapy.Request(url=self.basic_url + url, callback=self.parse_item)
                # 遍历下一页数据
                if page_num == 20:
                    self.num += 1
                    url = self.start_urls[0].split("=")[0] + "=" + str(self.num)
                    yield scrapy.Request(url=url, callback=self.parse)

    # 判断时间戳是否符合今天的数据条件
    def judgeTimeStamp(self, publishtime):
        now = datetime.datetime.now()
        # 今日0点
        zeroToday = now - datetime.timedelta(hours=now.hour, minutes=now.minute, seconds=now.second,                                             microseconds=now.microsecond)
        # 今日23点59
        lastToday = zeroToday + datetime.timedelta(hours=23, minutes=59, seconds=59)
        zeroarray = time.strptime(str(zeroToday), "%Y-%m-%d %H:%M:%S")
        zerostamp = int(time.mktime(zeroarray))
        lastarray = time.strptime(str(lastToday), "%Y-%m-%d %H:%M:%S")
        laststamp = int(time.mktime(lastarray))
        time_array = time.strptime(publishtime, "%Y-%m-%d %H:%M:%S")
        publishStamp = time.mktime(time_array)
        if zerostamp < publishStamp < laststamp:
            # 是今天的数据
            flag = True
        else:
            flag = False
        return flag

    def parse_item(self, response):
        if self.basic_url in response.url:
            if self.duplicate.redis_db.hexists(self.duplicate.redis_data_dict, response.url):
                print("该连接已被爬取")
            else:
                item = ZzradioItem()
                item['title'] = response.xpath("//div[@class='tit']/h2/text()").extract_first()
                item['publishtime'] = response.xpath("//div[@class='tit']/span[2]/text()").extract_first()
                content = response.xpath("//div[@id='content']/news_page").xpath('string(.)').extract_first()
                if content:
                    content = re.findall(u"[\u4e00-\u9fa5]+", content)
                item['content'] = ''.join(content)
                item['fromwhere'] = response.xpath("//div[@class='tit']/span[1]/text()").extract_first()
                item['editor'] = response.xpath("//div[@class='edit']/span/text()").extract_first()
                item['url'] = response.url
                item['spiderName'] = ELASTICSEARCH_TYPE
                item['spiderDesc'] = '郑州人民广播电台'
                item['siteType'] = '新闻'
                item['source'] = '郑州人民广播电台'
                item['publicTimeStamp'] = int(time.mktime(self.today.timetuple()))
                item['insertTimeStamp'] = int(time.time() * 1000)
                yield item
