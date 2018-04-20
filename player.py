'''
播放基本类
'''
from core import app
from core import constants
import os
import logging
import subprocess

class Player(object):
    '''
    播放器实现类
    '''
    def __init__(self,audio,tts):
        '''播放引擎,默认是play,ffmpeg,oxplayer'''
        self.player = None

        '''当前播放进程'''
        self._process = None

        '''当前时长'''
        self.duration = 0

        '''当前播放位置'''
        self.position = 0

        self.state = 0

        '''默认顺序播放'''
        self.random = False

        '''默认播放音量'''
        self.volume = 0.7

        '''播放状态,默认没有播放'''
        self.state = -1

        '''默认是音乐播放模式，自动下一首'''
        self.music_mode = False

        '''播放列表'''
        self.paly_list = []

        '''当前播放索引'''
        self.idx = 0

        '''当前播放歌名'''
        self.song = None

        '''是否播放完毕'''
        self.is_finished = False

        '''是否停止'''
        self.is_stop = False

        '''是否在播放'''
        self.is_play = False

        self.audio = audio

        self.tts = tts

        self.logger = logging.getLogger(__name__)


    def play(self, uri):
        '''
        播放
        :param uri:播放资源地址
        :return:
        '''
        pass

    def stop(self):
        '''
        停止
        :return:
        '''
        pass

    def pause(self):
        '''
        暂停
        :return:
        '''
        pass

    def resume(self):
        '''
        回复播放
        :return:
        '''
        pass

    def exit(self):
        '''
        结束播放，退出音乐播放模式
        :return:
        '''
        pass

    def previous(self):
        '''
        上一首
        :return:
        '''
        pass

    def run(self):
        '''
        主循环，自动播放模式
        :return:
        '''
        pass

    def next(self):
        '''
        下一首
        :return:
        '''
        pass
    def search(self,text):
        '''
        搜索列表
        :param text:
        :return:
        '''
        pass

    def randomize(self):
        '''
        随机播放
        :return:
        '''
        self.random = True

    def serialize(self):
        '''
        顺序播放
        :return:
        '''
        self.random = False

    def time2int(self, t):
        '''
        转换播放时长
        :param t:
        :return:int
        '''
        (h, m, s) = t.split(':')
        if '.' in s:
            s = s.split('.')
            s = int(s[0])+int(s[1])/1000
        return int(h) * 3600 + int(m) * 60 + int(s)

    def increase_volume(self):
        self.volume += .1
        if self.volume > 1:
            self.volume = 1

    def decrease_volume(self):
        self.volume -= .1
        if self.volume < 0:
            self.volume = 0


    def add_callback(self,callback):
        '''
        播放状态回调
        :param name: {eos, ...}
        :param callback: 回调函数
        :return:
        '''
        if not callable(callback):
            return
        callback()

    def file_extension(self,path):
        '''
        获取文件扩展名
        :param path:
        :return: string
        '''
        return os.path.splitext(path)[1]

    def play_audio(self,filename):
        '''
        播放本地媒体文件
        :param filename:
        :return:
        '''
        cmd = ''
        ext = self.file_extension(filename)
        if ext == 'mp3':
            cmd = ['play', str(filename)]
        elif ext == 'wma':
            cmd = ['aplay', str(filename)]
        try:
            subprocess.Popen(cmd)
            pass
        except Exception as e:
            print('play  error:%s,%s' %(cmd,e))
            pass
    '''
    文本转mp3播放出来,机器人的口
    '''
    def say(self,text, cache=False):
        try:
            # 停止录音
            self.audio.stop_passive = True
            cache_file_name = app.md5(text)
            cache_file_path = os.path.join(
                constants.TEMP_PATH,
                cache_file_name + ".mp3"
            )
            if cache and os.path.exists(cache_file_path):
                self.logger.info('播报缓存文件：%s' % cache_file_path)
                self.play_audio(cache_file_path)
            else:
                tmp = self.tts.get_speech(text)
                if tmp is not None:
                    self.play_audio(tmp)
                    if cache:
                        self.logger.info('移动缓存语音文件：%s' % cache_file_path)
                        os.rename(tmp, cache_file_path)
                    else:
                        os.remove(tmp)
            self.audio.stop_passive = False
        except Exception as e:
            logging.error('播放语音失败：%s'%e)
            self.audio.stop_passive = False
            pass




