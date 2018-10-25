import pika
import requests
import json
from bs4 import BeautifulSoup
import redis
user_pwd = pika.PlainCredentials("myuser", "mypass")
conn = pika.BlockingConnection(pika.ConnectionParameters('localhost', credentials=user_pwd))
channel_html = conn.channel()
channel_seed = conn.channel()
channel_html.queue_declare(queue='html')
channel_seed.queue_declare(queue='seed')

pool = redis.ConnectionPool(host='localhost', port=6379, decode_responses=True)
r = redis.Redis(connection_pool=pool)
r.flushdb()

# channel_html.basic_publish(exchange='',routing_key='seed',body="http://www.52duzhe.com/")



#
# def doing(ch,method,properties,url):
#      html = requests.get(url)
#      html.encoding = "utf-8"
#      url_html_json=json.dumps([str(url,'utf-8'),html.text])
#      print(url_html_json)
#      ch.basic_ack(delivery_tag=method.delivery_tag)
#
#
#
#
# def wait_msg():
#     channel_html.basic_qos(prefetch_count=1)
#     # 从html队列get数据
#     channel_html.basic_consume(doing,queue="html",no_ack=False)#no_ack 标记是否要在消息处理后发送确认信息
#     channel_html.start_consuming()
#
# wait_msg()

def filter_seeds(item):
    if(item=="#"):
        return False
    if("http://" in item):
        return False
    return True
def get_html_seed(html):

    soup = BeautifulSoup(html[1], 'html.parser')
    seed_list = []
    for k in soup.find_all('a'):
        print(k)
        try:
            seed_list.append(k['href'])
        except:
            pass

    url_href= list(filter(filter_seeds, seed_list))
    new_href=list(map(lambda x:html[0][0:html[0].rfind('/')+1]+x,url_href))
    return new_href

html = requests.get('http://www.52duzhe.com/2014_22/index.html')
html.encoding = "utf-8"

l=['http://www.52duzhe.com/2014_22/index.html',html.text]

seed_list=get_html_seed(l)

print(seed_list)


