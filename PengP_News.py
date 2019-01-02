import requests
import os
import pymongo
import time
from config import *
from urllib.parse import urlencode
from lxml import etree
from multiprocessing import Pool

def structure_urls():
    '''
    构造每个索引页面的URL
    :return:
    '''
    urls = []
    base_url = 'https://www.thepaper.cn/load_index.jsp?'
    for i in range(1, 26):
        params = {
                'nodeids': 25635,
                'pageidx': i
        }
        url = base_url + urlencode(params)
        # yield url
        urls.append(url)
    return urls

def structure_links(titles,links):
    '''
    构造每个新闻链接
    :param titles:
    :param links:
    :return:
    '''
    item = {}
    base_url = 'https://www.thepaper.cn/'
    for i in range(len(titles)):
        item[titles[i]] = base_url + links[i]
    return item

def fix_dir(dir_name):
    '''
    将解析得到的新闻标题中的特殊字符进行修改，避免在Windows上创建目录时报错
    :param dir_name:
    :return:
    '''
    if '<' in dir_name:
        dir_name = dir_name.replace('<', '')
    if '>' in dir_name:
        dir_name = dir_name.replace('>', '')
    if '?' in dir_name:
        dir_name = dir_name.replace('?', '？')
    if '"' in dir_name:
        dir_name = dir_name.replace('"', '”')
    if ':' in dir_name:
        dir_name = dir_name.replace(':', '：')
    if '/' in dir_name:
        dir_name = dir_name.replace('/', ' ')
    if '\\' in dir_name:
        dir_name = dir_name.replace('\\', ' ')
    if '*' in dir_name:
        dir_name = dir_name.replace('*', ' ')
    if '|' in dir_name:
        dir_name = dir_name.replace('|', '｜')
    return dir_name

def download(url):
    '''
    发送请求并返回响应
    :param url:
    :return:
    '''
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36'
    }
    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            if response.encoding == 'utf-8' or response.encoding == 'UTF-8':
                return response.text
            # print('%s的编码有问题^V^,它的编码是：%s' % (response.url, response.encoding))
    except Exception as e:
        print(e)

def parse_News_links(text):
    '''
    解析索引页面，获得每个新闻链接
    :param text:
    :return:
    '''
    try:
        html = etree.HTML(text)
        titles = html.xpath('//h2/a/text()')
        links = html.xpath('//h2/a/@href')
        News_links = structure_links(titles, links)
        return News_links
    except Exception as e:
        print(e)

def parse_News_content(content):
    '''
    解析新闻详情页面，获得新闻内容
    :param content:
    :return:
    '''
    try:
        html = etree.HTML(content)
        article = html.xpath('//div[@class="news_txt"]//text() | //div[@class="news_txt"]//img/@src')
        img = html.xpath('//div[@class="news_txt"]//img/@src')
        if article != []:
            article = '\n'.join(article)
            return article, img
        else:
            return '', []
    except Exception as e:
        print(e)
        return '', []

def save_mongo(tt, content, img):
    '''
    保存到MongoDB
    :param tt:
    :param content:
    :param img:
    :return:
    '''
    try:
        contents = {
            'title': tt,
            'content': content,
            'img': img,
        }
        result = collection.insert_one(contents)
    except Exception as e:
        print(e)
def save_txt(tt, content):
    '''
    保存到本地
    :param tt:
    :param content:
    :return:
    '''
    tt = fix_dir(tt)
    fp = r'%s\%s.txt' % (tt, tt)
    try:
        if not os.path.exists(tt):
            os.mkdir(tt)
        if not os.path.exists(fp):
            with open(fp, 'w', encoding='utf-8') as f:
                f.write(content)
                print('%s:保存成功' % fp)
    except Exception as e:
        print(e)

def main(url):
    text = download(url)
    News_links = parse_News_links(text)
    for tt, link in News_links.items():
        content = download(link)
        if content != None:
            article, img = parse_News_content(content)
            if article != None:
                save_txt(tt, article)
                save_mongo(tt, article, img)

if __name__ == '__main__':
    start = time.time()
    urls = structure_urls()
    pool = Pool()
    pool.map(main, urls)
    pool.close()
    pool.join()
    end = time.time()
    print('Total Spend Time: %s' % (end-start))