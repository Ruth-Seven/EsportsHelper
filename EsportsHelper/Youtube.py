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

    def setYoutubeQuality(self) -> bool:
        try:
            play_button = self.driver.find_element(By.CSS_SELECTOR, "button.ytp-play-button.ytp-button")
            play_button.click()

            settingsButton = self.driver.find_element(By.CSS_SELECTOR, "button[data-tooltip-target-id=ytp-settings-button]")
            self.driver.execute_script("arguments[0].click();", settingsButton)
            qualityButton = self.driver.find_element(By.XPATH, "/html/body/div[1]/div/div[25]/div/div/div[2]/div[3]")
            self.driver.execute_script("arguments[0].click();", qualityButton)
            option = self.driver.find_element(By.XPATH, "/html/body/div[1]/div/div[25]/div/div[2]/div[6]/div")
            self.driver.execute_script("arguments[0].click();", option)
            self.driver.switch_to.default_content()
            self.log.info(">_< Youtube 144p清晰度设置成功")
            return True
        
        except TimeoutException as e:
            DebugScreen(self.driver, "setYoutubeQuality")    
            self.log.critical(f"°D° Youtube 清晰度设置失败: {e}")
            return False
        
        except Exception as e:
            DebugScreen(self.driver, "setYoutubeQuality")    
            self.log.critical(f"°D° Youtube 清晰度设置失败: {e}")
            return False
