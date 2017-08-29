#encoding = utf-8

#引入私有类
import class_config
import class_MongoDB
import class_logger
import random
import time
import json
import string
import class_plugins
from flask import Flask, render_template,request,redirect,make_response,url_for

'''
冷月私有爬虫引擎v1
结合多线程检测控制
主程序
'''


app = Flask(__name__)
def page_getinfo(p):
    page = {'now':p,
            'menus':[],
            'users':[],
            'update':{},
            'menusinfo':[]
            }
    if p == 'users':
        i = 0
        for u in Main_dbc.get_all('users',{}):
            i += 1
            u['id'] = i
            u['group'] = str(u['group'])
            page['users'].append(u)
        return ('users',page)

    if p == 'menu':
        i = 0
        for u in Main_dbc.get_all('pages',{}):
            i += 1
            u['id'] = i
            page['menusinfo'].append(u)
        return ('menusinfo', page)

    if p == 'updateUser':
        dbret = Main_dbc.get_one('users', {'username':request.args.get('username')})
        if dbret != None:
            page['update']['username'] = dbret['username']
            page['update']['password'] = dbret['password']
            page['update']['groups'] = ''
            for mps in dbret['group']:
                page['update']['groups'] = page['update']['groups'] + mps + ';'
        else:
            page['update']['username'] = '用戶不存在'
        return ('update', page)

    if p == 'updateMenu':
        dbret = Main_dbc.get_one('pages', {'url':request.args.get('url')})
        if dbret != None:
            page['update'] = dbret
        else:
            page['update']['name'] = '菜單不存在'
        return ('update', page)
    return ('now',page)

#权限检查器
def check_login(token):
    if token == None:
        return False
    dbret = Main_dbc.get_one('users',{'token':token})
    if dbret != None:
        return dbret
    else:
        return False

#主頁
@app.route('/')
def show_index():
    ckr = check_login(request.cookies.get('token'))
    if ckr != False:
        return redirect('/main/' + ckr['username'])
    linfo = Main_dbc.get_one('info',{'page':'login'})
    page = {'title':linfo['title'],
            'favicon':Main_cfg['favicon'],
            'appicon':Main_cfg['appicon']
            }
    return render_template('index.html', page = page)

#用戶進入主界面
@app.route('/main/<username>')
def show_main(username):
    #检察权限
    ckr = check_login(request.cookies.get('token'))
    if ckr == False:
        return redirect('/')
    #获取页面参数
    p = request.args.get('page')
    if p == None:
        p = 'panel'
    linfo = Main_dbc.get_one('pages', {'url': p})
    pinfo = Main_dbc.get_one('info', {'page': 'main'})
    if linfo == None:
        page = {'username': ckr['username'],
                'description': '',
                'title': pinfo['title'] + ' - ' + '404',
                'favicon': Main_cfg['favicon'],
                'appicon': Main_cfg['appicon'],
                'now':'404'
                }
        return render_template('main.html', page=page)

    page = {'username':ckr['username'],
            'description':linfo['description'],
            'title':pinfo['title'] + ' - ' + linfo['name'],
            'favicon':Main_cfg['favicon'],
            'appicon':Main_cfg['appicon'],
            'now':p,
            'menus':[],
            'plugin':{},
            'select':p}

    #获取普通页面数据
    (a,b) = page_getinfo(p)
    page[a] = b[a]
    #处理菜单生产 验证
    auth = False
    for group in ckr['group']:
        pages = Main_dbc.get_all('pages', {'group': group})
        for i in pages:
            if i['show'] == 1:
                page['menus'].append(i)
            if i['url'] == p:
                auth = True

    if auth == False:
        page['now'] = 'auth'
        return render_template('main.html', page=page)

    #判断是否加载插件
    if linfo['father'] != "":
        args = {'requests': request.args, 'user': ckr, 'cookies': request.cookies}
        (page_plugin,now) = Main_plugins.exec(linfo['father'], 'build_page', args)
        page['plugin'] = page_plugin
        page['now'] = now
        Main_logger.info(now)
    Main_logger.info(page)

    try:
        return render_template('main.html', page=page)
    except:
        page['now'] = '404'
        return render_template('main.html', page=page)



