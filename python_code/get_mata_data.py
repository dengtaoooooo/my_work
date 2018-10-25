import pika
import redis
import json
from pymongo import MongoClient
from bs4 import BeautifulSoup
import requests
import re

html = requests.get("http://www.52duzhe.com/2017_24/duzh20172408.html", timeout=3)
html.encoding="utf-8"
content = html.text


def get_content(html):
    soup = BeautifulSoup(html, 'html.parser')
    p=""
    for k in soup.find_all('p'):
        p=p+str(k.text);
    return p

def get_auther(html):
    soup = BeautifulSoup(html, 'html.parser')
    auther=soup.find("span",id="pub_date").text
    return auther[auther.find("：")+1:]


def get_type(html):
    soup = BeautifulSoup(html, 'html.parser')
    p_type=soup.find("div",class_="menuItem itemNow")
    p_type=p_type.find_previous("h2").text
    return p_type


def get_year(html):
    soup = BeautifulSoup(html, 'html.parser')
    date=soup.find("a",href="index.html").text
    return date[0:4]

def get_d(html):
    soup = BeautifulSoup(html, 'html.parser')
    date=soup.find("a",href="index.html").text
    return date[6:8]

print(get_d(content))