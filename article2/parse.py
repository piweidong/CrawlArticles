# coding: utf8
import re
import json
import lxml.html


def parse_doc(page_raw):
    '''
    :param page_raw: html源码
    :return: Element对象
    '''
    return lxml.html.fromstring(page_raw)


html = '''

<html>
　　<head>
　　　　<meta name="content-type" content="text/html; charset=utf-8" />
　　　　<title>友情链接查询 - 站长工具</title>
　　　　<!-- uRj0Ak8VLEPhjWhg3m9z4EjXJwc -->
　　　　<meta name="Keywords" content="友情链接查询" />
　　　　<meta name="Description" content="友情链接查询" />

　　</head>
　　<body>
　　　　<h1 class="heading">Top News</h1>
　　　　<p style="font-size: 200%">World News only on this page</p>
　　　　Ah, and here's some more text, by the way.
　　　　<p>
           <a href="http://www.4399.com/" target="_blank">4399小游戏</a> 
       </p>

　　　　<a href="http://www.cydf.cn/" rel="nofollow" target="_blank">青少年发展基金会</a> 
　　　　<a href="http://www.4399.com/flash/32979.htm" target="_blank">洛克王国</a> 
　　　　<a href="http://game.3533.com/game/" target="_blank">手机游戏</a>
　　　　<a href="http://game.3533.com/tupian/" target="_blank">手机壁纸</a>
　　　　
　　　　<a href="http://www.91wan.com/" title="游戏">91wan游戏</a>

　　</body>
</html>

'''

doc = parse_doc(html)
print(doc)


# (1)定位html标签节点

a_xpath = "/html/body/a"  # 选择body标签下面的所有a标签，注意不包括p标签下面的a标签节点
a_node_list = doc.xpath(a_xpath)  # 返回节点对象的列表
print(a_node_list)
# 输出：[<Element a at 0x10d8938b8>, ..., <Element a at 0x10d893cc8>]


a_xpath = "//a"  # 选择所有的a标签
a_node_list = doc.xpath(a_xpath)  # 返回节点对象的列表
print(a_node_list)
# 输出：[<Element a at 0x10d893ea8>, ..., <Element a at 0x10d893cc8>]


a_xpath = "//body//a"  # 选择body标签下面的所有a标签，包括p标签下面的a标签
a_node_list = doc.xpath(a_xpath)  # 返回节点对象的列表
print(a_node_list)
# 输出：[<Element a at 0x10d893ea8>, ..., <Element a at 0x10d893cc8>]


# (2)定位到标签的属性

h_xpath = "//h1/@class"  # 选择h1标签的class属性
class_value_list = doc.xpath(h_xpath)
print(class_value_list)
# 输出：['heading']


# (3)定位到标签里面的文本

h_text_xpath = "//h1/text()"  # 选择h1标签下面的text
h_text_list = doc.xpath(h_text_xpath)
print(h_text_list)
# 输出：['Top News']

body_text_xpath = "//body//text()"  # 选择body标签下面的所有text
body_text_list = doc.xpath(body_text_xpath)
print(body_text_list)
# 输出：['\n\u3000\u3000', ..., '91wan游戏', '\n\n\u3000\u3000\n']


# (4)根据特定的属性选择节点

meta_keywords_xpath = "//meta[@name='Keywords']"  # 选择name属性为Keywords的节点
meta_keywords_node_list = doc.xpath(meta_keywords_xpath)  # 返回符合条件的节点列表
print(meta_keywords_node_list)
# 输出：[<Element meta at 0x10d923048>]


meta_desc_xpath = "//meta[contains(@name, 'Descri')]"  # 选择name属性包含Descri的节点
meta_desc_node_list = doc.xpath(meta_desc_xpath)  # 返回符合条件的节点列表
print(meta_desc_node_list)
# 输出：[<Element meta at 0x10d9232c8>]

content_value_xpath = "//meta[contains(@name, 'Keywords')]/@content"
# 选择符合条件的节点的content属性的值
content_value_list = doc.xpath(content_value_xpath)
print(content_value_list)
# 输出：['友情链接查询']


