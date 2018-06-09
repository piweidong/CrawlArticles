# coding: utf8

# 百度抓取需要用到的包
import os
import json
import base64
import time
import datetime
import urllib.parse
import collections
import traceback
import platform
import requests
import lxml.html
import pytesseract
from io import BytesIO
from selenium import webdriver
from user_agent import generate_user_agent
from PIL import Image, ImageFilter, ImageEnhance


# 将网页源码转成tree型对象, 然后可用xpath查找元素
def parse_doc(page_raw):
    return lxml.html.fromstring(page_raw)


# 阿里云验证码接口
def get_verify_code_by_ali(pic_path, type='cen'):

    url = 'http://jisuyzmsb.market.alicloudapi.com/captcha/recognize?type={}'.format(type)
    appcode = 'XXX'  # todo 这里填上你自己的appcode[之前文章介绍了]

    with open(pic_path, 'rb') as f:
        data = f.read()
    bodys= {'pic': base64.b64encode(data)}

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


def recognize_ocr(image):  # 识别数字
    # 将图片放大5倍
    _, _, x, y = image.getbbox()
    image = image.resize((x*5, y*5), Image.BILINEAR)
    # 调对比度
    en = ImageEnhance.Contrast(image)
    image = en.enhance(1.0)
    image = image.convert('L')
    # 将图片平滑
    image = image.filter(ImageFilter.SMOOTH)

    table = [0 if i < 220 else 1 for i in range(256)]
    image = image.point(table, '1')
    # image.show()
    image = image.filter(ImageFilter.MedianFilter)

    # 使用pytesseract模块识别图片
    raw_num = pytesseract.image_to_string(image, config='digits')

    # 将字符串处理成汉字
    nums = raw_num.replace(' ', '').replace('.', '').replace(',', '')
    nums = [int(e) for e in nums.split() if e.isdigit()]

    return nums


def recognize(image):  # 识别7个纵坐标值
    # 百度指数纵坐标7个数据，且位等差数列，为了确保能识别正确，我们切割成7份，分开识别

    ocr_fail_count = 0
    num_list = []
    for i in range(7):
        box = (0, 0+i*60, 200, 60+i*60 if 60+i*60 < 394 else 394)  # 注意这里坐标不能超出图片
        image_one = image.crop(box)
        nums = recognize_ocr(image_one)
        if len(nums) == 1:
            num = nums[0]
        else:
            ocr_fail_count += 1
            num = 0
        print(num)
        num_list.append(num)

    print('ocr result:', num_list)
    print('ocr failed:', ocr_fail_count)

    #  校验
    if len(num_list) != 7 or ocr_fail_count > 3:
        return False

    return num_list


def validate_nums(num_list):  # 判断识别的数字是否正确，再进行修正
    if not num_list:
        return False

    # 计算识别出数字的等差
    c = collections.Counter()
    for i in range(7):
        for j in range(7):
            if i < j:
                c.update({(num_list[i]-num_list[j])/(j-i)})
    dis = c.most_common()[0][0]

    # 如果等差为0报错
    if dis == 0:
        return False

    # 如果等差有多个,但是最大的两个等差个数是一样的报错
    if len(c.most_common()) > 1 and c.most_common()[0][1] == c.most_common()[1][1]:
        return False

    # 使用等差找出正确的数值
    c = collections.Counter()
    for i in range(7):
        for j in range(7):
            if i < j:
                if (num_list[i]-num_list[j]) == (dis * (j-i)):
                    c.update([i, j])

    if not c.most_common():  # 如果没有正确值
        return False

    valid_idx = c.most_common()[0][0]  # 出现次数最多的正确值
    max_val = num_list[valid_idx] + valid_idx * dis  # 计算出最大值
    return max_val, dis  # 返回最大值和等差


