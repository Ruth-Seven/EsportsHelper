import time
from traceback import format_exc

from selenium.common import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.keys import Keys

from EsportsHelper.util import DebugScreen, TimeOutRetries, TimeOutRetriesRetunrBool


class Youtube:
    def __init__(self, driver, log) -> None:
        self.driver = driver
        self.log = log

    @TimeOutRetriesRetunrBool(3, "检查Youtube载入")
    def checkYoutube(self) -> bool:
        WebDriverWait(self.driver, 30).until(ec.presence_of_element_located((
            By.CSS_SELECTOR, "iframe[id=video-player-youtube]")))
        self.log.debug("确定是Youtube播放器")
        return True

    def setYoutubeQuality(self) -> bool:

        def handle(): 
            DebugScreen(self.driver, "setYoutubeQuality"),
            self.driver.switch_to.default_content()
        
        @TimeOutRetriesRetunrBool(3, "°D° Youtube 清晰度设置", "可能网络超时",
                                  errorHandle=handle, returnHandle=handle)
        def inner():
            if not self.checkYoutube():
                self.log.error("该页面没有Youtube播放器")
                return False
            
            self.driver.switch_to.frame("video-player-youtube")
            self.log.debug("进入Youtube player")

            # 开始播放
            play_button = WebDriverWait(self.driver, 30).until(
                ec.element_to_be_clickable((By.CSS_SELECTOR, "button.ytp-play-button.ytp-button")))
            # if play_button.get_attribute("data-title-no-tooltip") == "Play": 
            play_button.click()
            self.log.debug("启动播放")

            # setting_button
            self.driver.find_element(
                By.CSS_SELECTOR, "button.ytp-settings-button").click()
            self.log.debug("按下设置")
            # quality div
            time.sleep(1)  # wait for animation
            WebDriverWait(self.driver, 5).until(ec.element_to_be_clickable(
                (By.XPATH, "//div[contains(text(),'Quality')]"))).click()
            self.log.debug("成功设置quality")
            # 140p div
            time.sleep(1)
            WebDriverWait(self.driver, 5).until(ec.element_to_be_clickable(
                (By.XPATH, "//span[contains(string(),'144p')]"))).click()
            self.log.debug("成功设置144p")
            self.driver.switch_to.default_content()
            self.log.info(">_< Youtube 144p清晰度设置成功")
            return True
        return inner()
