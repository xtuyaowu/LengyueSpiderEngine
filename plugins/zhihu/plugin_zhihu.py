#encoding=utf-8
'''
知乎插件
'''
import json


def init(dbc,logger):
    global plugin_dbc,plugin_logger
    plugin_dbc = dbc
    plugin_logger = logger
    logger.info('Inited')

def getinfo(a):
    ret = []
    for i in plugin_dbc.get_all('Users',{}).limit(100):
        ret.append({'url_token':i['url_token']})
    return json.dumps(ret)

def showexec(args):
    args['user']['_id'] = str(args['user']['_id'])
    return json.dumps(args)

def build_page(args):
    if 'sub' in args['requests']:
        return ({'sub':'sss'}, args['requests']['sub'])
    else:
        return (args, 'main')