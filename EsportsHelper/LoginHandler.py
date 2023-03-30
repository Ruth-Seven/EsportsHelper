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
        try:
            self.driver.get(
                "https://lolesports.com/schedule?leagues=lcs,north_american_challenger_league,lcs_challengers_qualifiers,college_championship,cblol-brazil,lck,lcl,lco,lec,ljl-japan,lla,lpl,pcs,turkiye-sampiyonluk-ligi,vcs,worlds,all-star,european-masters,lfl,nlc,elite_series,liga_portuguesa,pg_nationals,ultraliga,superliga,primeleague,hitpoint_masters,esports_balkan_league,greek_legends,arabian_league,lck_academy,ljl_academy,lck_challengers_league,cblol_academy,liga_master_flo,movistar_fiber_golden_league,elements_league,claro_gaming_stars_league,honor_division,volcano_discover_league,honor_league,msi,tft_esports")
        except Exception as e:
            self.driver.get("https://lolesports.com/schedule")

        loginButton = WebDriverWait(self.driver, 30).until(
            ec.presence_of_element_located((By.CSS_SELECTOR, "a[data-riotbar-link-id=login]")))
        self.driver.execute_script("arguments[0].click();", loginButton)
        
        self.log.info("눈_눈 登录中...")
        usernameInput = self.driver.find_element(By.CSS_SELECTOR, "input[name=username]")
        usernameInput.send_keys(username)
        passwordInput = self.driver.find_element(By.CSS_SELECTOR, "input[name=password]")
        passwordInput.send_keys(password)
        submitButton = self.driver.find_element(By.CSS_SELECTOR, "button[type=submit]")
        self.driver.execute_script("arguments[0].click();", submitButton)
        try:
            WebDriverWait(self.driver, 15).until(ec.presence_of_element_located((By.CSS_SELECTOR, "div.riotbar-summoner-name")))
            self.log.info("∩_∩ 账密 提交成功")
            return True
        except TimeoutException:
            return False
        