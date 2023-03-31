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
    loginHandler = LoginHandler(log=log, driver=driver)
    try:
        driver.get(
            "https://lolesports.com/schedule?leagues=lcs,north_american_challenger_league,lcs_challengers_qualifiers,college_championship,cblol-brazil,lck,lcl,lco,lec,ljl-japan,lla,lpl,pcs,turkiye-sampiyonluk-ligi,vcs,worlds,all-star,european-masters,lfl,nlc,elite_series,liga_portuguesa,pg_nationals,ultraliga,superliga,primeleague,hitpoint_masters,esports_balkan_league,greek_legends,arabian_league,lck_academy,ljl_academy,lck_challengers_league,cblol_academy,liga_master_flo,movistar_fiber_golden_league,elements_league,claro_gaming_stars_league,honor_division,volcano_discover_league,honor_league,msi,tft_esports")
    except Exception as e:
        driver.get("https://lolesports.com/schedule")
    # driver.set_window_size(960, 768)
  
    if not loginHandler.automaticLogIn(config.username, config.password):
        Quit(driver, "登陆失败")
    log.info("∩_∩ 好嘞 登录成功")

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
    
