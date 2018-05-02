# coding: utf8
import time
import datetime
import lxml.html
from article1.crawl import _crawl
from functools import wraps
import threading
from article3.proxy import ProxyPool


free_ips = set()
valid_ips = set()


def sync(lock):
    def catch_func(func):
        @wraps(func)
        def catch_args(*args, **kwargs):
            with lock:
                return func(*args, **kwargs)
        return catch_args
    return catch_func


@sync(threading.Lock())
def get_proxy():
    if free_ips:
        return free_ips.pop()


def parse_doc(page_raw):
    '''
    :param page_raw: html源码
    :return: Element对象
    '''
    return lxml.html.fromstring(page_raw)


def get_free_ips():
    ips = set()
    for url in [
        'http://www.xicidaili.com/nn/',
        'http://www.xicidaili.com/nt/'
    ]:
        headers = {
            'Host': 'www.xicidaili.com',
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.181 Safari/537.36',
        }
        page_raw = _crawl('get', url, headers)
        doc = parse_doc(page_raw)
        for each in doc.xpath("//table[@id='ip_list']//tr")[1:]:
            ip = each.xpath("./td[2]/text()")[0]
            port = int(each.xpath("./td[3]/text()")[0])
            ips.add((ip, port))

    return ips


def validate(host, port):
    proxy_url = 'http://{}:{}'.format(host, port)
    proxies = {
        'http': proxy_url,
        'https': proxy_url
    }

    url = 'http://www.sina.com.cn/'  # 访问新浪网，如果成功说明ip有效
    try:
        start_time = time.time()
        page_raw = _crawl('get', url, proxies=proxies, timeout=5)
        if page_raw and 'sina' in page_raw:
            pass
        else:
            raise Exception('response is invalid')
        end_time = time.time()
        time_cost = end_time - start_time
    except Exception as e:
        print(e)
        time_cost = 25

    if time_cost < 15:
        ProxyPool.objects(id='{}:{}:{}'.format('sina', host, port)).update(
            set__host=host,
            set__port=port,
            set__updated_at=datetime.datetime.now(),
            upsert=True,
        )
        valid_ips.add((host, port))

    return time_cost


def run():
    while 1:
        proxy = get_proxy()
        if proxy:
            print(proxy)
            host, port = proxy
            validate(host, port)
        else:
            break


if __name__ == '__main__':

    start_time = datetime.datetime.now()

    free_ips.update(get_free_ips())  # 将网站的免费代理加入待验证集合
    # 将数据库中已有的代理也加入待验证集合
    free_ips.update([(p.host, p.port) for p in ProxyPool.objects.no_cache()])

    # 使用多线程加快验证速度
    threads = []
    for i in range(100):
        time.sleep(0.01)
        t = threading.Thread(target=run)
        t.start()
        threads.append(t)

    for t in threads:
        t.join()

    # 删掉数据库中无效的代理
    ProxyPool.objects(updated_at__lt=start_time).delete()

    # 打印出所有有效代理
    print('valid_ips_num:', len(valid_ips))
    # valid_ips_num: 21
    for valid_ip in valid_ips:
        print(valid_ip)
