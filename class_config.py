#encoding=utf-8
import os
'''
配置文件
'''
Mongo_uri = 'mongodb://192.168.121.1:27017'
Logger_file = 'spider.log'
PATH = os.getcwd() + '/Lengyue-SpiderEngine'

def getSYSinfo(dbc):
    return dbc.get_one('info',{'name':'SYSconfig'})