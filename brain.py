import queue
import threading
import time
import logging
from core.player import Player
from core import tts


class Brain(object):
    '''
    唤醒引擎(平台无关)
    '''
    def __init__(self, config=None, audio=None, interrupt_check=lambda: False):
        self.done = False
        self.config = config
        self.audio = audio
        self.logger = logging.getLogger(__name__)
        # tts实体
        self.tts = tts.get_engine_by_slug(config['tts_engine'])(config)
        self.player = Player(self.audio,tts=self.tts)
        self.interrupt = interrupt_check

    def start(self):
        '''
        唤醒引擎启动
        :return:
        '''
        self.done = False
        thread = threading.Thread(target=self.__run)
        thread.daemon = True
        thread.start()

    def stop(self):
        '''
        唤醒引擎关闭
        :return:
        '''
        self.done = True

    def wakup(self,result=None):
        '''
        已经唤醒要处理事件
        :param result:
        :return:
        '''
        print('我已唤醒...')

        input = self.audio.recording()
        print(input)
        pass

    def __run(self):
        self.logger.info('请说[小白小白]来唤醒我.......')
        self.audio.start()
        frames = []
        scores = []
        averages = [0 for i in range(5)]
        threshold = 0
        is_active = False
        active_counts = 0
        sleep_time = .01
        '''
        唤醒引擎线程实体
        :return:
        '''
        while not self.done:
            if self.interrupt():
                self.logger.debug("detect voice return")
                return
            # 是否停止本地录音
            if self.audio.stop_passive:
                self.logger.info('跳过停止录音')
                time.sleep(sleep_time)
                continue
            data = self.audio.read_raw()
            if not data:
                continue
            if len(data) == 0:
                time.sleep(sleep_time)
                continue
            rms = self.audio.get_rms(data)
            if rms <= 200:
                time.sleep(sleep_time)
                # self.logger.info('没有监听到声音')
                continue
            '''# 记录
            if not is_active and len(frames) > 10:
                frames.pop(0)
                scores.pop(0)
            frames.append(data)
            scores.append(rms)
            if is_active:  # 已经有语音输入，判断是否需要结束
                active_counts += 1
                average = self.averageLast_n(scores, 10)
                # print('a%d' % average)
                if average < threshold * 0.8 or active_counts > 180:
                    print('END: %d' % average)
                    is_active = False
                    active_counts = 0
                    scores = []
                    frames = []
                    self.wakup('a')
                    continue

            if not is_active:  # 没有听到声音输入，判断是否有有效声音输入
                average = self.averageLast_n(scores, 10)
                # print(average)
                if average > averages[4] + 3 and averages[4] > 50:
                    active_counts +=  1
                else:
                    active_counts = 0
                averages.pop(0)
                averages.append(average)
                if active_counts > 5:  # 声音值一直在增大，持续5次以上，认为有效语音输入
                    is_active = True
                    threshold = average
                    print('TD: %d' % threshold)
                    active_counts = 0'''
            print(rms)
            #time.sleep(sleep_time)


