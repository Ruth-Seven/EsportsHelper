import time
import traceback

import requests
from rich import print
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.ui import WebDriverWait

from EsportsHelper.util import DebugScreen, KnockNotify, FalseRetries, TimeOutRetriesRetunrBool


class Rewards:
    def __init__(self, log, driver, config) -> None:
        self.log = log
        self.driver = driver
        self.config = config

    def _isRewardMarkExist(self):
        @FalseRetries(3, "检查可获取奖励状态")
        def inner():
            time.sleep(10) # wait for stream cache
            box = WebDriverWait(self.driver, 60).until(ec.presence_of_element_located(
                (By.CSS_SELECTOR, "div.status-items div.message")))
            if not "enjoy the show!" in box.get_attribute("innerHTML"):
                self.log.debug(
                    f"Reward info: {box.get_attribute('innerHTML')}")
                DebugScreen(self.driver, "isRewardMarkExist")
                return False
            return True
        return inner()

    def checkRewardable(self, url) -> bool:
        splitUrl = url.split('/')
        match = ""
        if splitUrl[-2] != "live":
            match = splitUrl[-2]
        else:
            match = splitUrl[-1]

        if self._isRewardMarkExist():
            self.log.critical(f"√√√√√ {match} 正常观看 可获取奖励 √√√√√ ")
            return True
        else:
            DebugScreen(self.driver, "checkRewardsfail")
            self.log.error(f"xxxxxx{match} 不能获取奖励 xxxxx")
            return False

    def checkNewDrops(self):
        try:
            isDrop = False
            imgUrl = []
            title = []
            imgEl = self.driver.find_elements(
                by=By.CSS_SELECTOR, value="img[class=img]")
            if len(imgEl) > 0:
                for img in imgEl:
                    imgUrl.append(img.get_attribute("src"))
                isDrop = True
            titleEl = self.driver.find_elements(
                by=By.CSS_SELECTOR, value="div[class=title]")
            if len(titleEl) > 0:
                for tit in titleEl:
                    title.append(tit.text)
                isDrop = True
            self.driver.implicitly_wait(15)
            if isDrop:
                DebugScreen(self.driver, "checkNewDrops-Yes")
                return isDrop, imgUrl, title
            else:
                return isDrop, [], []
        except Exception:
            self.log.error("〒.〒 检查掉落失败")
            return False, [], []

    def SystemNotify(self,  imgUrl, title):
        if self.config.systemNotify:
            for index, item in enumerate(zip(imgUrl, title)):
                drop_msg = "有新的掉落啦，\n{item[0]}\n{item[1]}\n可检查: https://lolesports.com/rewards"
                KnockNotify(drop_msg)

    def notifyDrops(self, imgUrl, title):
        self.SystemNotify(imgUrl, title)
        try:
            for i in range(len(imgUrl)):
                if "https://oapi.dingtalk.com" in self.config.connectorDropsUrl:
                    data = {
                        "msgtype": "link",
                        "link": {
                            "text": "Drop掉落提醒",
                            "title": f"[{self.config.username}]{title[i]}",
                            "picUrl": f"{imgUrl[i]}",
                            "messageUrl": "https://lolesports.com/rewards"
                        }
                    }
                    requests.post(self.config.connectorDropsUrl, json=data)
                elif "https://discord.com/api/webhooks" in self.config.connectorDropsUrl:
                    embed = {
                        "title": "掉落提醒",
                        "description": f"[{self.config.username}]{title[i]}",
                        "image": {"url": f"{imgUrl[i]}"},
                        "thumbnail": {"url": "https://www.cdnjson.com/images/2023/03/26/QQ20230326153220.jpg"},
                        "color": 6676471,
                    }
                    params = {
                        "username": "EsportsHelper",
                        "embeds": [embed]
                    }
                    requests.post(self.config.connectorDropsUrl, headers={
                                  "Content-type": "application/json"}, json=params)
                elif "https://fwalert.com" in self.config.connectorDropsUrl:
                    params = {
                        "text": f"[{self.config.username}]{title[i]}"
                    }
                    requests.post(self.config.connectorDropsUrl, headers={
                                  "Content-type": "application/json"}, json=params)
        except Exception:
            self.log.error("〒.〒 掉落提醒失败")
