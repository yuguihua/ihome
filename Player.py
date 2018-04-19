'''
播放基本类
'''

class Player(object):
    '''
    播放器实现类
    '''
    def __init__(self):
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
        self.music_mode = 1

        '''播放列表'''
        self.paly_list = []

        '''当前播放索引'''
        self.idx = 0

        '''当前播放歌名'''
        self.song = None

        '''是否播放完毕'''
        self.is_finished = False


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
        self.player.set_state(Gst.State.NULL)

    def pause(self):
        '''
        暂停
        :return:
        '''
        self.player.set_state(Gst.State.PAUSED)

    def resume(self):
        '''
        回复播放
        :return:
        '''
        self.player.set_state(Gst.State.PLAYING)

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

    def time2Int(self, t):
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

    @property
    def duration(self):
        '''
        播放时长
        :return:
        '''
        pass

    @property
    def position(self):
        '''
        播放位置
        :return:
        '''
        success, position = self.player.query_position(Gst.Format.TIME)
        if not success:
            position = 0

        return int(position / Gst.MSECOND)

    @property
    def state(self):
        '''
        播放状态	one of (“1:Playing” | “0:Paused” | “-1:Stopped”)
        :return:int
        '''
        return self.state
