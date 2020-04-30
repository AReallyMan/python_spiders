# coding: utf-8
from spider_util.settings import REDIS_HOST, REDIS_PORT, ELASTICSEARCH_HOST, ELASTICSEARCH_PORT
# import settings
from elasticsearch import Elasticsearch
from redis import Redis

import time


class Duplicate(object):

    def __init__(self, dbName='dupe'):
        self.redis_db = Redis(host=REDIS_HOST, port=str(REDIS_PORT), db=0)  # 连接redis
        self.redis_data_dict = dbName  # 存储所有url的key

    def find_all_url(self, index, doc_type, source):
        # 查询所有的url
        es = Elasticsearch([{"host": ELASTICSEARCH_HOST, "port": str(ELASTICSEARCH_PORT)}])

        queryData = es.search(index=index,
                              doc_type=doc_type,
                              scroll='5m',
                              timeout='3s',
                              size=100,
                              body={"query": {"match_all": {}}},
                              _source=source)

        mdata = queryData.get("hits").get("hits")

        if not mdata:
            print('empty!')
        else:
            for i in mdata:
                # 把每一条的值写入key的字段里
                self.redis_db.hset(self.redis_data_dict, i["_source"][source], 0)
            scroll_id = queryData["_scroll_id"]
            total = queryData["hits"]["total"]

            for i in range(int(total / 100)):
                res = es.scroll(scroll_id=scroll_id, scroll='5m')  # scroll参数必须指定否则会报错
                for j in res["hits"]["hits"]:
                    # 把每一条的值写入key的字段里
                    if source in j["_source"].keys():
                        self.redis_db.hset(self.redis_data_dict, j["_source"][source], 0)


