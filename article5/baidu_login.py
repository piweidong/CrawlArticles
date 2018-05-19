import os
import time
import requests
import base64
import json
from PIL import Image
from user_agent import generate_user_agent
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException


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


def get_verify_code_by_ali(pic_path, type='cen'):
    # pic_path = '/Users/good/Desktop/test.png'

    url = 'http://jisuyzmsb.market.alicloudapi.com/captcha/recognize?type={}'.format(type)
    appcode = 'xxx'  # 这里填上你自己的appcode

    bodys = {}
    with open(pic_path, 'rb') as f:
        data = f.read()
    bodys['pic'] = base64.b64encode(data)

    headers = {
        'Authorization': 'APPCODE ' + appcode,
        'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
    }

    r = requests.post(url, data=bodys, headers=headers)
    if r.status_code != 200:
        return False  # 验证码识别错误

    res = json.loads(r.text)
    if res.get('msg') != 'ok':
        return False  # 验证码识别错误

    return res['result']['code']


def recognize_verify_code(browser):

    page_path = './page.png'
    browser.save_screenshot(page_path)

    image = Image.open(page_path)
    verify_code_path = './verify_code.png'
    verify_image_element = browser.find_element_by_xpath("//img[@class='pass-verifyCode']")
    # 不同操作系统获取图片坐标可能不一样，笔者是mac系统，读者根据自己的系统测试下
    x1 = verify_image_element.location['x']
    y1 = verify_image_element.location['y']
    delta_x = verify_image_element.size['width']
    delta_y = verify_image_element.size['height']
    x2 = x1 + delta_x
    y2 = y1 + delta_y
    box = (x1*2, y1*2, x2*2, y2*2)
    image = image.crop(box)
    image.save(verify_code_path)
    verify_code = get_verify_code_by_ali(verify_code_path)

    return verify_code


def is_logined(browser):
    if '修改资料' in browser.page_source and '修改密码' in browser.page_source:
        print('登陆成功: ----------------')
        return True
    return False


def get_cookie(browser):
    return ';'.join([e['name'] + '=' + e['value'] for e in browser.get_cookies()])


def change_verify_pic(browser):
    element = browser.find_element_by_xpath("//a[@class='pass-change-verifyCode']")
    element.click()
    time.sleep(1)


def get_baidu_cookie(user_name, password):
    with ChromeDownloader() as browser:
        browser.get('https://passport.baidu.com/v2/?login')
        # 等待元素加载完成
        wait = WebDriverWait(browser, 10)
        element = wait.until(EC.presence_of_element_located((By.XPATH, "//p[@title='用户名登录']")))
        if 'none' not in element.get_attribute('style'):
            element.click()
            time.sleep(2)
        element = wait.until(EC.presence_of_element_located((By.NAME, "userName")))
        element.send_keys(user_name)
        element = wait.until(EC.presence_of_element_located((By.NAME, "password")))
        element.send_keys(password)
        element.send_keys(Keys.RETURN)
        time.sleep(3)
        if is_logined(browser):
            return get_cookie(browser)

        try:
            element = browser.find_element_by_name('verifyCode')
        except NoSuchElementException:
            element = browser.find_element_by_xpath("//input[@value='登录']")
            element.click()
            if is_logined(browser):
                return get_cookie(browser)
            else:
                raise ValueError

        for i in range(3):
            verify_code = recognize_verify_code(browser)
            if verify_code:
                break
            change_verify_pic(browser)
        else:
            raise Exception('can not get right code')

        print('获取验证码成功：', verify_code)

        element.send_keys(verify_code)
        element.send_keys(Keys.RETURN)
        time.sleep(3)
        if is_logined(browser):
            return get_cookie(browser)
        return ''


if __name__ == '__main__':
    # 模拟登陆，获取数据
    for i in range(3):
        cookie = get_baidu_cookie('user_name', 'password')  # 百度用户名和密码
        if cookie:
            break
    else:
        raise ValueError('wrong cookie')

    print(cookie)
