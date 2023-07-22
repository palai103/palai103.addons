import json
import time
from selenium import webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.common.driver_utils import get_driver_path


def get_episode_selenium():
    url = "https://www.animesaturn.tv/watch?file=UGaddilbpVvFX&server=4"

    desired_capabilities = DesiredCapabilities.CHROME
    desired_capabilities["goog:loggingPrefs"] = {"performance": "ALL"}
    driverPath = get_driver_path("chromedriver")
    options = webdriver.ChromeOptions()
    options.add_argument("headless")
    options.add_argument("--ignore-certificate-errors")
    driver = webdriver.Chrome(
        driverPath, chrome_options=options, desired_capabilities=desired_capabilities
    )

    driver.get(url=url)

    time.sleep(2)

    episode_url = None
    for log in driver.get_log("performance"):
        message_json = json.loads(log["message"])["message"]
        try:
            if "x.mp4" in message_json["params"]["response"]["url"]:
                episode_url = message_json["params"]["response"]["url"]
                break
        except:
            pass

    driver.quit()
    return episode_url
