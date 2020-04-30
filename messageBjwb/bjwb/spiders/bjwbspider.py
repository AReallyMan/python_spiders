# -*- coding: utf-8 -*-
import scrapy
import time
import datetime
from scrapy.mail import MailSender
from ..items import BjwbItem  # 导入items底下的类
from ..settings import ELASTICSEARCH_INDEX, ELASTICSEARCH_TYPE


class BjwbspiderSpider(scrapy.Spider):
    name = 'bjwbspider'
    today = datetime.date.today()
    # 现在的日期
    current_date = time.strftime('%Y-%m/%d', time.localtime(time.time()))
    start_urls = ['http://bjwb.bjd.com.cn/html/' + current_date + '/node_113.htm']  # 开始url链接(北京晚报)
    basic_url = 'http://bjwb.bjd.com.cn/html/' + current_date + '/'  # 公共链接部分(北京晚报)
    # start_urls = ['http://bjwb.bjd.com.cn/html/'+current_date+'/node_113.htm']  # 开始url链接(北京晚报)

    def parse(self, response):
        url_node = response.xpath("//div[@class='hidenPage']/li/a")  # 每个板报里的对应的条例的末尾数据
        for url_end in url_node:
            if len(url_end.xpath("./@href").extract_first().split("./")[0]) == 0:  # 判断是否是第一个节点链接，True则取索引1，False取0
                url = self.basic_url + url_end.xpath("./@href").extract_first().split("./")[
                    1]
            else:
                url = self.basic_url + url_end.xpath("./@href").extract_first().split("./")[
                    0]
            yield scrapy.Request(url=url, callback=self.detail_page)

    def detail_page(self, response):
        detail_page_urlend = response.xpath("//div[@class='main-list']/ul/li/h2/a")
        for detail_url in detail_page_urlend:
            url = self.basic_url + detail_url.xpath("./@href").extract_first()
            if self.duplicate.redis_db.hexists(self.duplicate.redis_data_dict, url):
                print("该连接已被爬取")
            else:
                yield scrapy.Request(url=url, callback=self.getData)

    def getData(self, response):
        item = BjwbItem()
        node_list = response.xpath("//div[@class='main-in clearfix']")
        for nodes in node_list:
            item['url'] = response.url  # 链接
            item['fromwhere'] = nodes.xpath("./div/div/div[@class='article']/div[@class='info']/span[1]/text()").extract_first()  # 来源
            item['title'] = nodes.xpath("./div/div/div[@class='article']/h1/text()").extract_first()  # 标题
            data = nodes.xpath("./div/div/div[@class='article']/div[@class='text']")
            info = data[0].xpath('string(.)').extract()[0]
            item['content'] = info
            item['timetoday'] = nodes.xpath("./div/div/div[@class='article']/div[@class='info']/span[2]/text()").extract_first()  # 时间
            item['version'] = nodes.xpath("./div/div/div[@class='article']/div[@class='info']/span[4]/text()").extract_first()  # 版次
            item['auther'] = nodes.xpath("./div/div/div[@class='article']/div[@class='info']/span[5]/text()").extract_first()  # 作者
            item['spiderName'] = ELASTICSEARCH_TYPE
            item['spiderDesc'] = '北京晚报'
            item['siteType'] = '纸媒'
            item['source'] = '北京晚报'
            item['publicTimeStamp'] = int(time.mktime(self.today.timetuple()))
            item['insertTimeStamp'] = int(time.time() * 1000)
            yield item

    # def closed(self, reason):
    #     today_date = datetime.date.today()
    #     settings = scrapy.settings.Settings({'MAIL_FROM': 'zhzwx9@163.com', 'MAIL_HOST': 'smtp.163.com',
    #                                          'MAIL_PORT': '25', 'MAIL_USER': 'zhzwx9@163.com',
    #                                          'MAIL_PASS': 'FVDYFCDKVXGTVKNA'}, priority='project')
    #     mailer = MailSender.from_settings(settings)
    #     attach_name = "北京晚报.xlsx"
    #     mimetype = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    #     file_object = open('北京晚报.xlsx', 'rb')
    #     return mailer.send(to=['yangteng@rietergroup.com'], subject=str(today_date) + u"新舆情资源文件: 北京晚报.xlsx;", body='',
    #                        cc=['zhzwx9@163.com'], attachs=[(attach_name, mimetype, file_object)],
    #                        mimetype='text/plain')

