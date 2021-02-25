# -*- coding: utf-8 -*-
test = True
__auther__ = 'XL'
import re
import time
from bs4 import BeautifulSoup
import requests
from selenium import webdriver
import gevent
from gevent import monkey
from urllib.parse import urlparse
import random

monkey.patch_all()
requests_head={
    'User-Agent':'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:60.0) Gecko/20100101 Firefox/60.0'  #伪造请求头中的浏览器
}

class Pachong(object):
    '''
    爬虫父类,所有爬虫应该基于此类
    '''
    def __init__(self,main_url):
        self.main_url=main_url
        self.domain='{urx.scheme}://{urx.netloc}'.format(urx=urlparse(self.main_url))
        self.target_url=''

    @staticmethod
    def Req(url):
        '''
        网络请求
        :return:response对象
        '''
        respond=requests.get(url=url,headers=requests_head,verify=False)
        return respond

    @staticmethod
    def WebDriver(url):
        '''
        大量Ajax渲染的页面，用该方法抓取
        :return: 返回Html字符串
        '''
        Browser=webdriver.Firefox()
        Browser.get(url)
        Data=Browser.page_source
        Browser.close()
        return Data

    @staticmethod
    def Filename_correcter(title):
        title = re.sub('/', '', title)
        title = re.sub('\?', '', title)
        title = re.sub('\.', '', title)
        title = re.sub(':', '', title)
        title = re.sub('\*', '', title)
        title = re.sub('\"', '', title)
        title = re.sub('<', '', title)
        title = re.sub('>.', '', title)
        title = re.sub('|', '', title)
        return title

    def Extract_main(self):
        '''
        提取菜单页面的文章URL，由子类实现
        :return: 一个装满待爬取url的可迭代对象
        '''
        pass

    def Extract_article(self):
        '''
        提取目标文章的首页评论，由子类实现
        :return: 一个字符串（媒体名称+文章标题） 和 一个装满评论的可迭代对象
        '''
        pass

    def run(self):
        '''
        主程序运行
        :return:
        '''
        url_list=self.Extract_main(self.Req(self.main_url))
        count=len(url_list)
        count_finished=0
        for comment_page_url in url_list:
            title,comment_list=self.Extract_article(self.WebDriver(comment_page_url))
            title=self.Filename_correcter(title)
            title=self.medianame+title
            with open(title+'.txt','w',encoding='utf-8') as f:
                f.writelines(title+'\n')
                for item in comment_list:
                    f.writelines(item+'\n')
            count_finished+=1
            print('{media_name}:{model}----进度{finished}/{amount}'.format(media_name=self.medianame,model=self.modelname,finished=count_finished,amount=count))
            sleep_time=random.uniform(1.1,3.2)
            time.sleep(sleep_time)                  #为防止被识别为机器人，随机暂停一段时间。

class Autohome(Pachong):
    def __init__(self,main_url,model_name):
        super(Autohome, self).__init__(main_url)
        self.medianame='汽车之家'
        self.modelname=model_name

    def Extract_main(self,respond):
        '''
        解析车型的目录页面
        :return:以列表的形式返回文章的评论页
        '''
        url_list=[]
        html=respond.text
        soup=BeautifulSoup(html,'lxml')
        soup=soup.find(class_='cont-info')
        soup=soup.find(name='ul')
        soup=soup.find_all(name='h3')
        for item in soup:
            code=re.search('href=.*/(\d+?).html"',item.prettify()).group(1)
            url='https://www.autohome.com.cn/comment/Articlecomment.aspx?articleid='+code
            url_list.append(url)
        return url_list

    def Extract_article(self,data):
        '''

        解析评论页面
        :return:文章标题，装满评论的列表
        '''
        message_list=[]
        soup=BeautifulSoup(data,'lxml')
        title=soup.find(name='title').string
        soup=soup.find(id='reply-list')
        soup=soup.find_all(name='dd')
        for item1 in soup:
            message=item1.find(name='p')
            message=message.text
            message_list.append(message)
        return title,message_list

class Bitauto(Pachong):

    def __init__(self,main_url,modelname):
        super(Bitauto, self).__init__(main_url)
        self.medianame='易车网'
        self.modelname=modelname

    def Extract_main(self,respond):
        '''
        解析车型的目录页面
        :return:以列表的形式返回文章的评论页
        '''
        url_list=[]
        html=respond.text
        soup=BeautifulSoup(html,'lxml')
        soup=soup.find(class_='main-inner-section')
        soup=soup.find_all(class_='figure')
        for item in soup:
            message=re.search('href=.*?/(\d+?).html"',item.prettify()).group(1)
            message=message[3:]
            url=''.join(['http://news.bitauto.com/comment4/list_1_',message,'.html'])
            url_list.append(url)
        return url_list

    def Extract_article(self,data):
        '''
        解析评论页面
        :return:文章标题，装满评论的列表
        '''
        message_list=[]
        soup=BeautifulSoup(data,'lxml')
        title=soup.find(class_='comment-tit')
        title=title.find(name='h2')
        title=str(title)
        title=re.search('>(.*?)<',title).group(1)

        soup=soup.find_all(class_='content')
        for content in soup:
            comment=str(content.string)
            message_list.append(comment)
        return title,message_list

class Xcar(Pachong):

    def __init__(self,main_url,model_name):
        super(Xcar, self).__init__(main_url)
        self.medianame='爱卡汽车'
        self.modelname=model_name

    def Extract_main(self,respond):
        '''
        解析车型的目录页面
        :return:以列表的形式返回文章的评论页
        '''
        url_list=[]
        html=respond.text
        soup=BeautifulSoup(html,'lxml')
        soup=soup.find_all(class_='post_tt')
        for content in soup:
            data=re.search('<a.*?/news_(.*?)_1.html"',str(content)).group(1)
            url='http://comment.xcar.com.cn/comment.php?nid='+data
            url_list.append(url)
        return url_list




    def Extract_article(self,data):
        '''
        解析评论页面
        :return:文章标题，装满评论的列表
        '''

        message_list=[]
        soup=BeautifulSoup(data,'lxml')
        title=soup.find(name='title').text
        soup=soup.find_all(class_='comment_main_write')
        for content in soup:
            message=content.find(name='p')
            message=message.text
            if message=='':
                message='灌水的表情，跳过'
            message_list.append(message)
        return title,message_list










Pachong1=Autohome('https://www.autohome.com.cn/4453/0/0-0-1-0/','karoq')
Pachong2=Bitauto('http://car.bitauto.com/karoq/wenzhang/','karoq')
Pachong3=Xcar('http://newcar.xcar.com.cn/3706/news_1.htm','karoq')
run1=Pachong3.run
run2=Pachong2.run
run3=Pachong1.run
gevent.joinall([gevent.spawn(run1),gevent.spawn(run2),gevent.spawn(run3)])
