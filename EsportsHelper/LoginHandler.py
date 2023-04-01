import time
from traceback import format_exc
from selenium.common import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec
from rich import print

from EsportsHelper.util import TimeOutRetries


class LoginHandler:
    def __init__(self, log, driver) -> None:
        self.log = log
        self.driver = driver

    @TimeOutRetries(5, "登陆操作", "请检查网络和账号并重试")
    def automaticLogIn(self, username, password):
        loginButton = WebDriverWait(self.driver, 10).until(
            ec.presence_of_element_located((By.CSS_SELECTOR, "a[data-riotbar-link-id=login]")))
        self.driver.execute_script("arguments[0].click();", loginButton)

        self.log.info("눈_눈 登录中...")
        WebDriverWait(self.driver, 20).until(
            ec.presence_of_element_located(
                (By.CSS_SELECTOR, "input[name=username]"))
        ).send_keys(username)
        self.driver.find_element(
            By.CSS_SELECTOR, "input[name=password]").send_keys(password)
        WebDriverWait(self.driver, 20).until(
            ec.element_to_be_clickable((By.CSS_SELECTOR, "button[type=submit]"))).click()

        WebDriverWait(self.driver, 15).until(ec.presence_of_element_located(
            (By.CSS_SELECTOR, "div.riotbar-summoner-name")))
        self.log.info("∩_∩ 登陆成功")
        return True
