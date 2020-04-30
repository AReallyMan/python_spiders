# -*- coding: utf-8 -*-
import scrapy
from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor
import time
import datetime
from ..items import ChinajwItem
from ..settings import ELASTICSEARCH_INDEX, ELASTICSEARCH_TYPE


class ChainjwSpiderSpider(CrawlSpider):
    name = 'chinajw_spider'
    allowed_domains = ['81.cn']
    start_urls = ['http://www.81.cn/', 'http://www.81.cn/jmywyl/index.htm']
    current_time = time.strftime("%Y-%m/%d", time.localtime())
    today = datetime.date.today()
    rules = {
        Rule(LinkExtractor(allow='http://www.81.cn/jmywyl/index_[2-9]\.htm')),
        Rule(LinkExtractor(allow='http://www.81.cn/jmywyl/'+current_time+'/content_\d{7}.htm'), callback='parse_item'),
        Rule(LinkExtractor(allow='http://www.81.cn/[a-z]{2,6}/'+current_time+'/content_\d{7}.htm'), callback='parse_item')
    }

    def parse_item(self, response):
        item = ChinajwItem()
        url = response.url
        if self.duplicate.redis_db.hexists(self.duplicate.redis_data_dict, url):
            print("该连接已被爬取")
        else:
            item['url'] = url
            title = response.xpath("//div[@class='article-header']/h1/text()").extract_first()
            if title is None:
                item['title'] = response.xpath("//div[@class='container artichle-info']/h2/text()").extract_first()
            else:
                item['title'] = title
            item['content'] = response.xpath("//div[@id='article-content']").xpath('string(.)').extract_first()
            fromwhere = response.xpath("//div[@class='info']/span[1]/text()").extract_first()
            if fromwhere is None:
                item['fromwhere'] = response.xpath("//div[@class='container artichle-info']/p/span/a/text()").extract_first()
            else:
                item['fromwhere'] = fromwhere
            author = response.xpath("//div[@class='info']/span[3]/text()").extract_first()
            if author is None:
                item['author'] = response.xpath("//span[@id='author-info']/text()").extract_first()
            else:
                item['author'] = author
            publishtime = response.xpath("//div[@class='info']/div/small/i[1]/text()").extract_first()
            if publishtime is None:
                item['publishtime'] = response.xpath("//div[@class='container artichle-info']/p/span[3]/text()").extract_first()
            else:
                item['publishtime'] = publishtime
            item['spiderName'] = ELASTICSEARCH_TYPE
            item['spiderDesc'] = '中国军网'
            item['siteType'] = '军网'
            item['source'] = '中国军网'
            item['publicTimeStamp'] = int(time.mktime(self.today.timetuple()))
            item['insertTimeStamp'] = int(time.time() * 1000)
            yield item