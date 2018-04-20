# coding: utf8
import re
import html
import lxml.html
import datetime
from article1.crawl import _crawl


def format_text(text):
    '''
    将html一些源码字符处理成正常字符
    :param text:
    :return:
    '''
    if not text:
        return ''

    text = html.unescape(text.replace('&nbsp;', ' ').replace('<br>', ' '))
    text = text.replace('\t', ' ').replace('\r', ' ').replace('\n', ' ').strip()
    return text


def text2datetime(text):
    '''
    将文本转成时间格式
    :param text:
    :return:
    '''
    now = datetime.datetime.now()
    if '小时前' in text and re.findall(r'\d+', text):
        return now - datetime.timedelta(hours=int(re.findall(r'\d+', text)[0]))
    elif '天前' in text and re.findall(r'\d+', text):
        return now - datetime.timedelta(days=int(re.findall(r'\d+', text)[0]))
    elif re.findall(r'\d+-\d+-\d+', text):
        year, month, day = re.findall(r'(\d+)-(\d+)-(\d+)', text)[0]
        return datetime.datetime(int(year), int(month), int(day))
    else:
        raise Exception('text is wrong', text)


def parse_doc(page_raw):
    '''
    :param page_raw: html源码
    :return: Element对象
    '''
    return lxml.html.fromstring(page_raw)


def parse_channel_urls_page(page_raw):
    '''
    解析首页新闻类别
    :param page_raw: 网页源码字符串
    :return:
    '''

    doc = parse_doc(page_raw)

    channels = []
    for each in doc.xpath("//ul[contains(@class, 'header-column')]/li/a[contains(@href, 'channel')]"):
        channel_url_xpath = "./@href"
        channel_name_xpath = "./text()"

        channel_id = re.findall(r'channel/(\d+).html', each.xpath(channel_url_xpath)[0])[0]
        channel_name = each.xpath(channel_name_xpath)[0]

        channels.append(dict(channel_id=channel_id, channel_name=channel_name))

    return channels


def parse_channel_list_page(page_raw):
    '''
    解析类别列表页
    :param page_raw: 网页源码
    :return:
    '''

    doc = parse_doc(page_raw)

    articles = []
    for each in doc.xpath("//div[@class='mod-info-flow']/div"):
        article_url_xpath = ".//h2/a/@href"
        article_title_xpath = ".//h2/a/text()"
        article_publish_time_xpath = ".//span[@class='time']/text()"
        article_author_name_xpath = ".//span[@class='author-name']/text()"

        article_id = re.findall(r'article/(\d+).html', each.xpath(article_url_xpath)[0])[0]
        article_title = format_text(each.xpath(article_title_xpath)[0])
        article_publish_time = text2datetime(each.xpath(article_publish_time_xpath)[0])
        article_author_name = format_text(each.xpath(article_author_name_xpath)[0])

        articles.append(dict(
            article_id=article_id,
            article_title=article_title,
            publish_time=article_publish_time,
            author_name=article_author_name,
        ))

    return articles


if __name__ == '__main__':

    # 抓取首页
    url = 'https://www.huxiu.com/'
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.181 Safari/537.36',
    }
    page_raw = _crawl('get', url, headers)
    channels = parse_channel_urls_page(page_raw)
    print(channels)

    # 抓取列表页面
    for channel in channels:
        url = 'https://www.huxiu.com/channel/{}.html'.format(channel['channel_id'])
        page_raw = _crawl('get', url, headers)
        articles = parse_channel_list_page(page_raw)
        print(articles)

    # 注：笔者在抓取列表页面时，只是抓取了第一页，没有抓取第一页，第二页，...，读者有兴趣可以研究下，抓取其他页面。
