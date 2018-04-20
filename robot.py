from core.brain import Brain
from core import constants
from core.audio import Audio
import os
import logging
import yaml
import time
import signal
interrupted = False


def signal_handler(signal, frame):
    global interrupted
    interrupted = True


def interrupt_callback():
    global interrupted
    return interrupted

# capture SIGINT signal, e.g., Ctrl+C
signal.signal(signal.SIGINT, signal_handler)


def main():
    logger = logging.getLogger(__name__)
    config = None
    if not os.access(constants.APP_CONFIG_FILE, os.W_OK):
        logger.error("无法读取配置文件: '%s'", constants.APP_CONFIG_FILE, exc_info=True)
        raise Exception(["无法读取配置文件: '%s'", constants.APP_CONFIG_FILE])
    '''读取配置文件'''
    try:
        with open(constants.APP_CONFIG_FILE, 'r', encoding="utf-8") as c:
            config = yaml.safe_load(c)
    except Exception as e:
        logger.error("Can't open config file: %s", constants.APP_CONFIG_FILE)
        raise e


    # 创建录音设备(平台相关)
    audio = Audio()
    # 创建唤醒引擎
    wakeup_engine = Brain(config,audio,interrupt_check=interrupt_callback)
    wakeup_engine.start()

    while True:
        try:
            time.sleep(1)
        except KeyboardInterrupt:
            break

    wakeup_engine.stop()
    audio.close()


if __name__ == '__main__':
    main()