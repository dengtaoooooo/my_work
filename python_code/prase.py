import pika
import hashlib
import redis
import json
from pymongo import MongoClient
from bs4 import BeautifulSoup
import uuid
import requests
import time

"""
1.先看看要不要把这个ｈｔｍｌ文件入库

2.解析该网页内的链接（ｓｅｅｄ）然后经过下面两步骤，看看是否满足入库
３．去掉该网页内队列内重复ｓｅｅｄ
４．判断是否出域名
"""

pool = redis.ConnectionPool(host='localhost', port=6379, decode_responses=True)
r = redis.Redis(connection_pool=pool)
user_pwd = pika.PlainCredentials("myuser", "mypass")
conn = pika.BlockingConnection(pika.ConnectionParameters('localhost', credentials=user_pwd))
channel_html = conn.channel()
channel_seed = conn.channel()
channel_html.queue_declare(queue='html')
channel_seed.queue_declare(queue='seed')


def get_title(html):
    soup = BeautifulSoup(html, 'html.parser')
    title_list=[]
    for k in soup.find_all('h1'):
        title_list.append(k.text)
    return title_list[0]

def filter_seeds(item):
    if(item=="#"):
        return False
    if("http://" in item):
        return False
    return True

# 拆分url方便做判断，该方法与业务逻辑无关
def url2list(url):
    templist = url.split("/")
    url_list=list(templist)
    return list(filter(None,url_list))


# 控制要不要解析该url的html内容
def html_need2db(html):
    if(("作者" in html[1]) and ("上一篇" in html[1])
            and ("下一篇" in html[1])  and ("来源" in html[1])):
        return True
    else:
        return False

# 解析html
def parse_html2db(html):
    conn = MongoClient('127.0.0.1', 27017)
    db = conn.duzhe
    my_set = db.item
    title=get_title(html[1])
    my_set.insert({"title":title.replace("."," "),"content":html[1]})
    conn.close()
    print(title + "　的内容已经入库")
# 得到网页的seed
def get_html_seed(html):
    soup = BeautifulSoup(html[1], 'html.parser')
    seed_list = []
    for k in soup.find_all('a'):
        try:
           seed_list.append(k['href'])
        except:
            pass
    url_href= list(filter(filter_seeds, seed_list))
    new_href=list(map(lambda x:html[0][0:html[0].rfind('/')+1]+x,url_href))
    return new_href

# 控制不要爬出域名外的内容
def is_in_domain(url):
    if("http://www.52duzhe.com" in url):
       return True
    else:
        return False


# 控制不能重复添加url
def url_in_redis(url):
     m = hashlib.md5(url.encode("utf-8"))
     md5_url=str(m.hexdigest())
     if(r.exists(md5_url)):
         return False
     else:
         r.set(md5_url, url)
         return True


def doing(ch,method,properties,body):
    """根据url判断是否入库，从页面提取url放入seed队列"""
    body=str(body, 'utf-8')
    url_html_list=json.loads(body)


    is2db= html_need2db(url_html_list)

    if (is2db):
        parse_html2db(url_html_list)

    seed_list=get_html_seed(url_html_list)

    no_rep_url = list(filter(url_in_redis,seed_list))

    result = list(filter(is_in_domain, no_rep_url))


    print(url_html_list[0]+"内的可用链接为：")
    print(result)

    for i in result:
        url_in_redis(i)
        channel_html.basic_publish(exchange='', routing_key='seed', body=i)
    ch.basic_ack(delivery_tag=method.delivery_tag)

def wait_msg():
    channel_html.basic_qos(prefetch_count=1)
    # 从html队列get数据
    channel_html.basic_consume(doing,queue="html",no_ack=False)#no_ack 标记是否要在消息处理后发送确认信息
    channel_html.start_consuming()

wait_msg()