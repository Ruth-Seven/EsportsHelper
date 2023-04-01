import argparse
from traceback import format_exc
from selenium.webdriver.common.by import By


from rich import print
from EsportsHelper.LoginHandler import LoginHandler
from EsportsHelper.Webdriver import Webdriver
from EsportsHelper.Logger import log
from EsportsHelper import Config
from EsportsHelper.Config import Configuration
from EsportsHelper.Match import Match
from EsportsHelper.util import KnockNotify, info, Quit


global driver


def Watch(config):
    global driver
    try:
        driver = Webdriver(config).createWebdriver(config) 
    except TypeError:
        log.error(format_exc())
        log.error("눈_눈 生成WEBDRIVER失败!\n无法找到最新版谷歌浏览器!如没有下载或不是最新版请检查好再次尝试\n以上都检查过的话如还不行检查节点或是尝试可以用管理员方式打开\n")
        Quit(driver, e)
    except Exception as e:
        log.error(format_exc())
        log.error("눈_눈 生成WEBDRIVER失败!\n是否有谷歌浏览器?\n是不是网络问题?请检查VPN节点是否可用\n")
        Quit(driver, e)
    
    if not LoginHandler(log=log, driver=driver).automaticLogIn(config.username, config.password):
        Quit(driver, "登陆失败")

    Match(log=log, driver=driver, config=config).watchMatches(
        delay=config.delay, max_run_hours=config.max_run_hours)


def main():
    global driver
    info()

    parser = argparse.ArgumentParser(
        prog='EsportsHelper.exe', description='EsportsHelper help you to watch matches')
    parser.add_argument('-c', '--config', dest="configPath", default="./config.yaml",
                        help='config file path')
    args = parser.parse_args()

    config = Config.config = Configuration(log, args.configPath)

    KnockNotify("🫡尝试挂机")
    log.info("如果由于暂时的网络连接缓慢，登陆、切换、载入可能错误，在多次检查重置状态中可以被修复")
    log.info("但是网络直接断开，没办法, 重启吧")
    log.info("不要挂在日本等节点，由于语言问题最好选择香港，台湾，美国等英语中文国家")
    
    Watch(config)
    log.info("观看结束～")
    KnockNotify("😎挂机结束")


if __name__ == '__main__':
    try:
        main()
    except (KeyboardInterrupt, InterruptedError):
        Quit(driver, "程序被打断")
    except SystemExit:
        pass
    except Exception as e:
        Quit(driver, e)
    
