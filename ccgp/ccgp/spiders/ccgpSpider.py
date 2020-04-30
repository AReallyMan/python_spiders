# -*- coding: utf-8 -*-
import scrapy
from ..items import CcgpItem
import re
from datetime import date, timedelta, datetime
import time
from urllib import parse
# import urllib


class CcgpspiderSpider(scrapy.Spider):

    name = 'ccgpSpider'
    allowed_domains = ['ccgp.gov.cn']
    today = str(date.today())
    # today = '2020-04-16'
    basic_url = 'http://search.ccgp.gov.cn/bxsearch?'

    # start_urls = ['http://search.ccgp.gov.cn/bxsearch?searchtype=1&bidSort=&buyerName=&projectId=&pinMu=3&bidType=1&dbselect=bidx&kw=%E5%8C%97%E4%BA%AC&start_time=2020%3A04%3A15&end_time=2020%3A04%3A16&timeType=6&displayZone=%E5%8C%97%E4%BA%AC%E5%B8%82&zoneId=11&pppStatus=0&agentName=']
    # start_urls = ['http://search.ccgp.gov.cn/bxsearch?searchtype=1&bidSort=&buyerName=&projectId=&pinMu=3&bidType=1&dbselect=bidx&kw=%E5%8C%97%E4%BA%AC&start_time=2020%3A04%3A21&end_time=2020%3A04%3A22&timeType=6&displayZone=%E5%8C%97%E4%BA%AC%E5%B8%82&zoneId=11&pppStatus=0&agentName=']
    start_urls = ['http://search.ccgp.gov.cn/bxsearch?searchtype=1&bidSort=&buyerName=&projectId=&pinMu=3&bidType=1&dbselect=bidx&kw=%E5%8C%97%E4%BA%AC&start_time=2020%3A04%3A22&end_time=2020%3A04%3A23&timeType=6&displayZone=%E5%8C%97%E4%BA%AC%E5%B8%82&zoneId=11&pppStatus=0&agentName=']
    params = {"searchtype": "1",
              "page_index":"1",
              "bidSort": "",
              "buyerName": "",
              "projectId": "",
              "pinMu": "3",
              "bidType": "1",
              "dbselect": "bidx",
              "kw": "北京",
              "start_time": "2020:02:14",
              "end_time": "2020:02:17",
              "timeType": "6",
              "displayZone": "北京市",
              "zoneId": "11",
              "pppStatus": "0",
              "agentName": ""
    }
    page = 0

    # def start_requests(self):
    #     self.params['start_time'], self.params['end_time'] = self.get_timeZone()
    #     print("*************",self.params['start_time'], self.params['end_time'])
    #     url = self.basic_url+parse.urlencode(self.params)
    #     print("**************", url)
    #     yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response):
        items = response.xpath("//ul[@class='vT-srch-result-list-bid']/li")
        for item in items:
            pub_time_sub = re.findall(r'20\d{2}\.\d{2}\.\d{2} \d{2}:\d{2}:\d{2}', item.xpath('./span/text()[1]').extract_first())
            print('pub_time_sub::',pub_time_sub)
            if pub_time_sub:
                href = item.xpath("./a/@href").extract()[0]
                yield scrapy.Request(url=href, callback=self.parseItems, meta={"item": pub_time_sub[0]})
                # 读取的时间和对应的时间戳
                now_timestamp = time.mktime(time.strptime(pub_time_sub[0], "%Y.%m.%d %H:%M:%S"))
                time_zone = self.get_timeZone_stampTime()
                # print("&&&&&&&&",time_zone[0],time_zone[1])
                # print(now_timestamp)
                # print(time_zone)
                if time_zone[0] < now_timestamp <= time_zone[-1]:
                    href = item.xpath("./a/@href").extract()[0]
                    yield scrapy.Request(url=href, callback=self.parseItems, meta={"item":pub_time_sub[0]})
            # if pub_time_sub and int(pub_time_sub[0]) < 17:
            # href = item.xpath("./a/@href").extract()[0]
            # yield scrapy.Request(url=href, callback=self.parseItems)
        # 通过总量计算所需页码
        total_items = response.xpath("/html/body/div[5]/div[1]/div/p[1]/span[2]/text()").extract_first()
        for i in range(1,2):
        # if self.page <= -(-int(total_items)//20):
            print(self.page)
            self.page += 1
            page_params = self.params.copy()
            page_params['page_index'] = str(self.page)
            yield scrapy.Request(self.basic_url + parse.urlencode(page_params), callback=self.parse)

    def parseItems(self, response):
        trs = response.xpath("//div[@class='table']/table/tr")
        print(self.getText(item=response, xpathString="//h2[@class='tc']/text()"))
        publish_time = response.meta['item']
        if not publish_time:
            publish_time = ''

        yield CcgpItem({
            'title' : self.getText(item=response, xpathString="//h2[@class='tc']/text()"),#标题
            'publish':publish_time,  # 发布时间
            'budget' : self.getText(item=trs[10], xpathString="string(./td[2])"),# 预算金额
            'project' : self.getText(item=trs[1], xpathString="string(./td[2])"), #采购项目名称
            'type' : self.getText(item=trs[2], xpathString="string(./td[2])"),#品目
            'company' : self.getText(item=trs[3], xpathString="string(./td[2])"), #采购单位
            'noticeTime' :   self.getText(item=trs[4], xpathString="string(./td[4])"),#公告时间
            'priceTime' :  self.getText(item=trs[5], xpathString="string(./td[2])") ,#获取招标问价时间
            'openTime' : self.getText(item=trs[8], xpathString="string(./td[2])"), #开标时间
            'address' : self.getText(item=trs[9], xpathString="string(./td[2])"),#开标地点
            'href' : response.url
        })

    def getText(self, item, xpathString):
        return item.xpath(xpathString).extract()[0].replace(u'\xa0', u'')

    def get_timeZone_stampTime(self, offset=-1):
        today = datetime.now()
        offset_day = timedelta(days=offset)
        last_one_day = (today + offset_day).strftime('%Y.%m.%d 17:00:00')
        # last_one_day = '2020.04.15 17:00:00'
        bid_today = time.strftime("%Y.%m.%d 17:00:00", time.localtime())
        # bid_today = '2020.04.16 17:00:00'
        print(last_one_day, bid_today)
        return [time.mktime(time.strptime(i, "%Y.%m.%d %H:%M:%S")) for i in [last_one_day, bid_today]]

    def get_timeZone(self, offset=-1):
        today = datetime.now()
        offset_day = timedelta(days=offset)
        return (today + offset_day).strftime('%Y:%m:%d'), time.strftime("%Y:%m:%d", time.localtime())


    def get_timeZone_stampTime2(self, offset=-1):
        today = datetime.now()
        offset_day = timedelta(days=-3)
        last_one_day = (today + offset_day).strftime('%Y.%m.%d 17:00:00')
        bid_today = time.strftime("%Y.%m.%d 17:00:00", time.localtime())
        last_two_day = (today + timedelta(days=-3)).strftime('%Y.%m.%d 17:00:00')
        print("today::", today)
        print("last_two_day::", last_two_day)
        return [time.mktime(time.strptime(i, "%Y.%m.%d %H:%M:%S")) for i in [last_two_day,today]]

    def get_timeZone2(self, offset=-1):
        today = datetime.now()
        offset_day = timedelta(days=-3)
        return (today + offset_day).strftime('%Y:%m:%d'), today.strftime('%Y:%m:%d')