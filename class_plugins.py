import shutil
import class_MongoDB
import class_logger
import class_config
import os.path
'''
插件模块
'''
class plugins:
    Main_plugins = {}
    #初始化
    def __init__(self,Main_dbc):
        for plug in Main_dbc.get_all('plugins', {}):
            self.Main_plugins[plug['model']] = __import__('plugins.' + plug['model'] + '.plugin_' + plug['model'])
            self.Main_plugins[plug['model']] = eval(
                "self.Main_plugins[plug['model']]." + plug['model'] + ".plugin_" + plug['model'])
            self.Main_plugins[plug['model']].init(
                dbc=class_MongoDB.MongoClient(class_config.Mongo_uri, class_logger.getLogger('Mdb - ' + plug['name']),
                                              plug['db']), logger=class_logger.getLogger(plug['name']))
            plug_templates = class_config.PATH + "/plugins/" + plug['model'] + "/templates"
            for parent,dirnames,filenames in os.walk(plug_templates):
                for filename in filenames:
                    shutil.copyfile(plug_templates + '/' + filename, class_config.PATH + "/templates/plugin_" + plug['model'] + "_" + filename)

    #执行
    def exec(self,plugname,method,args,api=0):
        if api == 1:
            return eval('self.Main_plugins[plugname].' + method)(args)
        else:
            (a,b) = eval('self.Main_plugins[plugname].' + method)(args)
            return (a,'plugin_' + plugname  + '_' + b)

    #获取列表
    def getlist(self):
        return self.Main_plugins