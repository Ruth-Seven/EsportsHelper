
import time
from traceback import format_exc
from rich import print
from selenium.webdriver.common.by import By
from selenium.common import NoSuchElementException
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.ui import WebDriverWait

from EsportsHelper.util import DebugScreen, TimeOutRetriesRetunrBool


class Twitch:
    def __init__(self, driver, log) -> None:
        self.driver = driver
        self.log = log

    @TimeOutRetriesRetunrBool(3, "检查Twitch载入")
    def checkTwitch(self) -> bool:
        WebDriverWait(self.driver, 15).until(ec.presence_of_element_located(
            (By.CSS_SELECTOR, "iframe[title=Twitch]")))
        self.log.debug("确定是Twitch播放器")
        return True

    def checkTwitchHealth(self) -> bool: 
        try:
            self.driver.find_element(By.CLASS_NAME, "div[data-a-target=tw-core-button-label-text]")[2].click()
            self.log.info("重新载入Twitch Stream 因为网络带宽问题")
            return True
        except (TimeoutError, NoSuchElementException):
            return True
        except Exception as e:
            self.log.error(f"点击重载button出错 {e}\n {format_exc()}")
        
    def setTwitchQuality(self) -> bool:
        def defer():
            DebugScreen(self.driver, "setTwitchQuality")
            self.driver.switch_to.default_content()

        @TimeOutRetriesRetunrBool(3, "°D° Twitch 清晰度设置失败", "请检查网络", errorHandle=defer)
        def inner():
            if not self.checkTwitch():
                self.log.error("该页面没有Twitch播放器")
                return False
            self.driver.switch_to.frame(self.driver.find_element(By.CSS_SELECTOR, "iframe[title=Twitch]"))
            self.log.debug("进入twitch")

            self.checkTwitchHealth()

            wait = WebDriverWait(self.driver, 30)
            wait.until(ec.presence_of_element_located(
                (By.CSS_SELECTOR, "button[data-a-target=player-settings-button]"))).click()
            time.sleep(1)  # wait for animation
            self.log.debug("成功按下setting")
            wait.until(ec.presence_of_element_located(
                (By.CSS_SELECTOR, "button[data-a-target=player-settings-menu-item-quality]"))).click()
            time.sleep(1)
            self.log.debug("成功设置quality")
            wait.until(ec.presence_of_all_elements_located(
                (By.CSS_SELECTOR, ("div[role=menuitemradio]"))))[-1].click()

            self.driver.switch_to.default_content()
            self.log.info(">_< Twitch 160p清晰度设置成功")
            return True

        return inner()
