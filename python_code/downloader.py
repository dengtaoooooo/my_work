import pika
import time
import json
import requests
from bs4 import BeautifulSoup
import threading
from multiprocessing import Process
user_pwd = pika.PlainCredentials("myuser", "mypass")
conn = pika.BlockingConnection(pika.ConnectionParameters('localhost', credentials=user_pwd))
channel_html = conn.channel()
channel_seed = conn.channel()
channel_html.queue_declare(queue='html')
channel_seed.queue_declare(queue='seed')



# 得到网页的编码
def get_html_code(html):
    soup = BeautifulSoup(html, 'html.parser')
    seed_list = []
    for k in soup.find_all('meta'):
        try:
            seed_list.append(k['content'])
        except:
            pass
    return seed_list[0][seed_list[0].rfind("="):]

# 从seed中获取url内容，同时把该seed加上
def seed2html(ch,method,properties,url):
    global flag
    """只做下载，不做逻辑判断，因为这个过程延时很大，逻辑判断全部加到解析器"""

    try:
        html = requests.get(url, timeout=3)
    except ConnectionError :
        print("网站链接超时，稍后会重试")
        ch.basic_reject(delivery_tag=method.delivery_tag, requeue=True)
        return
    except requests.exceptions.ConnectTimeout as e:
        print("网站链接超时，稍后会重试")
        ch.basic_reject(delivery_tag=method.delivery_tag, requeue=True)
        return
    except requests.exceptions.ReadTimeout:
        ch.basic_reject(delivery_tag=method.delivery_tag, requeue=True)
        return
    except requests.exceptions.ConnectionError:
        print("网站链接读取超时，稍后会重试")
        ch.basic_reject(delivery_tag=method.delivery_tag,requeue=True)
        return
    if(len(html.text) < 100):
        ch.basic_ack(delivery_tag=method.delivery_tag)
        return
    html.encoding = get_html_code(html.text)
    url_html_json=json.dumps([str(url,'utf-8'),html.text])
    print("发送以下html的内容和Url到消息队列")
    print(url)
    print("\n")
    channel_html.basic_publish(exchange='',routing_key='html',body=url_html_json)
    # 所有工作做完通知消息队列该消息处理完毕
    ch.basic_ack(delivery_tag=method.delivery_tag)


def wait_msg():
    channel_seed.basic_qos(prefetch_count=1)
    #从seed队列get数据
    channel_seed.basic_consume(seed2html,queue="seed",no_ack=False)#no_ack 标记是否要在消息处理后发送确认信息
    channel_seed.start_consuming()




wait_msg()
