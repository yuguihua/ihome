import logging
import os
import threading
from pydub import AudioSegment
import datetime
import socket
import hashlib

def check_net_status(server='www.baidu.com'):
    """
        Checks if dingdang can connect a network server.
        Arguments:
            server -- (optional) the server to connect with (Default:
                      "www.baidu.com")
        Returns:
            True or False
        """
    logger = logging.getLogger(__name__)
    logger.debug("正在检测网络状态 '%s'...", server)
    try:
        # see if we can resolve the host name -- tells us if there is
        # a DNS listening
        host = socket.gethostbyname(server)
        # connect to the host -- tells us if the host is actually
        # reachable
        socket.create_connection((host, 80), 2)
    except Exception as e:
        logger.debug("网络不可用:%s"%e)
        return False
    else:
        logger.debug("网络连接正常...")
        return True


def mp3_to_wav(mp3_file):
    target = mp3_file.replace(".mp3", ".wav")
    if os.path.exists(mp3_file):
        voice = AudioSegment.from_mp3(mp3_file)
        voice.export(target, format="wav")
        return target
    else:
        logging.debug("文件错误")
        return None


def datetime(format='%Y-%m-%d %H:%M:%S'):
    return datetime.datetime.now().strftime(format)


def sec2time(sec, n_msec=3):
    '''
    Convert seconds to 'D days, HH:MM:SS.FFF'
    :param sec:
    :param n_msec:
    :return:
    '''
    if hasattr(sec, '__len__'):
        return [sec2time(s) for s in sec]
    m, s = divmod(sec, 60)
    h, m = divmod(m, 60)
    d, h = divmod(h, 24)
    if n_msec > 0:
        pattern = '%%02d:%%02d:%%0%d.%df' % (n_msec + 3, n_msec)
    else:
        pattern = r'%02d:%02d:%02d'
    if d == 0:
        return pattern % (h, m, s)
    return ('%d days, ' + pattern) % (d, h, m, s)


def get_cpu_temp():
    '''
    获取cpu温度
    :return:
    '''
    result = 0.0
    try:
        tempFile = open("/sys/class/thermal/thermal_zone0/temp")
        res = tempFile.read()
        result = float(res) / 1000
    except Exception as e:
        logging.debug('get cpu temp error:%s'%e)
        pass
    return result


def get_week(day=None):
    '''
    获取中文星期几
    :param day:
    :return:
    '''
    week_day_dict = {
        0: '星期一',
        1: '星期二',
        2: '星期三',
        3: '星期四',
        4: '星期五',
        5: '星期六',
        6: '星期天',
    }
    if day is None:
        d = datetime.datetime.now()
        day = d.weekday()
    return week_day_dict[day]


def md5(string):
    '''
    md5加密码
    :param self:
    :param string:
    :return:string
    '''
    m = hashlib.md5()
    m.update(string.encode('utf-8'))
    return m.hexdigest()