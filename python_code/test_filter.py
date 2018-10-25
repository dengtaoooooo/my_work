import pika
import hashlib
import redis
import json
from pymongo import MongoClient
from bs4 import BeautifulSoup
import requests
import time


pool = redis.ConnectionPool(host='localhost', port=6379, decode_responses=True)
r = redis.Redis(connection_pool=pool)
r.flushdb()
print(r.keys())
#
# def parse_html2db(html):
#     conn = MongoClient('127.0.0.1', 27017)
#     db = conn.duzhe
#     my_set = db.item
#     my_set.insert({str(map(lambda x:" " if(x==".") else x,html[0])):html[1]})
#     conn.close()
#     print(html[0] + "　的内容已经入库")
# def html_need2db(html):
#     if(("作者" in html) and ("上一篇" in html)
#             and ("下一篇" in html)  and ("来源" in html)):
#         return True
#     else:
#         return False
# def get_html_code(html):
#     soup = BeautifulSoup(html, 'html.parser')
#     seed_list = []
#     for k in soup.find_all('meta'):
#         try:
#             seed_list.append(k['content'])
#         except:
#             pass
#     return seed_list[0][seed_list[0].rfind("="):]
#
# def url_in_redis(url):
#     m = hashlib.md5(url.encode("utf-8"))
#     md5_url = str(m.hexdigest())
#     if (r.exists(md5_url)):
#         return False
#     else:
#         r.set(md5_url, url)
#         return True
#
#
# html = requests.get("http://www.52duzhe.com/1_2012_09/3196.html")
#
# html.encoding = get_html_code(html.text)
# print(html.text)
# x=html_need2db(html.text)
# print(x)