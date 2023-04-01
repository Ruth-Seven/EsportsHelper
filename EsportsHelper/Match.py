import time
from datetime import datetime, timedelta
from random import randint
from sys import exit
from time import sleep
from traceback import format_exc

import requests
from lxml.html import fromstring
from rich import print
from selenium.common import WebDriverException, InvalidSwitchToTargetException, TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.ui import WebDriverWait


from EsportsHelper.Rewards import Rewards
from EsportsHelper.Twitch import Twitch
from EsportsHelper.util import FalseRetries, Quit, TimeOutRetriesRetunrBool, matchUrl2Match
from EsportsHelper.Youtube import Youtube


class Match:
    def __init__(self, log, driver, config) -> None:
        self.log = log
        self.driver = driver
        self.config = config
        self.rewards = Rewards(log=log, driver=driver, config=config)
        self.twitch = Twitch(driver=driver, log=log)
        self.youtube = Youtube(driver=driver, log=log)
        self.liveWindows = {}
        self.mainWindow = self.driver.current_window_handle

    def watchMatches(self, delay, max_run_hours):
        self.liveWindows = {}
        self.retryTimes = 3
        self.mainWindow = self.driver.current_window_handle
        max_run_second = max_run_hours * 3600
        start_time_point = time.time()

        self.acceptCookies()
        while max_run_hours < 0 or time.time() < start_time_point + max_run_second:
            try:
                self.log.info("●_● 开始检查直播...")
                self.driver.switch_to.window(self.mainWindow)

                try:
                    self.driver.get("https://lolesports.com/schedule?leagues=lcs,north_american_challenger_league,lcs_challengers_qualifiers,college_championship,cblol-brazil,lck,lcl,lco,lec,ljl-japan,lla,lpl,pcs,turkiye-sampiyonluk-ligi,vcs,worlds,all-star,european-masters,lfl,nlc,elite_series,liga_portuguesa,pg_nationals,ultraliga,superliga,primeleague,hitpoint_masters,esports_balkan_league,greek_legends,arabian_league,lck_academy,ljl_academy,lck_challengers_league,cblol_academy,liga_master_flo,movistar_fiber_golden_league,elements_league,claro_gaming_stars_league,honor_division,volcano_discover_league,honor_league,msi,tft_esports")
                except Exception as e:
                    self.driver.get("https://lolesports.com/schedule")

                liveMatches = self.getMatchInfo()
                self.showNextGame()
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

                isDrop, imgUrl, title = self.rewards.checkNewDrops()
                if isDrop:
                    for tit in title:
                        self.log.info(
                            f"ΩДΩ {self.config.username}发现新的掉落: {tit}")
                    if self.config.connectorDropsUrl != "":
                        self.rewards.notifyDrops(imgUrl=imgUrl, title=title)

                self.log.info(
                    f"下一次检查在: {datetime.now() + timedelta(seconds=newDelay)}")
                sleep(newDelay)
                self.retryTimes = 3
            except InvalidSwitchToTargetException or WebDriverException as e:
                self.log.error(f"Q_Q 请勿关闭页面 {e}")
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
            wait = WebDriverWait(self.driver, 10)
            try:
                wait.until(ec.presence_of_element_located(
                    (By.CSS_SELECTOR, ".EventDate")))
                self.log.info("连接时间线成功")
            except TimeoutException:
                self.log.error("网络不稳定，请检查网络")
                return []
            elements = wait.until(ec.presence_of_all_elements_located(
                (By.CSS_SELECTOR, ".EventMatch .live.event")))
            for element in elements:
                matches.append(element.get_attribute("href"))
            return matches
        except Exception as e:
            self.log.info(f"Q_Q 无直播比赛: {e}")
            return []

    def showNextGame(self):
        try:
            elm = self.driver.find_element(
                By.CSS_SELECTOR, "div.divider.future~div.EventDate~div.EventMatch")
            tree = fromstring(elm.get_attribute("innerHTML"))
            hour = tree.cssselect(".hour")[0].text_content()
            ampm = tree.cssselect(".ampm")[0].text_content()
            team1 = tree.cssselect(
                "div.team.team1 span.name")[0].text_content()
            team2 = tree.cssselect(
                "div.team.team2 span.name")[0].text_content()
            league = tree.cssselect("div.league > div.name")[0].text_content()
            self.log.info(
                f"下一场比赛:  {team1} vs {team2}  在 {league} 赛区 {hour}{ampm} 举行")
        except Exception as e:
            self.log.error(f"获取下一场比赛信息失败 {e}")
            self.log.error(format_exc())

    def closeFinishedTabs(self, liveMatches):
        try:
            removeList = []
            for url in self.liveWindows.keys():
                self.driver.switch_to.window(self.liveWindows[url])
                if url not in liveMatches:
                    self.log.info(f"0.0 {matchUrl2Match(url)} 比赛结束.")
                    self.driver.close()
                    removeList.append(url)
                    self.driver.switch_to.window(self.mainWindow)
                else:
                    if not self.rewards.checkRewardable(url):
                        self.resetLivePage()
            for url in removeList:
                self.liveWindows.pop(url, None)
            self.driver.switch_to.window(self.mainWindow)
        except Exception as e:
            self.log.error(f"关闭窗口出错: {e} \n {format_exc()}")


    def startWatchNewMatches(self, liveMatches, disWatchMatches):
        newLiveMatches = set(liveMatches) - set(self.liveWindows.keys())
        for index, matchUrl in enumerate(newLiveMatches):
            
            def skipMatches():
                for disMatch in disWatchMatches:
                    if disMatch in matchUrl:
                        self.log.info(
                            f"(╯#-_-)╯ {disMatch}比赛跳过. ({index + 1} / {len(newLiveMatches)})")
                        return True
                return False
            if skipMatches():
                continue
            
            self.driver.switch_to.new_window('tab')
            self.liveWindows[matchUrl] = self.driver.current_window_handle
            self.log.info(f"●_●正在打开直播 ({index + 1} / {len(newLiveMatches)})")

            self.driver.get(matchUrl)
            self.initLiveStatus()

    def SwitchStream(self, url) -> bool:
        def clickOptionButton(time=25):
            try:
                sleep(time)  # wait for switching stream
                WebDriverWait(self.driver, time).until(ec.element_to_be_clickable(
                    (By.CSS_SELECTOR, "div.options-button"))).click()
            except Exception as e:
                self.log.error(f"点击stream bution 错误: {e} \n{format_exc()}")
        
        def closeOptionButton():
            try:
                self.driver.find_element(
                    By.CSS_SELECTOR, "div.overview-pane").click()
            except Exception as e:
                self.log.error(f"取消窗口出错: {e}")

        @TimeOutRetriesRetunrBool(3, "切换播放源到Twitch", f"联系ower with {url}",
                                  errorHandle=clickOptionButton, returnHandle=closeOptionButton)
        def inner():
            clickOptionButton(20)
            time.sleep(1)  # wait for animation
            WebDriverWait(self.driver, 10).until(ec.presence_of_all_elements_located(
                (By.CSS_SELECTOR, "div.options-section.stream-section  div.options-list div.option")))[0].click()
            time.sleep(1)
            try:
                WebDriverWait(self.driver, 10).until(ec.presence_of_element_located(
                    (By.CSS_SELECTOR, ("div.options-section.provider-selection ul.providers.options-list  li.option.twitch")))).click()
                self.log.info("成功切换到Twitch源")
                return True
            except:
                self.log.info(f"该比赛没有twitch源，尝试切换Youtube源")
                try:
                    WebDriverWait(self.driver, 10).until(ec.presence_of_element_located(
                        (By.CSS_SELECTOR, ("div.options-section.provider-selection ul.providers.options-list  li.option.youtube")))).click()
                    self.log.info("成功切换到Youtube源")
                except:
                    self.log.warn(f"没有Youtube源，放弃切换")
                    return False
            return False

        return inner()

    def initLiveStatus(self):
        url = self.driver.current_url
        self.SwitchStream(url)
        if self.twitch.checkTwitch():
            self.twitch.setTwitchQuality()
        elif self.youtube.checkYoutube():
            self.youtube.setYoutubeQuality()
        else:
            self.log.error(f"不支持的视频流, 请联系owner with: {url}")
        return self.rewards.checkRewardable(url)

    @FalseRetries(3, "刷新live并尝试保持获取状态")
    def resetLivePage(self):
        self.log.info("刷新live画面ing...")
        self.driver.refresh()
        return self.initLiveStatus()

    @FalseRetries(3, "cookies接受失败")
    def acceptCookies(self):
        try:
            WebDriverWait(self.driver, 15).until(ec.element_to_be_clickable(
                (By.CSS_SELECTOR, "button.osano-cm-accept-all"))).click()
            self.log.info("接受cookies")
            return True
        except TimeoutException:
            self.log.info("没有cookies")
            return True
        except Exception as e:
            self.log.error(f"接受cookies时发生错误: {e}")
            return False
