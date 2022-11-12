import sys
import time

from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By


email = sys.argv[1]
password = sys.argv[2]

chrome_service = Service(ChromeDriverManager().install())

chrome_options = Options()
options = [
    "--headless",
    "--disable-gpu",
    "--window-size=1920,1200",
    "--ignore-certificate-errors",
    "--disable-extensions",
    "--no-sandbox",
    "--disable-dev-shm-usage"
]
for option in options:
    chrome_options.add_argument(option)

driver = webdriver.Chrome(service=chrome_service, options=chrome_options)

driver.get("https://forge-vtt.com/account/login")
print(driver.title)
driver.find_element(By.ID, '__BVID__11').send_keys(email)
time.sleep(1)
driver.find_element(By.ID, '__BVID__13').send_keys(password)
time.sleep(1)
driver.find_element(By.CSS_SELECTOR, '#__BVID__15 > div:nth-child(1) > button:nth-child(1)').click()
time.sleep(5)
driver.get('https://forge-vtt.com/setup#itreachesout')
time.sleep(5)


driver.find_element(By.CSS_SELECTOR, 'div.border:nth-child(2) > div:nth-child(2) > div:nth-child(3) > button:nth-child(1)').click()
time.sleep(3)
driver.find_element(By.CSS_SELECTOR, '.list-group-item').click()
time.sleep(30)
