# -*- coding: utf-8 -*-
import re

import scrapy
import time
from ..items import JusticeItem
import datetime
from ..settings import ELASTICSEARCH_TYPE


# 正义网
class JusticeSpiderSpider(scrapy.Spider):
    name = 'justice_spider'
    allowed_domains = ['jcrb.com']
    start_urls = ['http://news.jcrb.com/gnxw/', 'http://news.jcrb.com/xwjj/',
                  'http://news.jcrb.com/gjxw/', 'http://news.jcrb.com/shxw/',
                  'http://news.jcrb.com/ycgj/', 'http://www.jcrb.com/legal/sfgz/',
                  'http://www.jcrb.com/procuratorate/XSJC/', 'http://www.jcrb.com/procuratorate/XZJC/',
                  'http://www.jcrb.com/procuratorate/GYSS/', 'http://www.jcrb.com/opinion/zywy/',
                  'http://news.jcrb.com/jsxw/']
    current_time = time.strftime("%Y-%m-%d", time.localtime())
    today = datetime.date.today()
    # 控制分页flag，遍历到最后就分页读取
    flag_page = 1
    # 分页数
    flag_fenye = 0

    def start_requests(self):
        for url in self.start_urls:
            yield scrapy.Request(url=url, callback=self.getList)

    def getList(self, response):
        u = response.url
        flag = 0
        node_list = response.xpath("//ul[@class='txtList']/li")
        for node in node_list:
            pTime = node.xpath("./text()").extract_first()
            if pTime:
                pTime = re.findall("\d{4}-\d{2}-\d{2}", pTime)[0]
            else:
                continue
            if self.current_time == pTime:
                flag += 1
                detail_url = node.xpath("./a/@href").extract_first()
                if len(detail_url) < 40:
                    detail_url = u.split("_")[0].split("index")[0] + detail_url.split("./")[1]
                else:
                    detail_url = detail_url
                yield scrapy.Request(url=detail_url, callback=self.getMsg)
                if flag == 40:
                    self.flag_fenye += 1
                    if self.flag_fenye == 1:
                        pages = u + "index_" + str(self.flag_page) + ".html"
                    else:
                        pages = u.split("_")[0]+"_"+str(self.flag_fenye)+".html"
                    self.flag_page += 1
                    yield scrapy.Request(url=pages, callback=self.getList)
            else:
                break

    def getMsg(self, response):
        item = JusticeItem()
        url = response.url
        if self.duplicate.redis_db.hexists(self.duplicate.redis_data_dict, url):
            print("该连接已被爬取")
        else:
            item['title'] = response.xpath("//div[@class='bt']/h1/text()").extract_first()
            item['publishtime'] = response.xpath("//span[@id='pubtime_baidu']/text()").extract_first()
            item['author'] = response.xpath("//span[@id='author_baidu']/text()").extract_first()
            item['editor'] = response.xpath("//span[@class='editor']/text()").extract_first()
            item['fromwhere'] = response.xpath("//span[@id='source_baidu']/text()").extract_first()
            item['url'] = url
            content = response.xpath("//div[@class='Custom_UnionStyle']").xpath('string(.)').extract_first()
            if content:
                content = re.findall(u"[\u4e00-\u9fa5]+", content)
                item['content'] = ''.join(content)
            else:
                c = response.xpath("//div[@id='fontzoom']/div[@class='TRS_Editor']").xpath('string(.)').extract_first()
                c = re.findall(u"[\u4e00-\u9fa5]+", c)
                item['content'] = ''.join(c)
            item['spiderName'] = ELASTICSEARCH_TYPE
            item['spiderDesc'] = '正义网'
            item['siteType'] = '新闻'
            item['source'] = '正义网'
            item['publicTimeStamp'] = int(time.mktime(self.today.timetuple()))
            item['insertTimeStamp'] = int(time.time() * 1000)
            yield item
