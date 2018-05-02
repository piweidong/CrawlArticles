# coding: utf8
import re
import time
import json
import requests


def get_html_encode(content_type, page_raw):
    '''
    :param content_type: str, response headers里面的参数 里面一般有编码方式
    :param page_raw: str, html源码信息, 里面的meta里面一般有编码方式
    :return: 返回编码方式
    '''

    encode_list = re.findall(r'charset=([0-9a-zA-Z_-]+)', content_type, re.I)
    if encode_list:
        return encode_list[0]

    encode_list = re.findall(r'<meta.+charset=[\'"]*([0-9a-zA-Z_-]+)', page_raw, re.I)
    if encode_list:
        return encode_list[0]


def _get_crawl(url, headers, get_payload, proxies, timeout):
    '''
    :param url: str, Request URL
    :param headers: dict, Request Headers
    :param get_payload: dict, Query String Parameters
    :return:
    '''

    r = requests.get(url, headers=headers, params=get_payload, proxies=proxies, timeout=timeout)
    if r.status_code != 200:  # 如果返回不是200, 报异常
        raise Exception(r.status_code)

    content_type = r.headers['Content-Type']
    if 'text/html' in content_type:
        encoding = get_html_encode(content_type, r.text)
        if encoding:
            r.encoding = encoding
        return r.text
    elif 'application/json' in content_type:
        return r.text
    elif 'application/pdf' in content_type:
        return r.content  # 返回字节
    elif 'image' in content_type:  # 图片
        return r.content  # 返回字节
    else:
        return r.content


def _post_crawl(url, headers, post_payload, proxies, timeout):
    '''
    :param url: str, Request URL
    :param headers: dict, Request Headers
    :param post_payload: dict, Query String Parameters
    :return:
    '''

    r = requests.post(url, headers=headers, data=post_payload, proxies=proxies, timeout=timeout)
    if r.status_code != 200:  # 如果返回不是200, 报异常
        raise Exception(r.status_code)

    content_type = r.headers['Content-Type']
    if 'text/html' in content_type:
        encoding = get_html_encode(content_type, r.text)
        if encoding:
            r.encoding = encoding
        return r.text
    elif 'application/json' in content_type:
        return r.text
    elif 'application/pdf' in content_type:
        return r.content  # 返回字节
    elif 'image' in content_type:  # 图片
        return r.content  # 返回字节
    else:
        return r.content


def _crawl(method, url, headers=None, payload=None, proxies=None, timeout=10):
    try:
        if method == 'get':
            return _get_crawl(url, headers, payload, proxies, timeout)
        elif method == 'post':
            return _post_crawl(url, headers, payload, proxies, timeout)
        else:
            raise Exception('method is wrong')
    except Exception as e:
        print(url)
        print(e)


if __name__ == '__main__':

    # 抓取36kr文章列表
    url = 'http://36kr.com/api/search-column/mainsite'
    get_payload = {
        'per_page': 20,
        'page': 1,
        '_': str(int(time.time() * 1000)),
    }
    headers = {
        'Host': '36kr.com',
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.181 Safari/537.36',
    }

    data = _crawl('get', url, headers, get_payload)
    print(data)

    # 解析json
    data = json.loads(data)
    articles = data['data']['items']
    print('文章id', '文章封面图片链接', '文章标题')
    for article in articles:
        print(article['id'], article['cover'], article['title'])

    # 抓取图片
    for article in articles:
        cover_url = article['cover']
        article_id = article['id']
        image_bytes = _crawl('get', cover_url)
        with open('{}.jpg'.format(article_id), 'wb') as f:
            # 将字节写入文件, 文件需要二进制形式
            f.write(image_bytes)

    # 抓取详情页
    for article in articles:
        url = 'http://36kr.com/p/{}.html'.format(article['id'])
        print(url)
        headers = {
            'Host': '36kr.com',
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.181 Safari/537.36',
        }
        # get_payload = {}  # 没有参数
        html = _crawl('get', url, headers)  # 下一篇文章会网页源码解析
        print(html)
