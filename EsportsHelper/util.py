import subprocess
import time
import traceback
import functools

from selenium.common.exceptions import TimeoutException


# from EsportsHelper.Config import 
from EsportsHelper import Config
from EsportsHelper.Logger import log
from EsportsHelper.VersionManager import VersionManager


def info():
    log.info("=========================================================")
    log.info(
        f"========        感谢使用 [blue]电竞助手[/blue] v{VersionManager.getVersion()}!        ========")
    log.info("============ 本程序开源于github链接地址如下: ============")
    log.info("====   https://github.com/Yudaotor/EsportsHelper     ====")
    log.info("==== 如觉得不错的话可以进上面链接请我喝杯咖啡支持下. ====")
    log.info("==== 请在使用前阅读教程文件, 以确保你的配置符合要求! ====")
    log.info("==== 如需关闭请勿直接右上角×关闭，请按Ctrl+C来关闭. ====")
    log.info("=========================================================")
    VersionManager.checkVersion()


def KnockNotify(msg):
    subprocess.run(f"source ~/.personalrc; knock {msg}", shell=True)


def Quit(driver=None, e=None):
    if e:
        KnockNotify(f"🥵停止挂机: '{e}'")
        log.error(e)
    log.info("------程序退出------")

    log.error(traceback.print_exc())
    try:
        driver.quit()
    except NameError:
        log.info("driver was not defined")


def DebugScreen(driver, lint=""):
    if Config.config.debug:
        png = f"./logs/pics/{time.strftime('%b-%d-%H-%M-%S')}-{lint}.png"
        log.info(f"DebugScreen: {png}")
        driver.save_screenshot(png)


def TimeOutRetries(times=3, msg="Error", hint=""):
    def inner(func):
        @functools.wraps(func)
        def Warp(*args, **vargs):
            retries = times
            while retries >= 0:
                retries = retries - 1
                try:
                    return func(*args, **vargs)
                except TimeoutException as e:
                    retries = retries - 1
                    if retries <= 0:
                        log.error(msg + " 超时重试多次 " + hint)
                except Exception as e:
                    log.error(msg + f"失败: {e}")
                    return
        return Warp
    return inner


def FalseRetries(times=3, msg=""):
    def inner(func):
        @functools.wraps(func)
        def Wrap(*args, **vargs):
            retries = times
            while retries >= 0:
                retries = retries - 1
                if func(*args, **vargs):
                    return True
                else:
                    log.warn(msg + ", 重试中")
            return False
        return Wrap
    return inner
