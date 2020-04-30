# -*- coding: utf-8 -*-
import re

import scrapy
from scrapy.spiders import Rule, CrawlSpider
from scrapy.linkextractors import LinkExtractor
import time
import datetime
from ..items import ShenzhennewsItem
from ..settings import ELASTICSEARCH_TYPE


#深圳新闻网
class ShenzhennewsSpiderSpider(CrawlSpider):
    name = 'shenzhenNews_spider'
    #allowed_domains = ['sznews.com']
    current_time = time.strftime("%Y-%m/%d", time.localtime())
    today = datetime.date.today()
    start_urls = ['http://www.sznews.com/news/node_18235.htm', 'http://news.sznews.com/node_18029.htm',
                  'http://news.sznews.com/node_134907.htm', 'http://news.sznews.com/node_31220.htm',
                  'http://news.sznews.com/node_18236.htm', 'http://news.sznews.com/node_150128.htm',
                  'http://www.sznews.com/news/node_227703.htm']
    rules = {
        Rule(LinkExtractor(allow='\_[2-6]\.htm')),
        Rule(LinkExtractor(allow='http://www.sznews.com/news/content/'+current_time+'/content_\d+\.htm'),
             callback='parse_item'),
        Rule(LinkExtractor(allow='http://news.sznews.com/content/'+current_time+'/content_\d+\.htm'),
             callback='parse_item'),
    }

    def parse_item(self, response):
        item = ShenzhennewsItem()
        if self.duplicate.redis_db.hexists(self.duplicate.redis_data_dict, response.url):
            print("该连接已被爬取")
        else:

            item['url'] = response.url
            title = response.xpath("//h1[@class='h1-news']/text()[2]").extract_first()
            if title:
                item['title'] = title
            else:
                item['title'] = response.xpath("//h1[@class='h1-news']/text()").extract_first()
            try:
                content = response.xpath("//div[@class='article-content cf new_txt']").xpath('string(.)').extract_first()
                if content:
                    content = re.findall(u"[\u4e00-\u9fa5]+", content)
                    item['content'] = ''.join(content)
            except KeyError:
                print("图片新闻")
            publishtime = response.xpath("//div[@class='share yahei cf']/div/div/text()").extract_first()
            if publishtime:
                item['publishtime'] = publishtime
            else:
                item['publishtime'] = response.xpath("//div[@class='fs18 r share-date']/text()").extract_first()
            fromwhere = response.xpath("//div[@class='share yahei cf']/div/div/span/text()").extract_first()
            if fromwhere:
                item['fromwhere'] = fromwhere
            else:
                item['fromwhere'] = response.xpath("//span[@class='ml10']/text()").extract_first()
            item['editor'] = response.xpath("//span[@class='r']/text()").extract_first()
            item['spiderName'] = ELASTICSEARCH_TYPE
            item['spiderDesc'] = '深圳新闻网'
            item['siteType'] = '新闻'
            item['source'] = '深圳新闻网'
            item['publicTimeStamp'] = int(time.mktime(self.today.timetuple()))
            item['insertTimeStamp'] = int(time.time() * 1000)
            yield item