class BaiduIndex(object):

    def __init__(self, user, pwd):
        self.browser = self.get_browser()
        self.user = user
        self.pwd = pwd

    def get_browser(self):
        co = webdriver.ChromeOptions()
        # co.add_argument('--headless')
        co.add_argument('--user-agent={}'.format(generate_user_agent(navigator=['chrome'])))
        browser = webdriver.Chrome(
            chrome_options=co,
            service_log_path=os.path.devnull
        )
        browser.set_window_size(1440, 900)

        return browser

    def change_verify_img(self):  # 更改验证码图片
        element = self.browser.find_element_by_class_name("pass-change-verifyCode")
        element.click()
        time.sleep(2)

    def need_login(self):  # 判断是否需要登陆
        return bool(self.browser.find_elements_by_xpath('//input[@value="登录"]'))

    def get_verify_code(self, img_class_name):
        """
        截取验证码图片, 调用阿里云图片接口识别
        :param img_class_name: 验证码图片元素class属性值
        :return: 验证码
        """
        time.sleep(2)
        page_path = './page.png'
        self.browser.save_screenshot(page_path)

        image = Image.open(page_path)
        verify_image_element = self.browser.find_element_by_class_name(img_class_name)
        x1 = verify_image_element.location['x']
        y1 = verify_image_element.location['y']
        delta_x = verify_image_element.size['width']
        delta_y = verify_image_element.size['height']
        x2 = x1 + delta_x
        y2 = y1 + delta_y
        box = (x1, y1, x2, y2)
        if 'Darwin' in platform.uname():
            box = (x1 * 2, y1 * 2, x2 * 2, y2 * 2)
        image = image.crop(box)

        code_path = './code.png'
        image.save(code_path)
        code = get_verify_code_by_ali(code_path)
        print('code', code)
        return code

    def login_verify(self):  # 登陆时, 有验证码识别登陆
        time.sleep(2)
        code = self.get_verify_code('pass-verifyCode')

        self.browser.find_element_by_name('verifyCode').send_keys(str(code))
        self.browser.find_element_by_css_selector("input.pass-button.pass-button-submit").click()
        time.sleep(1)

    def login(self):
        # 输入账号密码, 然后点击登陆按钮登陆
        self.browser.find_element_by_name('userName').send_keys(self.user)
        self.browser.find_element_by_name('password').send_keys(self.pwd)
        self.browser.find_element_by_css_selector("input.pass-button.pass-button-submit").click()

        time.sleep(3)

        for i in range(3):
            # 判断是否有验证码, 如果有验证码, 登陆时需要调用login_verify
            if not bool(self.browser.find_elements_by_xpath('//p[contains(@id, "verifyCodeImgWrapper")]')):
                break
            self.change_verify_img()  # 登陆失败, 更改验证码图片

            self.login_verify()  # 识别验证码然后登陆
        else:
            raise Exception('can not login')

    def need_verify(self):  # 判断是否需要输入验证码
        return bool(self.browser.find_elements_by_class_name('verifyInput'))

    def verify(self):  # 访问多了, 验证码识别
        for i in range(3):
            code = self.get_verify_code('verifyImg')

            self.browser.find_element_by_xpath('//input[@class="verifyInput"]').send_keys(str(code))
            self.browser.find_element_by_xpath('//span[@class="tang-dialog-button-s"]').click()
            self.browser.find_element_by_css_selector('span.tang-dialog-button-s').click()

            if not self.need_verify():
                break
            self.change_verify_img()
        else:
            raise Exception('cat not verify')

    def crawl(self, word):
        print(word, 'start')

        for i in range(5):
            url = 'http://index.baidu.com/?tpl=trend&word=%s' % urllib.parse.quote(word.encode('gbk'))
            self.browser.get(url)

            if '由于您访问过于频繁，请稍后再试' not in self.browser.page_source:
                time.sleep(1)
                break
            time.sleep(200)

        if self.need_login():  # 先判断是否需要登陆
            print('login')
            time.sleep(2)
            self.login()  # 登陆
            time.sleep(4)

        if self.need_verify():  # 判断是否有验证码
            time.sleep(1)
            self.verify()  # 验证操作
            time.sleep(2)

        if '未被收录，如要查看相关数据，您需要购买创建新词的权限' in self.browser.page_source:
            print('关键字未被收录')
            return
        if '暂不提供数据，且不提供创建新词服务，请查询或添加其他关键词' in self.browser.page_source:
            print('关键字未被收录')
            return

        self.browser.implicitly_wait(4)  # 等待数据加载, 画出百度指数图

        # self.browser.find_element_by_xpath(u'//div[@class="grpArea"]//a[text()="最近30天"]').click()

        # 将网页源码转成tree型结构对象, 方便使用xpath查找元素
        doc = parse_doc(self.browser.page_source)

        # 获取数据从坐标对应图片上的位置
        ls = doc.xpath('//div[@id="trend"]//path[@stroke="#3ec7f5"]/@d')[0]
        data = [(each.split(',')[-2], each.split(',')[-1]) for each in ls.split('M')[1].split('C')]
        y_list = [float(y) for x, y in data]

        assert len(y_list) == 30

        # 获取横坐标日期
        start_date, _, end_date = doc.xpath(
            u'//div[@id="trend-wrap"]//span[@class="compInfo" and contains(text(), " 至 ")]/text()'
        )[0].split()

        start_date = datetime.datetime.strptime(start_date, '%Y-%m-%d').date()
        end_date = datetime.datetime.strptime(end_date, '%Y-%m-%d').date()

        # 执行js获取纯净的纵坐标图片
        self.browser.execute_script('''
            document.querySelectorAll('path[fill="#3ec7f5"]')[0].setAttribute('style', 'display:none');
        ''')
        self.browser.execute_script('''
            var x = document.querySelectorAll('text')
            for(var i=0; i<x.length; i++) { x[i].setAttribute('style', 'display:none'); }
        ''')
        self.browser.execute_script('''
            var x = document.querySelectorAll('path')
            for(var i=0; i<x.length; i++) { x[i].setAttribute('style', 'display:none'); }
        ''')

        print('wait 2 second for scripts execute...')
        time.sleep(2)

        # 截取纵坐标图片
        image = Image.open(BytesIO(self.browser.get_screenshot_as_png()))
        box = (2480, 1132, 2680, 1526)  # 读者可能需要根据自己情况调整
        image = image.crop(box)

        print('识别纵坐标数字：')
        result = validate_nums(recognize(image))

        if not result:  # ocr识别失败
            print('纵坐标识别识别！')

        # 根据每个点在图片上的坐标位置, 计算出大致的百度指数
        max_val, dis = result  # 纵坐标最大值和等差
        delta = dis / (207.7 / 7)
        min_y = 130.9

        data = []

        for i in range(30):
            date = start_date + datetime.timedelta(days=i)
            index = int(max_val-(y_list[i]-min_y)*delta)
            data.append((date, index))

            if index < 0:  # 如果百度指数小于0, 识别有误
                print(index, date, '===== < 0 =====')
                raise Exception('index < 0')

        print(data)  # 读者可以将结果写入文件或者数据库

    def run(self, words):
        for word in words:
            for i in range(2):
                try:
                    self.crawl(word)
                    break
                except Exception:
                    traceback.print_exc()
                time.sleep(2)


def main(user, pwd, words):
    crawl = BaiduIndex(user, pwd)
    try:
        crawl.run(words)
    except Exception as e:
        raise e
    finally:
        print('quit browser ============')
        crawl.browser.quit()


if __name__ == "__main__":

    words = ['爬虫', 'python', '百度']
    main('baidu_user_name', 'baidu_password', words)  # todo 这里改为自己的百度用户名和密码
