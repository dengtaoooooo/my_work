import pika
import requests
import json
from bs4 import BeautifulSoup
import hashlib
import redis
user_pwd = pika.PlainCredentials("myuser", "mypass")
conn = pika.BlockingConnection(pika.ConnectionParameters('localhost', credentials=user_pwd))
channel_html = conn.channel()
channel_seed = conn.channel()
channel_html.queue_declare(queue='html')
channel_seed.queue_declare(queue='seed')

pool = redis.ConnectionPool(host='localhost', port=6379, decode_responses=True)
r = redis.Redis(connection_pool=pool)


# 控制不能重复添加url
def url_in_redis(url):
     m = hashlib.md5(url.encode("utf-8"))
     md5_url=str(m.hexdigest())
     if(r.exists(md5_url)):
         return False
     else:
         r.set(md5_url, url)
         return True
c=url_in_redis("http://www.52duzhe.com/2018_01/index.html")
print(c)
