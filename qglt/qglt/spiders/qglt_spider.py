# -*- coding: utf-8 -*-
import datetime
import re
import scrapy
import time
from ..items import QgltItem
from ..settings import ELASTICSEARCH_INDEX, ELASTICSEARCH_TYPE
import datetime


def getWithIn24(stamp):
    now = datetime.datetime.now()
    # 今日0点
    zeroToday = now - datetime.timedelta(hours=now.hour, minutes=now.minute, seconds=now.second,
                                         microseconds=now.microsecond)
    # 今日23点59
    lastToday = zeroToday + datetime.timedelta(hours=23, minutes=59, seconds=59)
    zeroToday = str(zeroToday)
    lastToday = str(lastToday)
    stamp = int(stamp)
    datatime = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(float(str(stamp)[0:10])))
    if zeroToday < datatime < lastToday:
        return True
    else:
        return False


class QgltSpiderSpider(scrapy.Spider):
    name = 'qglt_spider'
    basic_url = 'http://bbs1.people.com.cn/board/2/1_1.html'
    detail_url = 'http://bbs1.people.com.cn/txt_new/'
    today = datetime.date.today()

    def start_requests(self):
        yield scrapy.Request(url=self.basic_url, callback=self.parse)

    def parse(self, response):
        index_url = response.url
        flag = 0
        node_list = response.xpath("//ul[@class='tableList']/li")
        for node in node_list:
            page = index_url.split("_")[1].split(".")[0]
            page = int(page)
            showtime = node.xpath("./div[2]/div/p[1]/@datetime").extract_first()
            showstamp = node.xpath("./div[2]/div/p[1]/text()").extract_first()
            url = node.xpath("./div/div/p[@class='tableTitle']/a[1]/@href").extract_first()
            img = node.xpath("./p/img").extract_first()
            if img is not None:
                if getWithIn24(showstamp):
                    if self.duplicate.redis_db.hexists(self.duplicate.redis_data_dict, url):
                        print("该连接已被爬取")
                    else:
                        yield scrapy.Request(url=url, callback=self.getdetail)
            else:
                if getWithIn24(showstamp):
                    if self.duplicate.redis_db.hexists(self.duplicate.redis_data_dict, url):
                        print("该连接已被爬取")
                    else:
                        yield scrapy.Request(url=url, callback=self.getdetail)
                    flag += 1
                    if flag == 100:
                        page += 1
                        page = str(page)
                        page_url = "http://bbs1.people.com.cn/board/2/1_" + page + ".html"
                        yield scrapy.Request(url=page_url, callback=self.parse)
                else:
                    break

    def getdetail(self, response):
        item = QgltItem()
        item['url'] = response.url
        print(response.url)
        title = response.xpath("//div[@class='navBar']/h2/text()").extract_first()[19:]
        if len(title) == 0:
            title = response.xpath("//div[@class='navBar']/h2/text()[2]").extract_first()[19:]
        item['title'] = title
        item['publishtime'] = response.xpath("//p[@class='replayInfo']/span[1]/text()[3]").extract_first()[3:]
        item['author'] = response.xpath("//span[@class='float_R']/a/text()").extract_first()
        details_url = response.xpath("//article/div/@content_path").extract_first()
        content = response.xpath("//article/div[1]/text()").extract_first()
        if len(content) != 27:
            item['content'] = content
            yield item
        if details_url is not None:
            d_url = self.detail_url + details_url[32:]
            d_url = d_url.strip()
            yield scrapy.Request(url=d_url, callback=self.getcontent, meta={"item": item})

    def getcontent(self, response):
        item = response.meta['item']
        content = re.findall(u"[\u4e00-\u9fa5]+", response.text)
        item['content'] = ''.join(content)
        item['spiderName'] = ELASTICSEARCH_TYPE
        item['spiderDesc'] = '强国论坛'
        item['siteType'] = '论坛'
        item['source'] = '强国论坛'
        item['publicTimeStamp'] = int(time.mktime(self.today.timetuple()))
        item['insertTimeStamp'] = int(time.time() * 1000)
        yield item
