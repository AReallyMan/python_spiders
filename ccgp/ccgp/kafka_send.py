# -*- coding: utf-8 -*-
from kafka import KafkaProducer
from kafka.errors import KafkaError
import json
#producer = KafkaProducer(bootstrap_servers=['hadoop01:9092'])


# encode objects via msgpack
# 通过msgpack对对象进行编码
#producer = KafkaProducer(value_serializer=msgpack.dumps)
#producer.send('msgpack-topic', {'key': 'value'})

# produce json messages
producer = KafkaProducer(bootstrap_servers=['hadoop01:9092'], value_serializer=lambda m: json.dumps(m).encode('ascii'))
message = dict()
message["spiderName"] = "www.baidu.com"
message["index"] = "sentiment1"
for i in range(3000):
    message['segment'] = str(i)
    producer.send('sentiment', message)
print 'aaa'
# block until all async messages are sent
#直到所有的快发送成功后刷新
producer.flush()





