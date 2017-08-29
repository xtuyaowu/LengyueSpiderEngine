#encoding=utf-8
# 配置日志信息
import logging
import class_config

def init():
    logging.basicConfig(level=logging.DEBUG,
                        format='%(asctime)s %(name)-40s %(levelname)-8s %(message)s',
                        datefmt='%m-%d %H:%M',
                        filename=class_config.Logger_file,
                        filemode='w')
    # 定义一个Handler打印INFO及以上级别的日志到sys.stderr
    console = logging.StreamHandler()
    console.setLevel(logging.INFO)
    # 设置日志打印格式
    formatter = logging.Formatter('%(asctime)s | %(name)-25s | %(levelname)-8s| %(message)s')
    console.setFormatter(formatter)
    # 将定义好的console日志handler添加到root logger
    logging.getLogger('').addHandler(console)

def getLogger(name):
    return logging.getLogger(name)
