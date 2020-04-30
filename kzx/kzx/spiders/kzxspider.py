# -*- coding: utf-8 -*-
import json
import re
import time
from urllib import parse
from ..items import KzxItem
import scrapy
import datetime
from ..settings import ELASTICSEARCH_INDEX, ELASTICSEARCH_TYPE


def getStampIn24(timeStamp):
    now = datetime.datetime.now()
    # 今日0点
    zeroToday = now - datetime.timedelta(hours=now.hour, minutes=now.minute, seconds=now.second,
                                         microseconds=now.microsecond)
    # 今日23点59分59秒
    lastToday = zeroToday + datetime.timedelta(hours=23, minutes=59, seconds=59)
    zeroToday = str(zeroToday)
    lastToday = str(lastToday)
    zeroarray = time.strptime(zeroToday, "%Y-%m-%d %H:%M:%S")
    zerostamp = int(time.mktime(zeroarray))
    lastarray = time.strptime(lastToday, "%Y-%m-%d %H:%M:%S")
    laststamp = int(time.mktime(lastarray))
    if zerostamp < timeStamp < laststamp:
        return True
    else:
        return False


class KzxspiderSpider(scrapy.Spider):
    name = 'kzxspider'
    today = datetime.date.today()
    basic_url = 'https://papi.look.360.cn/tag_list?'
    params = {
        'callback': 'jQuery19106178612557609684_1585284594351',
        'scene': 'nh3_1',
        'refer_scene': 'nh3_1',
        'u': '91873708a94da6274c0e504c3c0bdb33',
        'sign': 'look',
        'sqid': '',
        'n': '20',
        'stype': 'portal',
        'tj_cmode': 'pclook',
        'tj_url': '',
        'version': '2.0',
        'device': '2',
        'action': '2',
        'ufrom': '1',
        'sv': '4',
        'net': '4',
        'market': 'pc_def',
        'where': 'new_third',
        'v': '1',
        'f': 'jsonp',
        'scheme': 'https',
        'c': 'y1:newhot2019nCoV',
        'clsclass': 'y1:newhot2019nCoV',
        '_': '1585284594352',
    }

    def start_requests(self):
        flag = 0
        params = self.params.copy()
        # indexPageStamp = int(params['_'])
        now = datetime.datetime.now()
        # 今日0点
        zeroToday = now - datetime.timedelta(hours=now.hour, minutes=now.minute, seconds=now.second,
                                             microseconds=now.microsecond)
        zeroarray = time.strptime(str(zeroToday), "%Y-%m-%d %H:%M:%S")
        zerostamp = str(time.mktime(zeroarray)).split(".")[0] + "000" #今日0点时间戳
        # 当前时间的时间戳
        millisStamp = int(round(time.time() * 1000))
        for i in range(int(zerostamp), millisStamp):
            flag += 1
            params['_'] = i
            url = self.basic_url + parse.urlencode(params)
            if flag < 300:
                yield scrapy.Request(url=url, callback=self.getlist)
            else:
                break

    def getlist(self, response):
        JSONPdata = response.text
        url = response.url
        if self.duplicate.redis_db.hexists(self.duplicate.redis_data_dict, url):
            print("该连接已被爬取")
        else:
            datas = json.loads(re.match(".*?({.*}).*", JSONPdata, re.S).group(1))
            if 'data' in datas:
                for datalist in datas['data']['res']:
                    p, title, publishtime, fromwhere = int(datalist['p']), datalist['t'], time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(int(datalist['p']))), datalist['f']
                    if getStampIn24(p):
                        item = KzxItem()
                        item['title'] = title
                        item['publishtime'] = publishtime
                        item['fromwhere'] = fromwhere
                        yield scrapy.Request(url=datalist['pcurl'], meta={"item": item}, callback=self.getDetail)

    def getDetail(self, response):
        item = response.meta['item']
        item['url'] = response.url
        item['spiderName'] = ELASTICSEARCH_TYPE
        item['spiderDesc'] = '快资讯'
        item['siteType'] = '资讯网站'
        item['source'] = '快资讯'
        item['publicTimeStamp'] = int(time.mktime(self.today.timetuple()))
        item['insertTimeStamp'] = int(time.time() * 1000)
        content = re.findall(r'"content":(.*?)\,', response.text)
        if content:
            content = content[0].encode('utf-8').decode('unicode_escape')
            content = re.findall(u"[\u4e00-\u9fa5]+", content)
            item['content'] = ''.join(content)
        else:
            item['content'] = ''
        yield item
