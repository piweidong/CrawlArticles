# coding: utf8
import time
import datetime
import random
import threading
from functools import wraps
from mongoengine import *


connect('test')  # 连接到mongodb本地test数据库


def sync(lock):
    def catch_func(func):
        @wraps(func)
        def catch_args(*args, **kwargs):
            with lock:
                return func(*args, **kwargs)
        return catch_args
    return catch_func


class ProxyPool(Document):

    id = StringField(primary_key=True)

    site = StringField()  # 此代理用于哪个网站

    host = StringField()
    port = IntField()
    user = StringField()
    password = StringField()

    time_cost = FloatField()  # 此代理请求网站所用时间
    updated_at = DateTimeField()  # 代理在数据库中更新时间
    last_used_at = DateTimeField()  # 代理最后一次使用时间

    meta = {
        'collection': 'proxy_pool',  # 会在mongodb中建立proxy_pool表
        'indexes': ['site'],
    }

    @property
    def proxies(self):
        if self.user and self.password:
            proxy_url = 'http://{user}:{password}@{host}:{port}'.format(
                user=self.user,
                password=self.password,
                host=self.host,
                port=self.port
            )
        else:
            proxy_url = 'http://{host}:{port}'.format(host=self.host, port=self.port)

        return {
            'http': proxy_url,
            'https': proxy_url,
        }


class ProxyHelper(object):

    def __init__(self, cache_seconds=5, site='sina', time_cost=5, timedelta=0):
        self.cache_seconds = cache_seconds
        self.site = site
        self.time_cost = time_cost
        self.timedelta = timedelta
        self.proxy_list = []
        self.last_fetch_at = time.time()
        self.fetch_proxy_list()

    def fetch_proxy_list(self):
        # 从数据库获取代理
        self.proxy_list = ProxyPool.objects(
            site=self.site, time_cost__lte=self.time_cost
        ).no_cache()
        self.last_fetch_at = time.time()

    @sync(threading.Lock())
    def random_choice(self):
        if (time.time() - self.last_fetch_at) >= self.cache_seconds:
            # 为了避免频繁访问数据库，每隔5s获取一次数据库中代理
            self.fetch_proxy_list()

        if not self.proxy_list:
            raise Exception('no proxy')

        available_proxy_list = [
            proxy
            for proxy in self.proxy_list
            if proxy.last_used_at <= datetime.datetime.now() - datetime.timedelta(seconds=self.timedelta)
        ]

        if not available_proxy_list:
            return

        proxy = random.choice(available_proxy_list)

        if self.timedelta:
            proxy.last_used_at = datetime.datetime.now()
            proxy.save()

        return proxy.proxies


proxy_helper = ProxyHelper()


def get_proxy():
    while 1:
        proxies = proxy_helper.random_choice()
        if proxies:
            return proxies
        else:
            time.sleep(1)


if __name__ == '__main__':

    proxies = get_proxy()
    print(proxies)

