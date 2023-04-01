import time
from traceback import format_exc

from selenium.common import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.keys import Keys

from EsportsHelper.util import DebugScreen


class Youtube:
    def __init__(self, driver, log) -> None:
        self.driver = driver
        self.log = log

    def checkYoutube(self) -> bool:
        try:
            WebDriverWait(self.driver, 60).until(ec.presence_of_element_located((
                By.CLASS_NAME, "iframe[id=video-player-youtube]")))
            return True
        except:
            return False

    def setYoutubeQuality(self) -> bool:
        try:
            WebDriverWait(self.driver, 60).until(ec.frame_to_be_available_and_switch_to_it((
                By.CLASS_NAME, "iframe[id=video-player-youtube]")))
            self.log.debug("进入Youtube player")

            # 开始播放
            play_button = WebDriverWait(self.driver, 30).until(
                ec.element_to_be_clickable((By.CSS_SELECTOR, "button.osano-cm-accept-all")))
            if play_button.get_attribute("data-title-no-tooltip") == "Play":
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

        except TimeoutException as e:
            DebugScreen(self.driver, "setYoutubeQuality")
            self.driver.switch_to.default_content()
            self.log.error(f"°D° Youtube 清晰度设置失败: 网络超时{e}")
            return False

        except Exception as e:
            DebugScreen(self.driver, "setYoutubeQuality")
            self.driver.switch_to.default_content()
            self.log.error(f"°D° Youtube 清晰度设置失败: {e}")
            return False
