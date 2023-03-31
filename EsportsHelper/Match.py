import time
from datetime import datetime, timedelta
from random import randint
from sys import exit
from time import sleep
from traceback import format_exc

import requests
from rich import print
from selenium.common import WebDriverException
from selenium.webdriver.common.by import By
from urllib3.exceptions import MaxRetryError

from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec

from EsportsHelper.Rewards import Rewards
from EsportsHelper.Twitch import Twitch
from EsportsHelper.util import DebugScreen, KnockNotify, Quit, TimeOutRetries
from EsportsHelper.Youtube import Youtube


class Match:
    def __init__(self, log, driver, config) -> None:
        self.log = log
        self.driver = driver
        self.config = config
        self.rewards = Rewards(log=log, driver=driver, config=config)
        self.twitch = Twitch(driver=driver, log=log)
        self.youtube = Youtube(driver=driver, log=log)
        self.currentWindows = {}
        self.mainWindow = self.driver.current_window_handle
        self.OVERRIDES = {}
        self.retryTimes = 3
        try:
            req = requests.session()
            headers = {'Content-Type': 'text/plain; charset=utf-8',
                       'Connection': 'close'}
            remoteOverrideFile = req.get(
                "https://raw.githubusercontent.com/Yudaotor/EsportsHelper/main/override.txt", headers=headers)
            if remoteOverrideFile.status_code == 200:
                override = remoteOverrideFile.text.split(",")
                first = True
                for o in override:
                    temp = o.split("|")
                    if len(temp) == 2:
                        if first:
                            first = False
                        else:
                            temp[0] = temp[0][1:]
                        self.OVERRIDES[temp[0]] = temp[1]
        except MaxRetryError:
            self.log.error("获取文件失败, 请稍等再试")
            input("按任意键退出")
        except Exception as ex:
            input("按任意键退出")

    def watchMatches(self, delay, max_run_hours):
        self.currentWindows = {}
        self.mainWindow = self.driver.current_window_handle
        max_run_second = max_run_hours * 3600
        start_time_point = time.time()

        self.acceptCookies()
        while max_run_hours < 0 or time.time() < start_time_point + max_run_second:
            try:
                self.log.info("●_● 开始检查直播...")
                self.driver.switch_to.window(self.mainWindow)
                
                isDrop, imgUrl, title = self.rewards.checkNewDrops()
                if isDrop:
                    for tit in title:
                        self.log.info(
                            f"ΩДΩ {self.config.username}发现新的掉落: {tit}")
                    if self.config.connectorDropsUrl != "":
                        self.rewards.notifyDrops(imgUrl=imgUrl, title=title)
                
                try:
                    self.driver.get("https://lolesports.com/schedule?leagues=lcs,north_american_challenger_league,lcs_challengers_qualifiers,college_championship,cblol-brazil,lck,lcl,lco,lec,ljl-japan,lla,lpl,pcs,turkiye-sampiyonluk-ligi,vcs,worlds,all-star,european-masters,lfl,nlc,elite_series,liga_portuguesa,pg_nationals,ultraliga,superliga,primeleague,hitpoint_masters,esports_balkan_league,greek_legends,arabian_league,lck_academy,ljl_academy,lck_challengers_league,cblol_academy,liga_master_flo,movistar_fiber_golden_league,elements_league,claro_gaming_stars_league,honor_division,volcano_discover_league,honor_league,msi,tft_esports")
                except Exception as e:
                    self.driver.get("https://lolesports.com/schedule")
                liveMatches = self.getMatchInfo()
                if len(liveMatches) == 0:
                    self.log.info("〒.〒 没有赛区正在直播")
                else:
                    self.log.info(f"ㅎ.ㅎ 现在有 {len(liveMatches)} 个赛区正在直播中")

                self.closeFinishedTabs(liveMatches=liveMatches)
                self.startWatchNewMatches(
                    liveMatches=liveMatches, disWatchMatches=self.config.disWatchMatches)

                randomDelay = randint(int(delay * 0.08), int(delay * 0.15))
                newDelay = randomDelay * 10
                self.driver.switch_to.window(self.mainWindow)
                self.log.info(
                    f"下一次检查在: {datetime.now() + timedelta(seconds=newDelay)}")
                sleep(newDelay)
                self.retryTimes = 3
            except WebDriverException as e:
                self.retryTimes -= 1
                self.log.error(f"Q_Q webdriver发生错误, 重试中. {e}")
                if self.retryTimes <= 0:
                    self.log.error(f"Q_Q webdriver发生错误, 将于3秒后退出... {e}")
                    Quit(self.driver)

            except Exception as e:
                self.retryTimes -= 1
                self.log.error(f"Q_Q 发生错误 {e}")
                if self.retryTimes <= 0:
                    self.log.error(f"Q_Q 发生错误, 将于3秒后退出... {e}")
                    Quit(self.driver)

    def getMatchInfo(self):
        try:
            matches = []
            wait = WebDriverWait(self.driver, 5)
            elements = wait.until(ec.presence_of_all_elements_located(
                (By.CSS_SELECTOR, ".EventMatch .live.event")))
            for element in elements:
                matches.append(element.get_attribute("href"))
            return matches
        except Exception as e:
            self.log.error(f"Q_Q 获取比赛列表失败. {e}")
            return []

    def closeFinishedTabs(self, liveMatches):
        try:
            removeList = []
            for k in self.currentWindows.keys():
                self.driver.switch_to.window(self.currentWindows[k])
                if k not in liveMatches:
                    splitUrl = k.split('/')
                    if splitUrl[-2] != "live":
                        match = splitUrl[-2]
                    else:
                        match = splitUrl[-1]
                    self.log.info(f"0.0 {match} 比赛结束. {e}")
                    self.driver.close()
                    removeList.append(k)
                    self.driver.switch_to.window(self.mainWindow)
                else:
                    self.rewards.checkRewards(k)
            for k in removeList:
                self.currentWindows.pop(k, None)
            self.driver.switch_to.window(self.mainWindow)
        except Exception as e:
            self.log.error(f"关闭窗口出错: {e}")

    @TimeOutRetries(3)
    def acceptCookies(self):
        button = self.driver.find_element(By.CSS_SELECTOR, "button.osano-cm-accept-all")
        button.click()
        self.log.info("接受cookies")
        
    def startWatchNewMatches(self, liveMatches, disWatchMatches):
        newLiveMatches = set(liveMatches) - set(self.currentWindows.keys())
        for match in newLiveMatches:

            flag = True
            for disMatch in disWatchMatches:
                if match.find(disMatch) != -1:
                    splitUrl = match.split('/')
                    if splitUrl[-2] != "live":
                        skipName = splitUrl[-2]
                    else:
                        skipName = splitUrl[-1]
                    self.log.info(f"(╯#-_-)╯ {skipName}比赛跳过.")
                    flag = False
                    break
            if not flag:
                continue
            self.driver.switch_to.new_window('tab')
            self.currentWindows[match] = self.driver.current_window_handle
            self.log.info(f"●_●正在载入直播")


            url = match
            self.driver.get(url)
            if self.twitch.checkTwitch():
                self.twitch.setTwitchQuality()
                self.rewards.checkRewards(url)
            elif self.Youtube.checkYoutube():
                self.youtube.setYoutubeQuality()
                self.rewards.checkRewards(url)
            else:
                self.log.error(f"不支持的视频流, 请联系owner with: {url}")

