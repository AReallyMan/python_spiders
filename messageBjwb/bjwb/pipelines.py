# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html
from openpyxl import Workbook
from elasticsearch import Elasticsearch
import elasticsearch.helpers
import redis
import os
import sys
path = [
    "/usr/local/workspace-gerapy/gerapy/projects",
    "E:/python1111/spider_project_yy"
]
[sys.path.append(p)for p in path if os.path.isdir(p)]
from spider_util.duplicate import Duplicate  # 临时环境
from spider_util.settings import *  # 公共配置
from kafka import KafkaProducer
import json
from .settings import ELASTICSEARCH_INDEX, ELASTICSEARCH_TYPE


class BjwbPipeline(object):
    def __init__(self):
        self.wb = Workbook()
        self.ws = self.wb.active
        self.ws.append(['出处', '标题', '内容', '时间', '链接',  '版次', '作者'])

    def process_item(self, item, spider):
        line = [item['fromwhere'], item['title'], item['content'], item['timetoday'], item['url'], item['version'], item['auther']]
        self.ws.append(line)  # 以行的形式存储
        self.wb.save(r"北京晚报.xlsx")
        return item


class KafkaPipeline(object):
    def open_spider(self, spider):
        self.producer = KafkaProducer(bootstrap_servers=['sentiment01:9092', 'sentiment03:9092'], value_serializer=lambda m: json.dumps(m).encode('ascii'))

    def process_item(self, item, spider):
        item['index'] = ELASTICSEARCH_INDEX
        self.producer.send('sentiment', dict(item))
        return item

    def close_spider(self, spider):
        self.producer.flush()
        self.producer.close()


class MongoPipeline(object):
    def open_spider(self, spider):
        pass

    def process_item(self, item, spider):
        return item

    def close_spider(self, spider):
        pass


class ElasticsearchPipeline(object):
    def open_spider(self, spider):
        self.es = Elasticsearch(([{"host": ELASTICSEARCH_HOST, "port": str(ELASTICSEARCH_PORT)}]))

    def process_item(self, item, spider):
        actions = [
            {
                '_op_type': 'index',
                '_index': ELASTICSEARCH_INDEX,
                '_type': ELASTICSEARCH_TYPE,
                '_source': dict(item)
            }
        ]
        elasticsearch.helpers.bulk(self.es, actions)  # 添加操作'''
        return item

    def close_spider(self, spider):
        pass


class RedisPipeline(object):
    def open_spider(self, spider):
        spider.duplicate = Duplicate(spider.name)
        spider.duplicate.find_all_url(index=ELASTICSEARCH_INDEX, doc_type=ELASTICSEARCH_TYPE, source='url')

    def process_item(self, item, spider):
        return item

    def close_spider(self, spider):
        print('爬虫关闭')
        r = redis.Redis(host=REDIS_HOST, port=str(REDIS_PORT), db=0)
        r.delete(spider.name)

