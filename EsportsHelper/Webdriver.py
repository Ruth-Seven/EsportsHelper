import undetected_chromedriver as uc
from rich import print
from webdriver_manager.chrome import ChromeDriverManager
from EsportsHelper.Logger import log


class Webdriver:
    def __init__(self, config) -> None:
        self.config = config

    def createWebdriver(self, conf):
        options = self.addWebdriverOptions(uc.ChromeOptions(), conf)
        log.info("ㅍ_ㅍ 正在准备中...")
        if self.config.platForm == "linux":
            driver = uc.Chrome(options=options)
            driver.set_page_load_timeout(30)
            driver.implicitly_wait(3)
            return driver
        elif self.config.platForm == "windows":
            chromeDriverManager = ChromeDriverManager(path=".\\driver")
            version = int(chromeDriverManager.driver.get_version().split(".")[0])
            driverPath = chromeDriverManager.install()
            return uc.Chrome(options=options, driver_executable_path=driverPath, version_main=version)
        else:
            log.error("不支持的操作系统")


    def addWebdriverOptions(self, options, conf):
        options.page_load_strategy = 'normal'
        options.add_argument("--lang=en")
        options.add_argument("--accept-lang=en")
        options.add_argument("--disable-extensions")
        options.add_argument('--disable-audio-output')
        options.add_argument( f'--proxy-server={conf.proxy}' )
        if self.config.headless:
            options.add_argument("--headless=new")
        options.add_argument("--disable-gpu")
        
        prefs = {
            "profile.password_manager_enabled": False,
            "credentials_enable_service": False,
        }
        options.add_experimental_option('prefs', prefs)
        # options.add_argument('--no-sandbox')
        windows_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Safari/537.36 Edg/111.0.1661.44"
        mac_agent = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Safari/537.36"
        user_agent = windows_agent if "win" in self.config.platForm else mac_agent 
        options.add_argument(f'user-agent={user_agent}')
        return options
