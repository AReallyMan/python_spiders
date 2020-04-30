# -*- coding: utf-8 -*-
import json
import re

import scrapy
import time
import datetime
from ..items import ChinafarmerItem
from ..settings import ELASTICSEARCH_INDEX, ELASTICSEARCH_TYPE


#中国农网
class ChainfarmerSpiderSpider(scrapy.Spider):
    name = 'chinafarmer_spider'
    allowed_domains = ['farmer.com.cn']
    start_urls = [
        'http://www.farmer.com.cn/xbpd/xw/szxw_874/NewsList_',
        'http://www.farmer.com.cn/xbpd/xw/rdjj_2458/NewsList_',
        'http://www.farmer.com.cn/xbpd/xw/jsbd_1051/NewsList_',
        'http://www.farmer.com.cn/xbpd/sx/sp/NewsList_',
        'http://www.farmer.com.cn/xbpd/sx/zjgd_902/NewsList_',
        'http://www.farmer.com.cn/xbpd/df/kx/NewsList_',
        'http://www.farmer.com.cn/xbpd/df/dfxw_2459/NewsList_',
        'http://www.farmer.com.cn/xbpd/wl/wh/NewsList_',
        'http://www.farmer.com.cn/xbpd/kj/nykjcx_2437/NewsList_',
        'http://www.farmer.com.cn/xbpd/al/xwrw_2468/NewsList_'
    ]
    param = {
        'page': '0',
        'end': '.json'
    }

    today = datetime.date.today()
    current_time = time.strftime("%Y-%m-%d", time.localtime())

    def start_requests(self):
        param = self.param.copy()
        page = int(param['page'])
        end = str(param['end'])
        for i in range(page, 10):
            for url in self.start_urls:
                url_page = url + str(page) + end
                yield scrapy.Request(url=url_page, callback=self.getlist)

    def getlist(self, response):
        JSONPdata = response.text
        datas = json.loads(re.match(".*?({.*}).*", JSONPdata, re.S).group(1))
        for datalist in datas['info']:
            createTime = datalist['createTime']
            print(createTime)
            if self.current_time == createTime:
                title, url, source = datalist['ovtitle'], datalist['url'], datalist['source']
                item = ChinafarmerItem()
                item['title'] = title
                item['url'] = url
                item['source'] = source
                if self.duplicate.redis_db.hexists(self.duplicate.redis_data_dict, url):
                    print("该连接已被爬取")
                else:
                    yield scrapy.Request(url=url, meta={"item": item}, callback=self.getmsg)

            else:
                print("排除不是今天的数据")

    def getmsg(self, response):
        print(response.url)
        item = response.meta['item']
        item['createTime'] = response.xpath("//span[@class='article-meta-time']/text()").extract_first()
        item['editor'] = response.xpath("//span[@class='tag-text'][1]/text()").extract_first()
        item['author'] = response.xpath("//span[@class='tag-text'][2]/text()").extract_first()
        item['content'] = response.xpath("//div[@id='article_main']").xpath('string(.)').extract_first()
        item['spiderName'] = ELASTICSEARCH_TYPE
        item['spiderDesc'] = '中国农网'
        item['siteType'] = '农网'
        item['source'] = '中国农网'
        item['publicTimeStamp'] = int(time.mktime(self.today.timetuple()))
        item['insertTimeStamp'] = int(time.time() * 1000)
        yield item



