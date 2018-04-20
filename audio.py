# -*- coding: utf-8 -*-
import collections
import pyaudio
import audioop
import logging
import queue
from ctypes import *
from contextlib import contextmanager
import core.constants as app_config

logging.basicConfig(level=app_config.LOGGER_LEVEL)
logger = logging.getLogger(__file__)
def py_error_handler(filename, line, function, err, fmt):
    pass
ERROR_HANDLER_FUNC = CFUNCTYPE(None, c_char_p, c_int, c_char_p, c_int, c_char_p)

c_error_handler = ERROR_HANDLER_FUNC(py_error_handler)

@contextmanager
def no_alsa_error():
    try:
        asound = cdll.LoadLibrary('libasound.so')
        asound.snd_lib_error_set_handler(c_error_handler)
        yield
        asound.snd_lib_error_set_handler(None)
    except:
        yield
        pass

class RingBuffer(object):
    """Ring buffer to hold audio from PortAudio"""

    def __init__(self, size=4096):
        self._buf = collections.deque(maxlen=size)

    def extend(self, data):
        """Adds data to the end of buffer"""
        self._buf.extend(data)

    def get(self):
        """Retrieves data from the beginning of buffer and clears it"""
        tmp = bytes(bytearray(self._buf))
        self._buf.clear()
        return tmp

class Audio(object):
    '''
    录音类(基于pyaudio)
    '''

    def __init__(self, rate=16000, frames_size=None, channels=None, device_index=None):
        '''
        录音类初始化
        :param rate:采样率
        :param frames_size:数据帧大小
        :param channels:通道数
        :param device_index:录音设备id
        '''
        self.sample_rate = rate
        self.frames_size = frames_size if frames_size else 1024
        self.channels = channels if channels else 1
        self.stop_passive = False
        # 自由聊天模式
        self.chat_modal = False
        with no_alsa_error():
            self.pyaudio_instance = pyaudio.PyAudio()

        if device_index is None:
            if channels:
                for i in range(self.pyaudio_instance.get_device_count()):
                    dev = self.pyaudio_instance.get_device_info_by_index(i)
                    name = dev['name'].encode('utf-8')
                    logger.info('{}:{} with {} input channels'.format(i, name, dev['maxInputChannels']))
                    if dev['maxInputChannels'] == channels:
                        logger.info('Use {}'.format(name))
                        device_index = i
                        break
            else:
                device_index = self.pyaudio_instance.get_default_input_device_info()['index']

            if device_index is None:
                raise Exception('Can not find an input device with {} channel(s)'.format(channels))
        self.ring_buffer = RingBuffer(
            self.channels * int(self.sample_rate) * 5)

        def audio_callback(in_data, frame_count, time_info, status):
            self.ring_buffer.extend(in_data)
            play_data = chr(0) * len(in_data)
            return play_data, pyaudio.paContinue

        self.open(device_index)

    def open(self,device_index,start=False):
        '''
        重新打开
        :return:
        '''
        self.stream = self.pyaudio_instance.open(
            start=start,
            format=pyaudio.paInt16,
            input_device_index=device_index,
            channels=self.channels,
            rate=int(self.sample_rate),
            frames_per_buffer=self.frames_size,
            input=True
        )

    def get_rms(self, data):
        '''
        获取rms
        :param data:
        :return:
        '''
        rms = audioop.rms(data, 2)
        return rms

    def read_raw(self):
        data = None
        try:
            data = self.stream.read(self.frames_size, exception_on_overflow=False)
        except Exception as e:
            logger.info('read record data error:%s'%e)
            pass
        return data

    def get_raw(self):
        '''
        获取录音数据
        :return:
        '''
        return self.ring_buffer.get()

    def get_rms(self, data):
        rms = audioop.rms(data, 2)
        return rms

    def average_lastn(self, array, n):
        array_len = len(array)
        if n > array_len:
            n = array_len
        return sum(array[array_len - n:array_len]) / n

    def recording(self):
        # prepare recording stream
        frames = []
        scores = []
        averages = [0 for i in range(5)]
        threshold = 0
        is_active = False
        active_counts = 0

        while True:
            try:
                # 声音数据，分值读取
                data = self.read_raw()
                score = self.get_rms(data)
                # 记录
                if not is_active and len(frames) > 10:
                    frames.pop(0)
                    scores.pop(0)
                frames.append(data)
                scores.append(score)

                if is_active:  # 已经有语音输入，判断是否需要结束
                    active_counts += 1
                    average = self.average_lastn(scores, 10)
                    # print('a%d' % average)
                    if average < threshold * 0.8 or active_counts > 180:
                        print('END: %d' % average)
                        break

                if not is_active:  # 没有听到声音输入，判断是否有有效声音输入
                    average = self.average_lastn(scores, 10)
                    # print(average)
                    if average > averages[4] + 3 and averages[4] > 50:
                        active_counts = active_counts + 1
                    else:
                        active_counts = 0
                    averages.pop(0)
                    averages.append(average)
                    if active_counts > 5:  # 声音值一直在增大，持续5次以上，认为有效语音输入
                        is_active = True
                        threshold = average
                        print('TD: %d' % threshold)
                        active_counts = 0

            except Exception as e:
                logger.error(e)
                continue
        # save the audio data



    def start(self):
        '''
        开始录音
        :return:
        '''
        self.stream.start_stream()

    def stop(self):
        '''
        结束录音
        :return:
        '''
        self.stream.stop_stream()

    def close(self):
        '''
        关闭释放资源
        :return:
        '''
        try:
            self.stream.start_stream()
            self.stream.close()
            self.pyaudio_instance.terminate()
        except Exception as e:
            logger.debug('pyaudio close error:%s' % e)
            pass
