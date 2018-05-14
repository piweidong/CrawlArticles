# coding: utf8
import os
import time
import lxml.html
from selenium import webdriver
from user_agent import generate_user_agent
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys

from article1.crawl import _crawl


user_agent = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/66.0.3359.139 Safari/537.36"
# user_agent这个模块可以自动生成user-agent, 如下：
# print(generate_user_agent())
# print(generate_user_agent(navigator=['chrome']))  # 只生成chrome的user-agent


def download():
    # 设置浏览器的一些参数
    co = webdriver.ChromeOptions()
    co.add_argument('--headless')  # 无界面模式
    co.add_argument('--disable-images')  # 禁止加载图片，提高速度
    # co.add_argument('--disable-javascript')  # 禁用js
    # co.add_argument('--proxy-server=http://ip:port')  # 使用代理
    co.add_argument('--user-agent={}'.format(user_agent))  # 设置user-agent
    browser = webdriver.Chrome(
        chrome_options=co,
        executable_path='/usr/bin/chromedriver',  # 如果chromedriver不在环境变量中，需要指定
        service_log_path=os.path.devnull  # 设置不输出日志
    )

    browser.get('https://www.baidu.com')
    print(browser.page_source)  # 打印出html源码


def parse_doc(page_raw):
    '''
    :param page_raw: html源码
    :return: Element对象
    '''
    return lxml.html.fromstring(page_raw)


class ChromeDownloader(object):

    def __init__(self, proxy=None):
        # 设置代理
        self.proxy = proxy  # http://ip:port

    def __enter__(self):
        #  打开浏览器
        self.browser = self.get_browser()
        return self.browser

    def __exit__(self, exc_type, exc_val, exc_tb):
        # 关闭浏览器
        try:
            if self.browser:
                self.browser.quit()
        except Exception as e:
            print(e)

    def get_browser(self):
        co = webdriver.ChromeOptions()
        # co.add_argument('--headless')
        # co.add_argument('--disable-images')
        if self.proxy:
            co.add_argument('--proxy-server={}'.format(self.proxy))  # 使用代理
        co.add_argument('--user-agent={}'.format(generate_user_agent(navigator=['chrome'])))
        browser = webdriver.Chrome(
            chrome_options=co,
            service_log_path=os.path.devnull
        )

        return browser


def login_weibo(user_name, password):
    with ChromeDownloader() as browser:
        browser.get('https://weibo.com/')
        # 等待元素加载完成
        wait = WebDriverWait(browser, 20)
        element = wait.until(EC.presence_of_element_located((By.ID, "loginname")))
        element.send_keys(user_name)  # 填入你微博账号
        element = wait.until(EC.presence_of_element_located((By.NAME, "password")))
        element.send_keys(password)  # 填入你微薄密码
        element.send_keys(Keys.RETURN)
        time.sleep(5)

        cookies = browser.get_cookies()
        cookie = ';'.join([e['name']+'='+e['value'] for e in cookies])

    return cookie


if __name__ == '__main__':

    # url = 'https://detail.tmall.com/item.htm?id=564794769484'
    #
    # # 使用requests
    # page_raw = _crawl('get', url)
    # doc = parse_doc(page_raw)
    # print(doc.xpath("//span[contains(text(), '月销量')]/following-sibling::span/text()"))
    # # 输出： []
    #
    # # 使用chrome
    # with ChromeDownloader() as browser:
    #     browser.get(url)
    #     doc = parse_doc(browser.page_source)
    #     print(doc.xpath("//span[contains(text(), '月销量')]/following-sibling::span/text()"))
    #     # 输出： ['95']

    cookie = login_weibo('user_name', 'passeord')  # 你的用户名和密码，在weibo手机端将登陆保护去掉
    print(cookie)

    # 下面直接用requests在headers中加入cookie，即可完成登陆，获取到页面数据
    headers = {'Cookie': cookie}
    page_raw = _crawl('get', 'https://weibo.com/2092770375/fans', headers=headers)
    print('脆弱的负离子饭' in page_raw, '=============')
    # 输出： true

    # from selenium import webdriver
    #
    # # 为了方便展示，使用有界面chrome
    # browser = webdriver.Chrome()
    # browser.get('https://www.baidu.com')
    #
    #
    # # 执行js
    # browser.execute_script('''
    #     document.getElementById("su").setAttribute("value","搜狗二下")
    # ''')
