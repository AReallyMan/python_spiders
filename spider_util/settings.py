# -*- coding: utf-8 -*-
'''
公共配置模块
'''

# elasticsearch 链接配置
ELASTICSEARCH_PORT = 9200
ELASTICSEARCH_HOST = '192.168.1.53'
# ELASTICSEARCH_HOST = '127.0.0.1'
ELASTICSEARCH_INDEX = 'sentiment1'


# redis 链接配置
REDIS_HOST = "192.168.1.51"
# REDIS_HOST = '127.0.0.1'
REDIS_PORT = 6379

# mongodb 链接配置
# MONGODB = 'mongodb://192.168.1.51:27017/'
MONGODB_URL = 'mongodb://192.168.1.51:27017/'
# MONGODB_URL = 'mongodb://127.0.0.1:27017/'