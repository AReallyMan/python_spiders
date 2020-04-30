# -*- coding: utf-8 -*-
import scrapy
from scrapy.spiders import Rule, CrawlSpider
import time
from ..items import TakungpaoItem
from scrapy.linkextractors import LinkExtractor
from ..settings import ELASTICSEARCH_INDEX, ELASTICSEARCH_TYPE
import datetime


class TakungpaoSpiderSpider(CrawlSpider):
    name = 'takungpao_spider'
    allowed_domains = ['takungpao.com']
    current_time = time.strftime("%m%d", time.localtime())
    start_urls = ['http://www.takungpao.com/opinion/index.html', 'http://www.takungpao.com/news/index.html']
    today = datetime.date.today()
    rules = {
        Rule(LinkExtractor(allow='http://www.takungpao.com/news/[0-9]{6}/2020/' + current_time + '/[0-9]{6}\.html'),
             callback='parse_item'),
        Rule(LinkExtractor(allow='http://www.takungpao.com/opinion/\d{6}/2020/'+current_time+'/\d{6}\.html'),
             callback='parse_item'),
    }

    def parse_item(self, response):
        item = TakungpaoItem()
        url = response.url
        if self.duplicate.redis_db.hexists(self.duplicate.redis_data_dict, url):
            print("该连接已被爬取")
        else:
            item['timetoday'] = response.xpath("//div[@class='tkp_con_author']/span[1]/text()").extract_first()
            fromwhere = response.xpath("//div[@class='tkp_con_author']/span[2]/text()").extract_first()
            if fromwhere is None:
                item['fromwhere'] = response.xpath("//div[@class='tkp_con_author']/span[2]/a/text()").extract_first()
            else:
                item['fromwhere'] = fromwhere
            author = response.xpath("//div[@class='tkp_con_author']/text()").extract_first()
            if author is None:
                item['author'] = ''
            else:
                item['author'] = author
            item['title'] = response.xpath("//h2[@class='tkp_con_title']/text()").extract_first()
            item['content'] = response.xpath("//div[@class='tkp_content']").xpath('string(.)').extract_first()
            item['url'] = response.url
            item['spiderName'] = ELASTICSEARCH_TYPE
            item['spiderDesc'] = '大公网'
            item['siteType'] = '新闻媒体'
            item['source'] = '大公网'
            item['publicTimeStamp'] = int(time.mktime(self.today.timetuple()))
            item['insertTimeStamp'] = int(time.time() * 1000)
            yield item
