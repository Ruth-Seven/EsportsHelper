

from rich import print
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.ui import WebDriverWait

from EsportsHelper.util import DebugScreen

class Twitch:
    def __init__(self, driver, log) -> None:
        self.driver = driver
        self.log = log

    def checkTwitch(self) -> bool:
        try:
            self.driver.find_element(By.CSS_SELECTOR, "iframe[title=Twitch]")
            return True
        except:
            return False

    def setTwitchQuality(self) -> bool:
        try:
            wait = WebDriverWait(self.driver, 30)
            wait.until(ec.frame_to_be_available_and_switch_to_it((By.CSS_SELECTOR, "iframe[title=Twitch]")))
            muteButton = wait.until(ec.presence_of_element_located((By.CSS_SELECTOR, "button[data-a-target=player-mute-unmute-button]")))
            try:
                muteButton.click()
            except Exception:
                self.driver.execute_script("arguments[0].click();", muteButton)
            settingsButton = wait.until(ec.presence_of_element_located((By.CSS_SELECTOR, "button[data-a-target=player-settings-button]")))
            self.driver.execute_script("arguments[0].click();", settingsButton)
            qualityButton = wait.until(ec.presence_of_element_located((By.CSS_SELECTOR, "button[data-a-target=player-settings-menu-item-quality]")))
            self.driver.execute_script("arguments[0].click();", qualityButton)
            options = wait.until(ec.presence_of_all_elements_located((By.CSS_SELECTOR, "input[data-a-target=tw-radio]")))
            self.driver.execute_script("arguments[0].click();", options[-1])
            self.driver.switch_to.default_content()
            self.log.info(">_< Twitch 160p清晰度设置成功")
            return True
        except Exception as e:
            DebugScreen(self.driver, "setTwitchQuality")    
            self.log.error(f"°D° Twitch 清晰度设置失败: {e}")               
            return False