'''

API区块

'''

#登录
@app.route('/mapi/<username>/login')
def mapi_login(username):
    ckr = check_login(request.cookies.get('token'))
    if ckr == False:
        ret = {'state': 400, 'msg': 'No Auth'}
        return json.dumps(ret)
    try:
        dbret = Main_dbc.get_one('users',{'username':username,'password':request.args.get('password')})
        Main_logger.info('DB return -> ' + str(dbret))
        if dbret != None:
            ret = {'state':200,'msg':'登录成功'}
            token = ''.join(random.sample(string.ascii_letters+string.digits, 20))
            ctime = time.time()
            Main_dbc.update('users',dbret,{'last_login':ctime,'token':token})
            ret['token'] = token
            ret['username'] = username
            ret['group'] = dbret['group']
        else:
            ret = {'state':201,'msg':'用户名或密码错误'}
    except:
        ret = {'state':500,'msg':'服务器错误'}
    return json.dumps(ret)



#登出
@app.route('/mapi/<username>/logout')
def mapi_logout(username):
    ckr = check_login(request.cookies.get('token'))
    if ckr == False:
        ret = {'state': 400, 'msg': 'No Auth'}
        return json.dumps(ret)
    resp = make_response(render_template('logout.html',url = url_for('show_index')))
    resp.delete_cookie('token')
    return resp

#创建用户
@app.route('/mapi/<username>/create')
def mapi_create(username):
    ckr = check_login(request.cookies.get('token'))
    if ckr == False:
        ret = {'state': 400, 'msg': 'No Auth'}
        return json.dumps(ret)
    try:
        dbret = Main_dbc.get_one('users',{'username':username})
        Main_logger.info('DB return -> ' + str(dbret))
        if dbret != None:
            ret = {'state':201,'msg':'用戶名已存在'}
        else:
            groups = request.args.get('groups').split(';')
            info = {
                "username": username,
                "password": request.args.get('password'),
                "group": groups,
                "token": "",
                "last_login": 0
            }
            dbret = Main_dbc.insert_one('users', info)
            ret = {'state':200,'msg':'注冊成功'}
    except:
        ret = {'state':500,'msg':'服务器错误'}
    return json.dumps(ret)


#新建组
@app.route('/mapi/group/add')
def mapi_group_create():
    ckr = check_login(request.cookies.get('token'))
    if ckr == False:
        ret = {'state': 400, 'msg': 'No Auth'}
        return json.dumps(ret)
    try:
        dbret = Main_dbc.get_one('pages',{'url':request.args.get('url')})
        Main_logger.info('DB return -> ' + str(dbret))
        if dbret != None:
            ret = {'state':201,'msg':'URL已存在'}
        else:
            info = {
                "name": request.args.get('name'),
                "url": request.args.get('url'),
                "group": request.args.get('group'),
                "css": request.args.get('css'),
                "show": int(request.args.get('show')),
                "description":request.args.get('description'),
                "father":""
            }
            dbret = Main_dbc.insert_one('pages', info)
            ret = {'state':200,'msg':'注冊成功'}
    except:
        ret = {'state':500,'msg':'服务器错误'}
    return json.dumps(ret)


#更新用户数据
@app.route('/mapi/<username>/update')
def mapi_update(username):
    ckr = check_login(request.cookies.get('token'))
    if ckr == False:
        ret = {'state': 400, 'msg': 'No Auth'}
        return json.dumps(ret)
    try:
        dbret = Main_dbc.get_one('users',{'username':username})
        Main_logger.info('DB return -> ' + str(dbret))
        if dbret != None:
            groups = request.args.get('groups').split(';')
            Main_dbc.update('users',{'username':username},{
                "password": request.args.get('password'),
                "group": groups
            })
            ret = {'state':200,'msg':'提交成功'}
        else:
            ret = {'state':201,'msg':'用戶不存在'}
    except:
        ret = {'state':500,'msg':'服务器错误'}
    return json.dumps(ret)



