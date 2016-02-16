from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.common.exceptions import TimeoutException, WebDriverException


class ExistingSeleniumSession(WebDriver):

  def __init__(self, command_executor='http://127.0.0.1:4444/wd/hub',
          desired_capabilities={}, browser_profile=None, proxy=None, keep_alive=False, session_id=None):
    super(ExistingSeleniumSession, self).__init__(command_executor, desired_capabilities, browser_profile, proxy, keep_alive)
    self.session_id = session_id
    self.w3c = False

  def start_session(self, desired_capabilities, browser_profile):
    self.capabilities = {}


class BossClient(object):
    SESSION_ID_FILE = "/tmp/boss-session-id.tmp"
    SELENIUM_URL = 'http://127.0.0.1:4444/wd/hub'

    def login(self, email, password):
        self.driver.get("https://account.bosscontrols.com/login")

        try:
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.XPATH, self.container_path()))
            )
        except TimeoutException:
            form = self.driver.find_element_by_id("loginformpage")
            form.find_element_by_id("login_user").send_keys(email)
            form.find_element_by_id("login_pass").send_keys(password)
            form.submit()
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.XPATH, self.container_path()))
            )

    def new_driver(self):
        driver = webdriver.Remote(command_executor=self.SELENIUM_URL, desired_capabilities=DesiredCapabilities.FIREFOX)
        with open(self.SESSION_ID_FILE, "w") as f:
            f.write(driver.session_id)
        return driver

    def existing_driver(self):
        try:
            session_id = file.read(open(self.SESSION_ID_FILE))
            driver = ExistingSeleniumSession(session_id=session_id, desired_capabilities=DesiredCapabilities.FIREFOX)
            driver.get("http://google.com") # will raise WebDriverException if the session was deleted
        except (IOError, WebDriverException):
            return None


    def __init__(self, email, password, device):
        self.driver = self.existing_driver() or self.new_driver()
        self.device = device

        self.login(email, password)

    def container_path(self):
        return ("//div[@class='contain']"
        "/div[@class='tile device']"
        "//h3[@title='{device}']"
        "/../..".format(device=self.device))

    def toggle(self):
        self.driver.find_element_by_xpath(self.container_path() + "/div[@class='right']/div[contains(@class, 'bottom')]/img").click()

    def switch(self, status):
        if (status == 'on' and self.status() in ['off', 'switching-off']) or (status == 'off' and self.status() in ['on', 'switching-on']):
            self.toggle()

    def power(self):
        raw_power = self.driver.find_element_by_xpath(self.container_path() + "/div[@class='left']/div[@class='bottom']/h2").text
        magnitude, unit = raw_power.split(' ') if raw_power != '' else [0, 'W']
        return {'unit': unit, 'magnitude': float(magnitude)}

    def pending(self):
        return len(self.driver.find_elements_by_xpath(self.container_path() + "//div[@class='bottom pending']")) > 0

    def on(self):
        return len(self.driver.find_elements_by_xpath(self.container_path() + "//img[@title='Click to turn the device off']")) > 0

    def status(self):
        if self.pending():
            if self.on():
                return 'switching-on'
            else:
                return 'switching-off'
        else:
            if self.on():
                return 'on'
            else:
                return 'off'
