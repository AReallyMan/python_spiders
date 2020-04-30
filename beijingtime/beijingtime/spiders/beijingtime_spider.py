# -*- coding: utf-8 -*-
import json
from ..items import BeijingtimeItem
import scrapy
import re
import time
from urllib import parse
import datetime
from ..settings import ELASTICSEARCH_TYPE, ELASTICSEARCH_INDEX


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


class BeijingtimeSpiderSpider(scrapy.Spider):
    name = 'beijingtime_spider'
    allowed_domains = ['btime.com']
    today = datetime.date.today()
    basic_url = 'https://pc.api.btime.com/btimeweb/getInfoFlow?'
    params = {
        'callback': 'jQuery111307376818355006773_1586481929706',
        'channel': 'news',
        'request_pos': 'channel',
        'citycode': 'local_610100_610000',
        'refresh': '2',
        'req_count': '2',
        'refresh_type': '2',
        'pid': '3',
        'from': '',
        'offset': '0',
        'page_refresh_id': '283ff756-7aca-11ea-8a42-6c92bf437bb2',
        'page': '2',
        '_': '1585284594352',
    }

    def start_requests(self):
        params = self.params.copy()
        flag1_page = 0
        flag2 = 2
        now = datetime.datetime.now()
        # 今日0点
        zeroToday = now - datetime.timedelta(hours=now.hour, minutes=now.minute, seconds=now.second,
                                             microseconds=now.microsecond)
        zeroarray = time.strptime(str(zeroToday), "%Y-%m-%d %H:%M:%S")
        zerostamp = str(time.mktime(zeroarray)).split(".")[0] + "000"  # 今日0点时间戳
        # indexPageStamp = int(params['_'])
        # 当前时间的时间戳
        millisStamp = int(round(time.time() * 1000))
        for i in range(int(zerostamp), millisStamp):
            params['_'] = i
            url = self.basic_url + parse.urlencode(params)
            flag1_page += 12
            flag2 += 1
            params['refresh'] = flag2
            params['req_count'] = flag2
            params['offset'] = flag1_page
            params['page'] = flag2
            if flag2 > 80:
                break
            yield scrapy.Request(url=url, callback=self.getlist)

    def getlist(self, response):
        JSONPdata = response.text
        url = response.url
        if self.duplicate.redis_db.hexists(self.duplicate.redis_data_dict, url):
            print("该连接已被爬取")
        else:
            datas = json.loads(re.match(".*?({.*}).*", JSONPdata, re.S).group(1))
            # if 'data' in datas:
            if datas['data']:
                for datalist in datas['data']:
                    if "create_name" in datalist['data']:
                        pdate, title, publishtime, fromwhere, editor = int(datalist['data']['pdate']), datalist['data']['title'], time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(int(datalist['data']['pdate']))), datalist['data']['source'], datalist['data']['create_name']
                        if getStampIn24(pdate):
                            item = BeijingtimeItem()
                            item['title'] = title
                            item['publishtime'] = publishtime
                            item['fromwhere'] = fromwhere
                            item['editor'] = editor
                            yield scrapy.Request(url=datalist['open_url'], meta={"item": item}, callback=self.getdetail)

    def getdetail(self, response):
        item = response.meta['item']
        item['url'] = response.url
        res = response.text
        data = res[res.find('page_data:') + len('page_data:'): res.find('layoutData')].strip()
        data = json.loads(data[:len(data) - 1])
        contents = ''
        for content in data['content']:
            if 'type' in content:
                if content['type'] == 'txt':
                    contents += content['value']
        if contents:
            contents = re.findall(u"[\u4e00-\u9fa5]+", contents)
            item['content'] = ''.join(contents)
        else:
            item['content'] = ''
        item['spiderName'] = ELASTICSEARCH_TYPE
        item['spiderDesc'] = '北京时间'
        item['siteType'] = '纸媒'
        item['source'] = '北京时间'
        item['publicTimeStamp'] = int(time.mktime(self.today.timetuple()))
        item['insertTimeStamp'] = int(time.time() * 1000)
        yield item

