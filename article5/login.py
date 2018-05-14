import requests
from user_agent import generate_user_agent


def login():
    # 一、模拟登陆
    login_url = 'https://passport.36kr.com/passport/sign_in'
    identity_url = 'https://rong.36kr.com/api/user/identity'

    form_data = {
        'type': 'login',
        'bind': 'false',
        'needCaptcha': 'false',
        'username': 'fanlitest221@163.com',
        'password': 'a1234567!',
        'ok_url': 'https://rong.36kr.com/list/detail&',
        'ktm_reghost': 'rong.36kr.com',
    }

    # requests headers
    headers = {
        'Origin': 'https://passport.36kr.com',
        'Referer': 'https://passport.36kr.com/pages/?ok_url=https%3A%2F%2Frong.36kr.com%2Flist%2Fdetail%26',
        'User-Agent': generate_user_agent(),
        'X-Tingyun-Id': 'Dio1ZtdC5G4;r=210046210',
    }

    # 我们这里使用requests.Session() 对象来保存对话，这也是requests模块简洁易用的原因
    s = requests.Session()

    r = s.post(login_url, data=form_data, headers=headers)
    print(r.status_code, 'login')
    r = s.get(identity_url)
    print(r.status_code, 'identity')

    # 获取数据
    data_url = 'https://rong.36kr.com/n/api/column/0/company?sortField=HOT_SCORE&p=1'
    r = s.get(data_url)
    print(r.status_code, 'data')
    print(r.text)


def login_by_cookie():
    # 直接用cookie登陆
    data_url = 'https://rong.36kr.com/n/api/column/0/company?sortField=HOT_SCORE&p=1'

    # requests headers
    headers = {
        'Cookie': 'acw_tc=AQAAAGN/MWsnZAQAx+dRZW+ZRIiiAWZY; MEIQIA_EXTRA_TRACK_ID=14XitWh9KPyLGsy63OE1Gjii9yz; kr_stat_uuid=FkPd725437013; download_animation=1; Hm_lvt_e8ec47088ed7458ec32cde3617b23ee3=1526200586,1526209180; Hm_lpvt_e8ec47088ed7458ec32cde3617b23ee3=1526220791; _kr_p_se=36532bb6-18d4-4d9c-9c0c-ac1c47b30367; krid_user_id=1800562212; krid_user_version=1000; kr_plus_id=1800562212; kr_plus_token=2QlVbm_xhpMc7pYjisPoyFGDWWqz26_491984___; kr_plus_utype=0; Z-XSRF-TOKEN=eyJpdiI6InFiajdFVDlGeEhaVDBjUTBiazNheHc9PSIsInZhbHVlIjoiY0RycnpnNTN6dG83WVFiaUlPcTluSmRKZGM4VjdTOVZVQmhWTTRsYkd4WVZWeVRUaWFTYTJWdlo4ZzQ5UzEza3B6alRINlRNUDFwSDRERUxwY0p3ZVE9PSIsIm1hYyI6Ijc5MDAzMDU1MTI2MDRhNmU3NjI0YzkwMWMxNWYyOTBmNTkxNDZiOThhNzcwNjU1YTdiZjllMzI0ZDgxN2ZjZDQifQ%3D%3D; krchoasss=eyJpdiI6IkZ1VnY2dHhHOG1tbWoxdWJacm5mWmc9PSIsInZhbHVlIjoiR2E1TlE5S0k3N1hcLzdJV0k2ZFpXTFNTdTVaWURabmhMd00ydHdOeVczME9SbVpQNWFzY0gyZkYweHF3ZjBIVHFzcWhEaHNmaEFicUlxR1RcL2srUlFsQT09IiwibWFjIjoiODY4NzFkZmY4NzA1MTQyYTY2Mjk3Y2YzY2Q1OWQ4NmM0ZGJmYmMwOTlkYzg0NjU4YTY5MzZiMzBhMjFmMjMxZCJ9',
        'Host': 'rong.36kr.com',
        'Referer': 'https://rong.36kr.com/list/detail&?sortField=HOT_SCORE',
        'User-Agent': generate_user_agent(),
    }
    r = requests.get(data_url, headers=headers)
    print(r.status_code, 'data')
    print(r.text)


from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys









if __name__ == '__main__':
    # 模拟登陆，获取数据
    login()

    # 使用cookie登陆，获取数据
    login_by_cookie()

    # 使用selenium+chrome登陆获取cookie
