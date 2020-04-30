# -*- coding: utf-8 -*-
import scrapy
from scrapy.spiders import Rule, CrawlSpider
from scrapy.linkextractors import LinkExtractor
import time
from ..items import QstheoryItem
from ..settings import ELASTICSEARCH_INDEX, ELASTICSEARCH_TYPE
import datetime


class QstheorySpiderSpider(CrawlSpider):
    name = 'qstheory_spider'
    allowed_domains = ['qstheory.cn']
    today = datetime.date.today()
    start_urls = ['http://www.qstheory.cn/', 'http://www.qstheory.cn/economy/index.htm', 'http://www.qstheory.cn/politics/index.htm', 'http://www.qstheory.cn/culture/index.htm', 'http://www.qstheory.cn/society/index.htm', 'http://www.qstheory.cn/cpc/index.htm', 'http://www.qstheory.cn/science/index.htm', 'http://www.qstheory.cn/zoology/index.htm', 'http://www.qstheory.cn/defense/index.htm', 'http://www.qstheory.cn/international/index.htm', 'http://www.qstheory.cn/qswp.htm']
    current_time = time.strftime("%Y-%m/%d", time.localtime())
    rules = {
        Rule(LinkExtractor(allow='http://www.qstheory.cn/[a-z]{2,8}/'+current_time+'/c_\d{10}.htm'), callback='parse_item'),
    }

    def parse_item(self, response):
        item = QstheoryItem()
        url = response.url
        if self.duplicate.redis_db.hexists(self.duplicate.redis_data_dict, url):
            print("该连接已被爬取")
        else:
            title = response.xpath("//div[@class='headtitle']/h1/text()").extract_first()
            if title is None:
                item['title'] = response.xpath("//div[@class='inner']/h1/text()").extract_first()
            else:
                item['title'] = title
            timetoday = response.xpath("//div[@class='headtitle']/span/text()").extract_first()
            if timetoday is None:
                item['timetoday'] = response.xpath("//div[@class='inner']/span[3]/text()").extract_first()
            else:
                item['timetoday'] = timetoday
            fromwhere_author = response.xpath("//div[@class='headtitle']/text()[5]").extract_first()
            if fromwhere_author is None:
                item['fromwhere_author'] = response.xpath("//div[@class='inner']/span[2]/text()").extract_first() + response.xpath("//div[@class='inner']/span[1]/text()").extract_first()
            else:
                item['fromwhere_author'] = fromwhere_author
            content = response.xpath("//div[@class='highlight']").xpath('string(.)').extract_first()
            if content is None:
                item['content'] = response.xpath("//div[@class='text']").xpath('string(.)').extract_first()
            else:
                item['content'] = content
            item['url'] = response.url
            item['spiderName'] = ELASTICSEARCH_TYPE
            item['spiderDesc'] = '求是网'
            item['siteType'] = '新闻媒体'
            item['source'] = '求是网'
            item['publicTimeStamp'] = int(time.mktime(self.today.timetuple()))
            item['insertTimeStamp'] = int(time.time() * 1000)
            yield item

