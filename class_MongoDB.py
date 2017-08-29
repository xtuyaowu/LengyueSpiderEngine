#encoding=utf-8
#数据库类
import pymongo

class MongoClient:
    #初始化
    def __init__(self,uri,logger,dbname):
        self.logger = logger
        # 初始化Mongo连接
        self.MongoClient = pymongo.MongoClient(uri)
        self.logger.info('Mongodb Connected to ' + uri)
        self.dbc = self.MongoClient[dbname]

    def setUnique(self,collection,index):
        self.dbc[collection].ensure_index(index, unique=True)
    #插入
    def insert_one(self,collection,info):
        try:
            self.dbc[collection].insert_one(info)
            self.logger.info('Insert into ' + collection + ' Succeed')
        except:
            self.logger.warn('Insert into ' + collection + ' Failed')

    # 刪除
    def remove(self, collection, info):
        try:
            self.dbc[collection].remove(info)
            self.logger.info('Remove from ' + collection + ' Succeed')
        except:
            self.logger.warn('Remove from ' + collection + ' Failed')
    #获取一条
    def get_one(self,collection,query):
        try:
            info = self.dbc[collection].find_one(query)
            self.logger.info('Get one -> ' + str(query) + ' from ' + collection + ' Succeed')
            return info
        except:
            self.logger.warn('Get one -> ' + str(query) + ' from ' + collection + ' Failed')
    #获取全部
    def get_all(self,collection,query):
        try:
            info = self.dbc[collection].find(query)
            self.logger.info('Get all -> ' + str(query) + ' from ' + collection + ' Succeed')
            return info
        except:
            self.logger.warn('Get all -> ' + str(query) + ' from ' + collection + ' Failed')
    #更新数据
    def update(self,collection,query,change):
        try:
            self.dbc[collection].update(query, {"$set": change})
            self.logger.info('Update -> ' + str(query) + ' from ' + collection + ' Succeed')
        except:
            self.logger.warn('Update -> ' + str(query) + ' from ' + collection + ' Failed')