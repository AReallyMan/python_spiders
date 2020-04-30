# -*- coding: utf-8 -*-
import sys

import scrapy
from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor
import time
from ..items import ZhongxinjwItem
from ..settings import ELASTICSEARCH_INDEX, ELASTICSEARCH_TYPE
import datetime
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from scrapy.mail import MailSender


class ZhongxinjwSpiderSpider(CrawlSpider):
    name = 'zhongxinjw_spider'
    #allowed_domains = ['chinanews.com']
    start_urls = ['http://www.jwview.com/znh.html', 'http://www.jwview.com/hg.html', 'http://www.jwview.com/jr.html', 'http://www.jwview.com/zq.html', 'http://www.jwview.com/sj.html', 'http://www.jwview.com/kj.html']
    current_time = time.strftime("%m-%d", time.localtime())
    today = datetime.date.today()
    rules = {
        Rule(LinkExtractor(allow='http://www.jwview.com/jingwei/html/'+current_time+'/\d{6}\.shtml'), callback='parse_item'),
    }

    def parse_item(self, response):
        item = ZhongxinjwItem()
        url = response.url
        if self.duplicate.redis_db.hexists(self.duplicate.redis_data_dict, url):
            print("该连接已被爬取")
        else:
            item['title'] = response.xpath("//div[@class='title']/h1/text()").extract_first()

            publishtime = response.xpath("//div[@class='title']/div/text()").extract_first()
            if publishtime:
                item['publishtime'] = publishtime[0:20]
            else:
                item['publishtime'] = ''
            fromwhere = response.xpath("//div[@class='title']/div/text()").extract_first()
            if fromwhere:
                item['fromwhere'] = fromwhere[20:]
            else:
                item['fromwhere'] = ''
            item['content'] = response.xpath("//div[@class='content_zw bgwhite']").xpath('string(.)').extract_first()

            item['editor'] = response.xpath("//div[@class='editor']/text()").extract_first()

            item['url'] = response.url
            item['spiderName'] = ELASTICSEARCH_TYPE
            item['spiderDesc'] = '中新经纬'
            item['siteType'] = '资讯'
            item['source'] = '中新经纬'
            item['publicTimeStamp'] = int(time.mktime(self.today.timetuple()))
            item['insertTimeStamp'] = int(time.time() * 1000)
            yield item

    def closed(self, reason):
        today_date = datetime.date.today()
        settings = scrapy.settings.Settings({'MAIL_FROM': 'zhzwx9@163.com', 'MAIL_HOST': 'smtp.163.com',
                                             'MAIL_PORT': '25', 'MAIL_USER': 'zhzwx9@163.com',
                                             'MAIL_PASS': 'FVDYFCDKVXGTVKNA'}, priority='project')
        mailer = MailSender.from_settings(settings)
        attach_name = "中新经纬.xlsx"
        mimetype = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        file_object = open('中新经纬.xlsx', 'rb')
        return mailer.send(to=['zhzwcs3@126.com'], subject=str(today_date)+u"新舆情资源文件: 中新经纬.xlsx;", body='',
                    cc=['zhzwx9@163.com'], attachs=[(attach_name, mimetype, file_object)], mimetype='text/plain')


        # today_date = datetime.date.today();
        # HOST = "smtp.163.com"
        # # PORT = "465"
        # SUBJECT = str(today_date)+"新舆情资源文件： 中新经纬.xlsx;"
        # FROM = "zhzwx9@163.com"
        # TO = "zhzwcs3@126.com"
        # message = MIMEMultipart('related')
        #
        # # 一般如果数据是二进制的数据格式，在指定第二个参数的时候，都使用base64，一种数据传输格式。
        # # 如果文件名是中文的：
        # # add_header()能够正常的显示中文；
        # # message_docx1['Content-Disposition']是无法正常显示中文的。
        #
        # # message_docx1['Content-Disposition'] = 'attachment;filename=测试.docx'
        # message_docx1 = MIMEText(open('中新经纬.xlsx', 'rb').read(), 'base64', 'utf8')
        # # filename发送文件，附件显示的名称
        # message_docx1.add_header('content-disposition', 'attachment', filename='中新经纬.xlsx')
        # message.attach(message_docx1)
        #
        # message['From'] = FROM
        # message['Subject'] = SUBJECT
        # message['To'] = TO
        #
        # client = smtplib.SMTP_SSL(host=HOST)
        # client.connect(host=HOST)
        #
        # print('result: ', client.login(FROM, 'FVDYFCDKVXGTVKNA'))
        #
        # print('发送结果：', client.sendmail(from_addr=FROM, to_addrs=[TO], msg=message.as_string()))
