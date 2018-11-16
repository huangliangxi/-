#!/usr/bin/python3
# -*-coding:utf-8 -*-
# Author:Eminjan
# @Time  :2018/5/14 21:31
# 定时抓取消息，发送到微信群
# 
# date:2018-08-08

import urllib.request
import datetime
import time
import re
from pyquery import PyQuery as pq
import itchat
from apscheduler.schedulers.background import BlockingScheduler
from itchat.components import hotreload

# 杂学杂问，搜狐网址
sohu_url = 'http://m.sohu.com/media/181028'
sohu_url_prefix = 'http://m.sohu.com'


# 获取今天的日期
def getCurrentDateAndTime():
    global today
    global str_today
    # 消息的标题，例如：8月9日早读分享
    global msg_title
    today = datetime.date.today()
    str_today = str(int(str(today).split('-')[1])) + '月' + str(int(str(today).split('-')[2])) + '日'
    msg_title = str_today + '早读分享'
    # print(msg_title)


def getTodayWeek():
    weekNum = int(time.strftime('%w', time.localtime(time.time())))
    if weekNum == 0:
        return '周日'
    if weekNum == 1:
        return '周一'
    if weekNum == 2:
        return '周二'
    if weekNum == 3:
        return '周三'
    if weekNum == 4:
        return '周四'
    if weekNum == 5:
        return '周五'
    if weekNum == 6:
        return '周六'


# 访问网页,返回html
def getPageData(url):
    try:
        response = urllib.request.urlopen(url)
        # 开始读取
        if response.getcode() != 200:
            print('读取网页失败，请关注！错误码==' + str(response.getcode()))
        else:
            # 得到首页的目录列表
            page_data = response.read().decode('utf-8')
            print('成功获取网页内容')
            # print('网页内容=='+page_data)
            return page_data
    except:
        print('读取网页失败，请关注！')


# 找到早读分享网页的链接地址
def getPageHref(page_first):
    html_doc = pq(page_first)
    # print(html_doc.html())
    html_lis = html_doc('li')
    for li in html_lis.items():
        h4 = li.find('h4').eq(0)
        # 找到内容的标题
        if h4.text().find(msg_title) != -1:
            # 杂学杂问 8月8日早读分享
            # print(h4.text())
            href = li.find('a').eq(0).attr('href')
            page_two_href = sohu_url_prefix + href
            print(msg_title + '==' + page_two_href)
            # 找到链接，返回
            return page_two_href


# 解析早读分享的网址，得到最终的数据data
def getFinalData(page_two):
    # print('page_two=='+page_two+'==')
    final_data = []
    msg_title_2 = str_today + getTodayWeek() + '早读分享'
    final_data.append(msg_title_2 + '：')
    html_doc = pq(page_two)
    html_articles = html_doc('article')
    # 找到每条消息的内容
    for p in html_articles.find('p'):
        # 获取到所有内容
        # print(pq(p).text())
        # 第一个p标签内容去掉
        data_each = pq(p).text()
        if data_each.find('早读分享') == -1:
            # print(data_each)
            final_data.append(data_each)
            # 结尾行
            if data_each.find('美好一天') != -1:
                break

    final_data = '\n\n'.join(final_data).replace('⭐️', '☆')
    print(final_data)
    return final_data


# 1、发送消息到微信好友
def sendMsgToFriend(friend_name, message):
    the_friend = itchat.search_friends(name= friend_name)
    friend_username = the_friend[0]["UserName"]
    itchat.send(message, friend_username)


# 2、发送消息到微信群聊
def sendMsgToQunliao(qunliao_name, message):
    the_chatroom = itchat.search_chatrooms(name="备份")
    qunliao_username = the_chatroom[0]["UserName"]
    itchat.send(message, qunliao_username)


# 3、发送消息到微信助手
def sendMsgToMyself(message):
    itchat.send(message, 'filehelper')


# 定义发送消息的任务
def myJob():
    getCurrentDateAndTime()
    # 微信自动登录，热加载
    itchat.auto_login(hotReload=True)
    print('itchat自动登录成功')
    # 获得发送的内容
    lastMsg = getFinalData(getPageData(getPageHref(getPageData(sohu_url))))
    # sendMsgToQunliao('itchat学习',lastMsg)
    sendMsgToFriend("杨鑫", lastMsg)
    sendMsgToMyself(lastMsg)

    # 保持运行
    itchat.run(blockThread=False)


def mainJob():
    # 新建定时任务
    scheduler = BlockingScheduler()
    # 每隔3小时发送一次
    # scheduler.add_job(myJob, trigger='cron', hour='0/3', minute='0/1')
    scheduler.add_job(myJob, 'interval', minutes=1)
    # scheduler.add_job(send_msg, 'cron', year=2018, month=7, day=28, hour=16, minute=5, second=30)

    print('定时任务开始启动，scheduler.start==' + str(datetime.datetime.now()))
    scheduler.start()


if __name__ == '__main__':
    # myJob()
    mainJob()










