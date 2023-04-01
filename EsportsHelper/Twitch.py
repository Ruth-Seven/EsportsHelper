
import time
from rich import print
from selenium.webdriver.common.by import By
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
        return True

    def setTwitchQuality(self) -> bool:
        def defer():
            DebugScreen(self.driver, "setTwitchQuality")
            self.driver.switch_to.default_content()

        @TimeOutRetriesRetunrBool(3, "°D° Twitch 清晰度设置失败", "请检查网络", handle=defer)
        def inner():
            if not self.checkTwitch():
                return False
            self.driver.switch_to.frame(0)
            self.log.debug("进入twitch")
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
