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
    try:
        if Config.config.systemNotify:
            subprocess.run(f"source ~/.personalrc; knock {msg}", shell=True)
    except:
        pass

def Quit(driver=None, e=None):
    if e:
        KnockNotify(f"🥵停止挂机: '{e}'")
        log.error(e)
    log.error(f"trace : \n{traceback.print_exc()}")
    log.info("------程序退出------")

    try:
        log.info("------关闭Chrome Driver------")
        driver.quit()
    except: 
        pass
    quit()


def DebugScreen(driver, lint=""):
    if Config.config.debug:
        png = f"./logs/pics/{time.strftime('%b-%d-%H-%M-%S')}-{lint}.png"
        log.debug(f"DebugScreen: {png}")
        driver.save_screenshot(png)


def TimeOutRetries(times=3, msg="操作", hint="请检查", handle=lambda : None):
    def inner(func):
        @functools.wraps(func)
        def Warp(*args, **vargs):
            retries = times
            while retries > 0:
                retries = retries - 1
                try:
                    return func(*args, **vargs)
                except TimeoutException as e:
                    retries = retries - 1
                    handle()
                    if retries <= 0:
                        log.error(msg + " 超时重试多次 " + hint)
                except Exception as e:
                    handle()
                    log.error(msg + f"失败: {e}")
                    raise e

        return Warp
    return inner

def TimeOutRetriesRetunrBool(times=3, msg="操作", hint="请检查", handle=lambda : None):
    def inner(func):
        @functools.wraps(func)
        def Warp(*args, **vargs):
            retries = times
            while retries > 0:
                retries = retries - 1
                try:
                    return func(*args, **vargs)
                except TimeoutException as e:
                    retries = retries - 1
                    handle()
                    if retries <= 0:
                        log.error(msg + " 超时重试多次 " + hint)
                    return False
                except Exception as e:
                    handle()
                    log.error(msg + f"失败: {e}")
                    return False
            return False
        return Warp
    return inner



def FalseRetries(times=3, msg="", hint="请检查"):
    def inner(func):
        @functools.wraps(func)
        def Wrap(*args, **vargs):
            retries = times
            while retries > 0:
                retries = retries - 1
                if func(*args, **vargs):
                    return True
                else:
                    log.warn(msg + "失败 重试中 " + hint)
            log.error(msg + ", 重试失败 " + hint)
            return False
        return Wrap
    return inner
