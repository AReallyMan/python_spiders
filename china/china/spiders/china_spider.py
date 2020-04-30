# -*- coding: utf-8 -*-
import scrapy
from scrapy.spiders import Rule, CrawlSpider
from scrapy.linkextractors import LinkExtractor
import time
import datetime
from ..items import ChinaItem
from ..settings import ELASTICSEARCH_INDEX, ELASTICSEARCH_TYPE


class ChainSpiderSpider(CrawlSpider):
    name = 'china_spider'
    allowed_domains = ['china.com.cn']
    start_urls = ['http://news.china.com.cn/']
    today = datetime.date.today()
    current_time = time.strftime("%Y-%m/%d", time.localtime())

    rules = {
        Rule(LinkExtractor(allow='http://news.china.com.cn/'+current_time+'/content_\d{8}\.htm'),
             callback='parse_item'),
        Rule(LinkExtractor(allow='http://news.china.com.cn/txt/'+current_time+'/content_\d{8}.htm'),
             callback='parse_item'),
        Rule(LinkExtractor(allow='http://military.china.com.cn/'+current_time+'/content_\d{8}.htm'),
             callback='parse_item'),

    }

    def parse_item(self, response):
        item = ChinaItem()
        url = response.url
        if self.duplicate.redis_db.hexists(self.duplicate.redis_data_dict, url):
            print("该连接已被爬取")
        else:
            item['timetoday'] = response.xpath("//span[@id='pubtime_baidu']/text()").extract_first()
            fromwhere = response.xpath("//span[@id='source_baidu']/a/text()").extract_first()
            if fromwhere is None:
                item['fromwhere'] = response.xpath("//span[@id='source_baidu']/text()").extract_first()
            else:
                item['fromwhere'] = fromwhere
            title = response.xpath("//h1[@class='articleTitle']/text()").extract_first()
            title_second = response.xpath("//h1[@class='artTitle']/text()").extract_first()
            if title is None and title_second is None:
                item['title'] = response.xpath("//h1[@class='artiTitle clearB']/text()").extract_first()
            elif title is None and title_second is not None:
                item['title'] = title_second
            else:
                item['title'] = title
            item['author'] = response.xpath("//span[@id='author_baidu']/text()").extract_first()
            content = response.xpath("//div[@id='articleBody']").xpath('string(.)').extract_first()
            content_second = response.xpath("//div[@class='artCon']").xpath('string(.)').extract_first()
            if content is None and content_second is None:
                item['content'] = response.xpath("//div[@class='artiContent']").xpath('string(.)').extract_first()
            elif content is None and content_second is not None:
                item['content'] = content_second
            else:
                item['content'] = content
            item['url'] = response.url
            item['spiderName'] = ELASTICSEARCH_TYPE
            item['spiderDesc'] = '中国网'
            item['siteType'] = '纸媒'
            item['source'] = '中国网'
            item['publicTimeStamp'] = int(time.mktime(self.today.timetuple()))
            item['insertTimeStamp'] = int(time.time() * 1000)
            yield item