text_xpath = "//body/a[contains(text(), '游戏')]/text()"  # 选择a标签text包含游戏的text
text_list = doc.xpath(text_xpath)
print(text_list)
# 输出：['手机游戏', '91wan游戏']


# （5）获取节点的父亲节点

p_xpath = "//p/a[contains(text(), '4399')]/parent::*"  # text包含4399的a标签的父节点
parent_node_list = doc.xpath(p_xpath)  # 返回父亲节点list
print(parent_node_list[0])  # 注：父亲节点只有一个
# 输出：<Element p at 0x10d9230e8>


# （6）获取后面兄弟标签节点

a_follow_xpath = "//body/a[contains(@href, '4399')]/following-sibling::*"
# href属性包含4399字符串的a标签的后续同级标签节点
a_follow_node_list = doc.xpath(a_follow_xpath)
print(a_follow_node_list)
# 输出：[<Element a at 0x10d893b38>, <Element a at 0x10d893d18>, <Element a at 0x10d893cc8>]


# （7）节点对象的一些常用方法

node = doc.xpath("//a[contains(text(), '洛克')]")[0]  # 得到节点对象
attrib_dict = node.attrib                 # 此节点标签的字典形式的属性
print(attrib_dict)
# 输出：{'href': 'http://www.4399.com/flash/32979.htm', 'target': '_blank'}

node_text = node.text  # 此节点的text
print(node_text)
# 输出：洛克王国

node_tag = node.tag  # 此节点的标签名称
print(node_tag)
# 输出：a

child_node_list = node.getchildren()  # 获取此节点的孩子节点
print(child_node_list)
# 输出：[]  空的原因是此几点无孩子节点

next_node = node.getnext()  # 此节点的一个同级节点
print(next_node)
# 输出：<Element a at 0x10d893b38>  下一个节点的对象

href_list = node.xpath("./@href")  # 此节点下面写xpath，注意前面需要有./ 表面是相对路径
print(href_list)
# ['http://www.4399.com/flash/32979.htm']


# xpath解析36kr新闻详情页

from article1.crawl import _crawl  # 导入篇文章介绍的抓取函数


url = 'http://36kr.com/p/5130007.html'
headers = {
    'Host': '36kr.com',
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.181 Safari/537.36',
}
html = _crawl('get', url, headers)  # 获取到文章源码
doc = parse_doc(html)  # 用lxml.html解析成树形结构对象

title_xpath = "//div[@class='mobile_article']/h1/text()"
print(doc.xpath(title_xpath))
# 输出：[]


data = re.findall(r'props=(.+),locationnal', html)[0]
data = json.loads(data)['detailArticle|post']
print(data['id'], data['title'])
# 输出：5130007 最前线 | 李大霄：中兴或可通过谈判获得一个解决方案


# 正则表达式介绍

article_id_list = re.findall(r'p/(\d+)', 'http://36kr.com/p/5130007.html')
print(article_id_list)  # 输出：['5130007']
# 正则表达式前面的r代表申明这个字符串是原生字符，不会对一些特殊字符进行转义
# \d 匹配数字0-9

domain_list = re.findall(r'//([\d\S]+)\.com', 'http://36kr.com/p/5130007.html')
print(domain_list)  # 输出：['36kr']
# \S 表示匹配 非空白字符
# [...] 表示字符集，对应的位置可以是字符集中任意字符
# . 表示除换行符\n 外的任意字符， \. 前面加个转义符\ 表示是一个普通的 .

article_id_list = re.findall(r'com.*(\d+)', 'http://36kr.com/p/5130007.html')
print(article_id_list)  # 输出：['7']
# 返回的结果并不是我们想要的结果
# * 表示匹配前一个字符0个或多个，是贪婪匹配，尽量多个

article_id_list = re.findall(r'com.*?(\d+)', 'http://36kr.com/p/5130007.html')
print(article_id_list)  # 输出：['5130007']
# 这里得到我我们想要的结果
# ？一般在*和+后面，将贪婪变成非贪婪