#更新菜单
@app.route('/mapi/menu/update')
def mapi_menu_update():
    ckr = check_login(request.cookies.get('token'))
    if ckr == False:
        ret = {'state': 400, 'msg': 'No Auth'}
        return json.dumps(ret)
    try:
        dbret = Main_dbc.get_one('pages',{'url':request.args.get('url')})
        Main_logger.info('DB return -> ' + str(dbret))
        if dbret != None:
            Main_dbc.update('pages',{'url':request.args.get('url')},{
                "name": request.args.get('name'),
                "url": request.args.get('url'),
                "group": request.args.get('group'),
                "css": request.args.get('css'),
                "show": int(request.args.get('show')),
                "description":request.args.get('description'),
                "father":""
            })
            ret = {'state':200,'msg':'提交成功'}
        else:
            ret = {'state':201,'msg':'url不存在'}
    except:
        ret = {'state':500,'msg':'服务器错误'}
    return json.dumps(ret)


#删除用户
@app.route('/mapi/<username>/remove')
def mapi_remove(username):
    ckr = check_login(request.cookies.get('token'))
    if ckr == False:
        ret = {'state': 400, 'msg': 'No Auth'}
        return json.dumps(ret)
    try:
        dbret = Main_dbc.get_one('users',{'username':username})
        Main_logger.info('DB return -> ' + str(dbret))
        if dbret == None:
            ret = {'state':201,'msg':'用戶不存在'}
        else:
            Main_dbc.remove('users',{'username':username})
            ret = {'state':200,'msg':'刪除成功'}
    except:
        ret = {'state':500,'msg':'服务器错误'}
    return redirect('/main/233?page=users')
    #return json.dumps(ret)

#删除组
@app.route('/mapi/menu/<url>/remove')
def mapi_menu_remove(url):
    ckr = check_login(request.cookies.get('token'))
    if ckr == False:
        ret = {'state': 400, 'msg': 'No Auth'}
        return json.dumps(ret)
    try:
        dbret = Main_dbc.get_one('pages',{'url':url})
        Main_logger.info('DB return -> ' + str(dbret))
        if dbret == None:
            ret = {'state':201,'msg':'菜單不存在'}
        else:
            Main_dbc.remove('pages',{'url':url})
            ret = {'state':200,'msg':'刪除成功'}
    except:
        ret = {'state':500,'msg':'服务器错误'}
    return redirect('/main/233?page=menu')
    #return json.dumps(ret)




#核心部分 插件部分
@app.route('/plugins/<plugname>')
def api_plugin(plugname):
    ckr = check_login(request.cookies.get('token'))
    if ckr == False:
        ret = {'state': 400, 'msg': 'No Auth'}
        return json.dumps(ret)

    if plugname in Main_plugins_list:
        args = {'requests':request.args,'user':ckr,'cookies':request.cookies}
        return Main_plugins.exec(plugname, request.args.get('method'), args , api=1)
    else:
        info = {'state':'400','msg':'Plugin not existed'}
        return json.dumps(info)



#初始化系统
if __name__ == '__main__':
    class_logger.init()
    Main_logger = class_logger.getLogger('SYS')
    Main_logger.info(class_config.Mongo_uri)
    Main_dbc = class_MongoDB.MongoClient(class_config.Mongo_uri,class_logger.getLogger('Mongo'),'SYS')
    Main_cfg = class_config.getSYSinfo(Main_dbc)
    Main_logger.info('SYScfg -> ' + str(Main_cfg))
    Main_dbc.setUnique('users', 'username')
    Main_dbc.setUnique('pages', 'url')
    Main_dbc.setUnique('plugins', 'model')
    Main_plugins = class_plugins.plugins(Main_dbc)
    Main_plugins_list = Main_plugins.getlist()
    app.run(host='0.0.0.0', port=6677)
