import os
'''
应用配置
'''
import logging

# 应用打印log等级
LOGGER_LEVEL = logging.DEBUG
'''项目目录'''
APP_PATH = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir))
'''
配置文件
'''
APP_CONFIG_FILE = os.path.join(APP_PATH, 'config/ihome.yml')
'''数据目录'''
DATA_PATH = os.path.join(APP_PATH, "data")
IMAGE_PATH = os.path.join(APP_PATH, "data/images/")
'''缓存文件'''
APP_CACHE_PATH = os.path.join(DATA_PATH,'cache')
"""核心功能库"""
LIB_PATH = os.path.join(APP_PATH, "core")
TEMP_PATH = os.path.join(DATA_PATH, "temp")
"""媒体文件目录"""
MEDIA_PATH = os.path.join(DATA_PATH,'audio')
"""插件目录"""
PLUGIN_PATH = os.path.join(APP_PATH, "plugins")

CONFIG_PATH = os.path.join(APP_PATH, 'config')

def config(*fname):
    return os.path.join(CONFIG_PATH, *fname)


def data(*fname):
    return os.path.join(DATA_PATH, *fname)
