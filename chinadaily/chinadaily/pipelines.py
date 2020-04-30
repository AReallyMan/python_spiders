# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html
from openpyxl import Workbook
from elasticsearch import Elasticsearch
import elasticsearch.helpers
import redis
from kafka import KafkaProducer
import json
from .settings import ELASTICSEARCH_INDEX, ELASTICSEARCH_TYPE
import os
import sys
path = [
    "/usr/local/workspace-gerapy/gerapy/projects",
    "C:/Users/asus/Desktop/spiders"
]
[sys.path.append(p)for p in path if os.path.isdir(p)]
from spider_util.duplicate import Duplicate  # 临时环境
from spider_util.settings import *  # 公共配置


class ChinadailyPipeline(object):
    def __init__(self):
        self.wb = Workbook()
        self.ws = self.wb.active
        self.ws.append(['时间', '来源', '标题', '内容', '编辑', '链接'])

    def process_item(self, item, spider):
        line = [item['publishtime'], item['fromwhere'], item['title'], item['content'], item['editor'],
                item['url']]
        self.ws.append(line)
        self.wb.save(r"C:\Users\asus\Desktop\pydata\中国日报（中文网）.xlsx")
        return item



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