# -*- coding: utf-8 -*-
import re

import scrapy
from scrapy.spiders import Rule, CrawlSpider
from scrapy.linkextractors import LinkExtractor
import time
import datetime
from ..items import ShanximediaItem
from ..settings import ELASTICSEARCH_TYPE


#陕西传媒网
class ShanximediaSpiderSpider(CrawlSpider):
    name = 'shanxiMedia_spider'
    #allowed_domains = ['sxdaily.com.cn']
    current_time = time.strftime("%Y-%m/%d", time.localtime())
    today = datetime.date.today()
    # nums = [841, 842, 1024, 791, 1066, 1726, 1911]
    # for num in nums:
    #     start_urls = ['https://www.sxdaily.com.cn/node_'+str(num)+'.html']
    start_urls = ['https://www.sxdaily.com.cn/node_841.html', 'https://www.sxdaily.com.cn/node_842.html',
                  'https://www.sxdaily.com.cn/node_1024.html', 'https://www.sxdaily.com.cn/node_791.html',
                  'https://www.sxdaily.com.cn/node_1066.html', 'https://www.sxdaily.com.cn/node_1726.html',
                  'https://www.sxdaily.com.cn/node_1911.html']
    rules = {
        Rule(LinkExtractor(allow='\_[2-6]\.html')),
        Rule(LinkExtractor(allow='https://www.sxdaily.com.cn/'+current_time+'/content_\d+\.html'),
             callback='parse_item'),
    }

    def parse_item(self, response):
        item = ShanximediaItem()
        if self.duplicate.redis_db.hexists(self.duplicate.redis_data_dict, response.url):
            print("该连接已被爬取")
        else:
            item['url'] = response.url
            item['title'] = response.xpath("//div[@class='container title']/h1/text()").extract_first()
            item['author'] = response.xpath("//div[@class='container title']/p/text()").extract_first()
            content = response.xpath("//div[@id='zoom']").xpath('string(.)').extract_first()
            if content:
                content = re.findall(u"[\u4e00-\u9fa5]+", content)
                item['content'] = ''.join(content)
            item['publishtime'] = response.xpath("//div[@class='container title']/div/p[1]/text()").extract_first()
            item['fromwhere'] = response.xpath("//p[@id='source']/text()").extract_first()
            item['editor'] = response.xpath("//div[@class='editor']/text()").extract_first()

            item['spiderName'] = ELASTICSEARCH_TYPE
            item['spiderDesc'] = '陕西传媒网'
            item['siteType'] = '新闻'
            item['source'] = '陕西传媒网'
            item['publicTimeStamp'] = int(time.mktime(self.today.timetuple()))
            item['insertTimeStamp'] = int(time.time() * 1000)
            yield item