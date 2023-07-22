import json
import re
import time
import requests
from selenium import webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.common.driver_utils import get_driver_path


class AnimeSaturnStreamer:
    def get_streaming_url(self, url):
        episode_url = (
            re.findall(
                r'"(.*?)"',
                re.search(r"\bimage:.*", requests.post(url).text).group(),
            )[0].split("playlist")[0]
            + "480p/playlist_480p.m3u8"
        )

        return episode_url


class StreamHideStreamer:
    def __init__(self, time_to_wait=2) -> None:
        self.time_to_wait = time_to_wait

    def get_streaming_url(self, url):
        desired_capabilities = DesiredCapabilities.CHROME
        desired_capabilities["goog:loggingPrefs"] = {"performance": "ALL"}
        driverPath = get_driver_path("chromedriver")
        options = webdriver.ChromeOptions()
        options.add_argument("headless")
        options.add_argument("--ignore-certificate-errors")
        driver = webdriver.Chrome(
            driverPath,
            chrome_options=options,
            desired_capabilities=desired_capabilities,
        )

        driver.get(url=f"{url}&server=4")
        time.sleep(self.time_to_wait)

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
