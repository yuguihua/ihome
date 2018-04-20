import logging
from core import constants
import os
import tempfile
from urllib import parse
import requests
from core.cache.redis import rds
from uuid import getnode as get_mac
import subprocess
from abc import ABCMeta, abstractmethod

class AbstractTTSEngine(object):
    """
    Generic parent class for all speakers
    """
    __metaclass__ = ABCMeta

    @classmethod
    def get_config(cls):
        return {}

    @classmethod
    def get_instance(cls):
        config = cls.get_config()
        instance = cls(**config)
        return instance

    @classmethod
    @abstractmethod
    def is_available(cls):
        return True

    def __init__(self, **kwargs):
        self._logger = logging.getLogger(__name__)



class BaiduTTS(AbstractTTSEngine):
    """
    使用百度语音合成技术
    要使用本模块, 首先到 yuyin.baidu.com 注册一个开发者账号,
    之后创建一个新应用, 然后在应用管理的"查看key"中获得 API Key 和 Secret Key
    填入 profile.xml 中.
    ...
        baidu_yuyin: 'AIzaSyDoHmTEToZUQrltmORWS4Ott0OHVA62tw8'
            api_key: 'LMFYhLdXSSthxCNLR7uxFszQ'
            secret_key: '14dbd10057xu7b256e537455698c0e4e'
        ...
    """

    SLUG = "baidu-tts"

    def __init__(self, config):
        self._logger = logging.getLogger(__name__)
        self.api_key = config['baidu_yuyin']['api_key']
        self.secret_key = config['baidu_yuyin']['secret_key']
        self.per = config['baidu_yuyin']['per']
        self.token = ''

    def get_token(self):
        result = rds.loadData(key='baidu_stt',format='json')
        if result is not None:
            self._logger.info("命中缓存Baidu tts token:%s" % result['access_token'])
            return result['access_token']
        else:
            URL = 'http://openapi.baidu.com/oauth/2.0/token'
            params = parse.urlencode({'grant_type': 'client_credentials',
                                      'client_id': self.api_key,
                                      'client_secret': self.secret_key})
            r = requests.get(URL, params=params)
            try:
                r.raise_for_status()
                token = r.json()['access_token']
                rds.saveData(key='baidu_stt',value=r.json(),lifetime=r.json()['expires_in'])
                return token
            except requests.exceptions.HTTPError:
                self._logger.critical('Token request failed with response: %r',
                                      r.text,
                                      exc_info=True)
                return ''

    def split_sentences(self, text):
        punctuations = ['.', '。', ';', '；', '\n']
        for i in punctuations:
            text = text.replace(i, '@@@')
        return text.split('@@@')

    def get_speech(self, phrase):
        if self.token == '':
            self.token = self.get_token()
        query = {'tex': phrase,
                 'lan': 'zh',
                 'tok': self.token,
                 'ctp': 1,
                 'cuid': str(get_mac())[:32],
                 'per': self.per
                 }
        r = requests.post('http://tsn.baidu.com/text2audio',
                          data=query,
                          headers={'content-type': 'application/json'})
        try:
            ctype = r.headers['content-type']
            if 'mp3' in ctype:
                with tempfile.NamedTemporaryFile(suffix='.mp3', delete=False) as f:
                    f.write(r.content)
                    f.close()
                    return f.name

            result = r.json()
            if result['err_msg'] is not None:
                self._logger.info('Baidu TTS failed with response: %r',
                                      result['err_msg'],
                                      exc_info=True)
                return None
        except Exception as e:
            self._logger.error('TTS Error:%s' %e)
            pass


def get_engine_by_slug(slug=None):
    """
    Returns:
        A speaker implementation available on the current platform
    Raises:
        ValueError if no speaker implementation is supported on this platform
    """

    if not slug or type(slug) is not str:
        raise TypeError("Invalid slug '%s'", slug)

    for engine in get_tts():
        if hasattr(engine,'SLUG') and engine.SLUG == slug:
            return engine


def get_tts():
    def get_subclasses(cls):
        subclasses = set()
        for subclass in cls.__subclasses__():
            subclasses.add(subclass)
            subclasses.update(get_subclasses(subclass))
        return subclasses
    return [tts_engine for tts_engine in
            list(get_subclasses(AbstractTTSEngine))
            if hasattr(tts_engine, 'SLUG') and tts_engine.SLUG]