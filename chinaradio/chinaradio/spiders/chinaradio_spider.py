# -*- coding: utf-8 -*-
import scrapy
from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor
from ..items import ChinaradioItem
import time
from ..settings import ELASTICSEARCH_INDEX, ELASTICSEARCH_TYPE
import datetime


class ChinaradioSpiderSpider(CrawlSpider):
    name = 'chinaradio_spider'
    #allowed_domains = ['cnr.cn']
    start_urls = ['http://news.cnr.cn/native/', 'http://news.cnr.cn/gjxw/', 'http://news.cnr.cn/dj/', 'http://news.cnr.cn/local/', 'http://news.cnr.cn/comment/', 'http://news.cnr.cn/theory/', 'http://military.cnr.cn/', 'http://ent.cnr.cn/']
    current_time = time.strftime("%Y%m%d", time.localtime())
    today = datetime.date.today()
    rules = {
        Rule(LinkExtractor(allow='index_[1-5]\.html'), follow=True),
        Rule(LinkExtractor(allow='http://news.cnr.cn/native/gd/' + current_time + '/t' + current_time + '_\d{9}\.shtml'), callback='parse_item'),
        Rule(LinkExtractor(allow='http://news.cnr.cn/gjxw/gnews/'+current_time+'/t' + current_time + '_\d{9}\.shtml'), callback='parse_item'),
        Rule(LinkExtractor(allow='http://china.cnr.cn/yaowen/' + current_time + '/t' + current_time + '_\d{9}\.shtml'), callback='parse_item'),
        Rule(LinkExtractor(allow='http://news.cnr.cn/native/city/' + current_time + '/t' + current_time + '_\d{9}\.shtml'), callback='parse_item'),
        Rule(LinkExtractor(allow='http://news.cnr.cn/native/comment/' + current_time + '/t' + current_time + '_\d{9}\.shtml'), callback='parse_item'),
        Rule(LinkExtractor(allow='http://news.cnr.cn/native/gd/' + current_time + '/t' + current_time + '_\d{9}\.shtml'), callback='parse_item'),
        Rule(LinkExtractor(allow='http://military.cnr.cn/ycdj/' + current_time + '/t' + current_time + '_\d{9}\.html'), callback='parse_item'),
        Rule(LinkExtractor(allow='http://ent.cnr.cn/zx/' + current_time + '/t' + current_time + '_\d{9}\.shtml'), callback='parse_item'),
    }

    def parse_item(self, response):
        item = ChinaradioItem()
        url = response.url
        title = response.xpath("//div[@class='article-header']/h1/text()").extract_first()
        if self.duplicate.redis_db.hexists(self.duplicate.redis_data_dict, url):
            print("该连接已被爬取")
        else:
            if title is None:
                item['title'] = response.xpath("//h1[@class='f24 lh40 fb txtcenter f12_292929 yahei']/text()").extract_first()
            else:
                item['title'] = title

            publishtime = response.xpath("//div[@class='article-header']/div/span[1]/text()").extract_first()
            if publishtime is None:
                item['publishtime'] = response.xpath("//span[@id='pubtime_baidu']/text()").extract_first()
            else:
                item['publishtime'] = publishtime
            fromwhere = response.xpath("//div[@class='article-header']/div/span[2]/text()").extract_first()
            if fromwhere is None:
                item['fromwhere'] = response.xpath("//span[@id='source_baidu']/a/text()").extract_first()
            else:
                item['fromwhere'] = fromwhere
            content = response.xpath("//div[@class='TRS_Editor']").xpath('string(.)').extract_first()
            if content is None:
                item['content'] = response.xpath("//div[@class='TRS_Editor']/div']").xpath('string(.)').extract_first()
            else:
                item['content'] = content
            editor = response.xpath("//div[@class='editor']/text()").extract_first()
            if editor is None:
                item['editor'] = response.xpath("//p[@class='right mr10 lh24 f14 fb f12_292929']/text()").extract_first()
            else:
                item['editor'] = editor
            item['url'] = response.url

            item['spiderName'] = ELASTICSEARCH_TYPE
            item['spiderDesc'] = '中央人民广播电台'
            item['siteType'] = '广播电台'
            item['source'] = '中央人民广播电台'
            item['publicTimeStamp'] = int(time.mktime(self.today.timetuple()))
            item['insertTimeStamp'] = int(time.time() * 1000)
            yield item