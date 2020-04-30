# -*- coding: utf-8 -*-
import re

import scrapy
from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor
import datetime
from ..items import ChinazxcmItem
import time
from ..settings import  ELASTICSEARCH_TYPE


class ChinazxcmSpiderSpider(CrawlSpider):
    name = 'chinazxcm_spider'
    current_time = time.strftime("%Y-%m/%d", time.localtime())
    today = datetime.date.today()
    #allowed_domains = ['zgzx.com.cn']
    start_urls = ['http://xw.zgzx.com.cn/node_44481.htm', 'http://xw.zgzx.com.cn/node_44478.htm',
                  'http://xw.zgzx.com.cn/node_44479.htm', 'http://xw.zgzx.com.cn/node_44480.htm',
                  'http://xw.zgzx.com.cn/node_44474.htm', 'http://lz.zgzx.com.cn/node_44519.htm',
                  'http://lz.zgzx.com.cn/node_44517.htm', 'http://lz.zgzx.com.cn/node_44556.htm',
                  'http://lz.zgzx.com.cn/node_44518.htm', 'http://lz.zgzx.com.cn/node_44516.htm',
                  'http://lz.zgzx.com.cn/node_44514.htm', 'http://ll.zgzx.com.cn/node_44675.htm',
                  'http://wh.zgzx.com.cn/node_44509.htm'
                  ]
    rules = {
        Rule(LinkExtractor(allow='node_\d{5}_[2-9]\.htm')),
        Rule(LinkExtractor(allow='http://[a-z]{2}.zgzx.com.cn/'+current_time+'/content_\d{7}\.htm'), callback='getList')
    }

    def getList(self, response):
        item = ChinazxcmItem()
        url = response.url
        if self.duplicate.redis_db.hexists(self.duplicate.redis_data_dict, url):
            print("该连接已被爬取")
        else:
            title = response.xpath("//h1[@id='articleTitle']/text()").extract_first()
            if title:
                item['title'] = title
            else:
                item['title'] = response.xpath("//h1[@class='picContentHeading']/text()").extract_first()
            publish_where = response.xpath("//div[@class='source']/p/text()").extract_first()
            # 2020-04-22 09:25:14
            if publish_where:
                fromwhere = re.findall(u"[\u4e00-\u9fa5]+", publish_where)
                fromwhere2 = ''.join(fromwhere)
                publishtime = re.findall("\d{4}-\d{2}-\d{2}[\s\t\n]+\d{2}:\d{2}:\d{2}", publish_where)
                publishtime2 = ''.join(publishtime)
            publishtime = response.xpath("//span[@id='pubTime']/text()").extract_first()
            if publishtime:
                item['publishtime'] = publishtime
            else:
                item['publishtime'] = publishtime2
            fromwhere = response.xpath("//span[@id='source']/text()").extract_first()
            fromwhereA = response.xpath("//span[@id='source']/a/text()").extract_first()
            if fromwhereA:
                item['fromwhere'] = fromwhereA
            elif fromwhere:
                item['fromwhere'] = fromwhere
            else:
                item['fromwhere'] = fromwhere2
            content = response.xpath("//div[@id='contentMain']").xpath('string(.)').extract_first()
            content2 = response.xpath("//div[@id='ArticleContent']/div/div/div").xpath('string(.)').extract_first()
            if content:
                content = re.findall(u"[\u4e00-\u9fa5]+", content)
                item['content'] = ''.join(content)
            elif content2:
                content2 = re.findall(u"[\u4e00-\u9fa5]+", content2)
                item['content'] = ''.join(content2)
            else:
                item['content'] = ''
            editor = response.xpath("//div[@id='contentLiability']/text()").extract_first()
            if editor:
                item['editor'] = editor
            else:
                item['editor'] = response.xpath("//span[@class='zb']/text()").extract_first()
            item['url'] = url
            item['spiderName'] = ELASTICSEARCH_TYPE
            item['spiderDesc'] = '中国政协传媒网'
            item['siteType'] = '新闻'
            item['source'] = '中国政协传媒网'
            item['publicTimeStamp'] = int(time.mktime(self.today.timetuple()))
            item['insertTimeStamp'] = int(time.time() * 1000)
            yield item
