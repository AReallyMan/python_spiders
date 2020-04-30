# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html
import json

import sys
# reload(sys)
# sys.setdefaultencoding('utf8')
#
# from kafka import KafkaProducer
# from kafka.errors import KafkaError
import json


from openpyxl import Workbook

class CcgpPipeline(object):
    def __init__(self):
        #self.file = open("json.json","wb")
        self.wb = Workbook()
        self.ws = self.wb.active
        self.ws.append(['标题','发布时间','预算金额','采购项目名称','品目',
                        '采购单位','公告时间',
                        '获取招标问价时间','开标时间','开标地点','链接'])

        #self.ws.column_dismensions['A'].width = 40.0
        #self.ws.row_dismensions[1].height = 60.0

        #self.producer = KafkaProducer(bootstrap_servers=['hadoop01:9092', 'hadoop02:9092'],
                                 #value_serializer=lambda m: json.dumps(m).encode('ascii'))

    def process_item(self, item, spider):

        #content = json.dumps(dict(item), ensure_ascii=False)+"\n"

        #self.file.write(content)
        line = [item['title'],item['publish'],item['budget'],item['project'],
                item['type'],item['company'],
                item['noticeTime'],item['priceTime'],
                item['openTime'],item['address'],item['href']]
        self.ws.append(line)



        #self.producer.send('test', dict(item))

        return item

    def close_spider(self, spider):
        self.wb.save(u'中国政府采购网-服务类品目采购公告(' + spider.today + ').xlsx')
        #self.producer.flush()
        pass

