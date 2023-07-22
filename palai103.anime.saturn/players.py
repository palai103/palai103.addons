import requests
import xbmc
import xbmcgui
import xbmcplugin
from bs4 import BeautifulSoup


class KodiPlayer:
    def __init__(self, main_streamer, backup_streamer) -> None:
        self.main_streamer = main_streamer
        self.backup_streamer = backup_streamer

    def set_handle(self, handle):
        self.handle = handle

    def play_episode(self, episode_url: str):
        episode_redirected_page = requests.post(episode_url)
        episode_redirected_page = BeautifulSoup(
            episode_redirected_page.text, "html.parser"
        )
        episode_redirected_page_url = episode_redirected_page.find(
            "div", class_="btn-light"
        ).parent["href"]

        try:
            episode_path = self.main_streamer.get_streaming_url(
                url=episode_redirected_page_url
            )
        except Exception as e:
            xbmc.log(
                f"[ERROR] {e}",
                xbmc.LOGERROR,
            )
            episode_path = self.backup_streamer.get_streaming_url(
                url=episode_redirected_page_url
            )

        # Create a playable item with a path to play.
        play_item = xbmcgui.ListItem(path=episode_path)
        # Pass the item to the Kodi player.
        xbmcplugin.setResolvedUrl(self.handle, True, listitem=play_item)
