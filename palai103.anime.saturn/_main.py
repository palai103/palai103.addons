# Module: main
# Author: Roman V. M.
# Created on: 28.11.2014
# License: GPL v.3 https://www.gnu.org/copyleft/gpl.html
"""
Example video plugin that is compatible with Kodi 19.x "Matrix" and above
"""
import sys
import os
import re
import requests
import ast
import xbmc
import xbmcgui
import xbmcplugin
import xbmcaddon

from bs4 import BeautifulSoup
from urllib.parse import urlencode, parse_qsl
from urllib.request import Request
from test_selenium import get_episode_selenium


PLUGIN_HANDLE = None


class AnimeSaturnAddon:
    def __init__(self):
        self.addon = xbmcaddon.Addon("anime.saturn.addon")
        self.window = xbmcgui.Window(10000)
        self.as_url = "https://www.animesaturn.tv/"
        self.url = sys.argv[0]
        self.handle = int(sys.argv[1])
        self.chunk_size = 50

    def get_url(self, **kwargs):
        """
        Create a URL for calling the plugin recursively from the given set of keyword arguments.

        :param kwargs: "argument=value" pairs
        :return: plugin call URL
        :rtype: str
        """
        return "{}?{}".format(self.url, urlencode(kwargs))

    def get_value_from_settings(self, setting_key: str, value_field: str):
        try:
            setting = self.addon.getSetting(setting_key)
            return ast.literal_eval(setting)[value_field]
        except SyntaxError:
            return None

    def get_playlists(self, query):
        """
        Get the list of video categories.

        Here you can insert some parsing code that retrieves
        the list of video categories (e.g. 'Movies', 'TV-shows', 'Documentaries' etc.)
        from some site or API.

        .. note:: Consider using `generator functions <https://wiki.python.org/moin/Generators>`_
            instead of returning lists.

        :return: The list of video categories
        :rtype: types.GeneratorType
        """

        html_search_string = "%20".join(query.split(" "))
        playlist_url = os.path.join(
            self.as_url, f"animelist?search={html_search_string}"
        )
        page = requests.get(playlist_url)
        page_soup = BeautifulSoup(page.content, "html.parser")
        search_results = page_soup.find_all("ul", class_="list-group")

        results = []
        for res in search_results:
            results.append(
                {
                    "name": res.find("a", class_="badge").get_text(),
                    "thumb": res.find("img", class_="locandina-archivio")["src"],
                    "episodes": res.find("a", class_="thumb")["href"],
                }
            )

        return results

    def get_episodes(self, episodes):
        """
        Get the list of videofiles/streams.

        Here you can insert some parsing code that retrieves
        the list of video streams in the given category from some site or API.

        .. note:: Consider using `generators functions <https://wiki.python.org/moin/Generators>`_
            instead of returning lists.

        :param episodes: Url for the episodes list
        :type episodes: str
        :return: the list of episodes in the playlist
        :rtype: list
        """
        results = []
        for episode in episodes[:5]:
            episode_redirected_page_1 = requests.post(episode["href"])
            episode_redirected_page_1 = BeautifulSoup(
                episode_redirected_page_1.text, "html.parser"
            )
            episode_redirected_page_url = episode_redirected_page_1.find(
                "div", class_="btn-light"
            ).parent["href"]

            # TODO: add "&server=4"
            episode_redirected_page_2 = requests.post(
                f"{episode_redirected_page_url}&server=4"
            )
            # TODO: this could be casted manually or we can think another way to pass the m3u8 to ffmpeg
            """ episode_url = (
                re.findall(
                    r'"(.*?)"',
                    re.search(r"\bimage:.*", episode_redirected_page_2.text).group(),
                )[0].split("playlist")[0]
                + "480p/playlist_480p.m3u8"
            ) """
            episode_url = get_episode_selenium()
            xbmc.log(
                f"[DEBUG] {episode_url}",
                xbmc.LOGERROR,
            )

            results.append(
                {
                    "name": episode.text.replace("\n", "")
                    .replace("\r", "")
                    .replace(" ", ""),
                    "url": episode_url,
                }
            )

        return results

    def get_user_input(self):
        kb = xbmc.Keyboard("", "Please enter the video title")
        kb.doModal()  # Onscreen keyboard appears
        if not kb.isConfirmed():
            return
        query = kb.getText()  # User input
        return query

    def initial_list(self):
        """
        Shows the initial list of commands: the search button and the last research.
        """
        xbmcplugin.setPluginCategory(self.handle, "Search")
        xbmcplugin.setContent(self.handle, "videos")

        list_items = []

        search_item = xbmcgui.ListItem(label="Search")
        search_item.setArt(
            {
                "thumb": "resources/search.png",
                "icon": "resources/search.png",
                "fanart": "resources/search.png",
            }
        )
        search_url = self.get_url(action="search")
        list_items.append((search_url, search_item, True))

        if ast.literal_eval(self.addon.getSetting("current_playlist"))["name"] != "":
            previous_research_item = xbmcgui.ListItem(
                label=ast.literal_eval(self.addon.getSetting("current_playlist"))[
                    "name"
                ]
            )

            previous_research_item.setArt(
                {
                    "thumb": ast.literal_eval(
                        self.addon.getSetting("current_playlist")
                    )["thumb"],
                    "icon": ast.literal_eval(self.addon.getSetting("current_playlist"))[
                        "thumb"
                    ],
                    "fanart": ast.literal_eval(
                        self.addon.getSetting("current_playlist")
                    )["thumb"],
                }
            )
            previous_research_item.setInfo(
                "video",
                {
                    "title": ast.literal_eval(
                        self.addon.getSetting("current_playlist")
                    )["name"],
                    "mediatype": "video",
                },
            )
            previous_research_url = self.get_url(
                action="listingepisodes",
                name=ast.literal_eval(self.addon.getSetting("current_playlist"))[
                    "name"
                ],
                thumb=ast.literal_eval(self.addon.getSetting("current_playlist"))[
                    "thumb"
                ],
                episodes=ast.literal_eval(self.addon.getSetting("current_playlist"))[
                    "episodes"
                ],
                chunk_index=ast.literal_eval(self.addon.getSetting("current_playlist"))[
                    "chunk_index"
                ],
            )
            list_items.append((previous_research_url, previous_research_item, True))

        xbmcplugin.addDirectoryItems(self.handle, list_items)
        # xbmcplugin.addSortMethod(self.handle, xbmcplugin.SORT_METHOD_LABEL_IGNORE_THE)
        xbmcplugin.endOfDirectory(self.handle)

    def list_playlists(self):
        """
        Create the list of playlists in the Kodi interface.
        """
        xbmcplugin.setPluginCategory(self.handle, "Reasearch results")
        xbmcplugin.setContent(self.handle, "videos")

        query = self.get_user_input()
        try:
            playlists = self.get_playlists(query)

            for playlist in playlists:
                list_item = xbmcgui.ListItem(label=playlist["name"])
                list_item.setArt(
                    {
                        "thumb": playlist["thumb"],
                        "icon": playlist["thumb"],
                        "fanart": playlist["thumb"],
                    }
                )
                list_item.setInfo(
                    "video", {"title": playlist["name"], "mediatype": "video"}
                )
                url = self.get_url(
                    action="listingepisodes",
                    name=playlist["name"],
                    thumb=playlist["thumb"],
                    episodes=playlist["episodes"],
                    chunk_index=0,
                )
                is_folder = True
                xbmcplugin.addDirectoryItem(self.handle, url, list_item, is_folder)

            xbmcplugin.addSortMethod(
                self.handle, xbmcplugin.SORT_METHOD_LABEL_IGNORE_THE
            )
            xbmcplugin.endOfDirectory(self.handle)
        except AttributeError:
            self.initial_list()

    def list_episodes(
        self, playlist_name, playlist_thumb, playlist_episodes_url, chunk_index
    ):
        """
        Create the list of playable videos in the Kodi interface.

        :param episodes: Url to the episodes
        :type episodes: str
        """
        xbmc.log(
            f"[DEBUG] {playlist_name}, {playlist_thumb}, {playlist_episodes_url}, {chunk_index}",
            xbmc.LOGERROR,
        )

        episodes_page = requests.get(playlist_episodes_url)
        episodes_page_soup = BeautifulSoup(episodes_page.content, "html.parser")
        playlist_episodes = episodes_page_soup.find(
            "div", class_="tab-content"
        ).find_all("a", class_="bottone-ep")

        if len(playlist_episodes) > self.chunk_size:
            episodes_chunks = [
                playlist_episodes[i : i + self.chunk_size]
                for i in range(0, len(playlist_episodes), self.chunk_size)
            ]
            current_chunk_episodes = episodes_chunks[int(chunk_index)]
            del episodes_chunks[int(chunk_index)]

            for index, chunk in enumerate(episodes_chunks):
                if index < int(chunk_index):
                    actual_index = int(index)
                else:
                    actual_index = int(index) + 1

                playlist_name_without_episodes = playlist_name.split("Episodes")[0]
                chunk_range_string = f"{playlist_name_without_episodes} Episodes [{playlist_episodes.index(chunk[0])+1}-{playlist_episodes.index(chunk[-1])+1}]"
                list_item = xbmcgui.ListItem(label=chunk_range_string)
                url = self.get_url(
                    action="listingepisodes",
                    name=chunk_range_string,
                    thumb=playlist_thumb,
                    episodes=playlist_episodes_url,
                    chunk_index=actual_index,
                )
                xbmcplugin.addDirectoryItem(self.handle, url, list_item, isFolder=True)

            playlist_episodes = current_chunk_episodes

        xbmcplugin.setPluginCategory(self.handle, playlist_name)
        xbmcplugin.setContent(self.handle, "videos")

        if playlist_name != self.get_value_from_settings("current_playlist", "name"):
            self.addon.setSetting(
                "current_playlist",
                '{{"name": "{}", "thumb": "{}", "episodes": "{}", "chunk_index": "{}"}}'.format(
                    playlist_name, playlist_thumb, playlist_episodes_url, chunk_index
                ),
            )
            self.addon.setSetting(
                "current_episodes", str(self.get_episodes(playlist_episodes))
            )

        for episode in ast.literal_eval(self.addon.getSetting("current_episodes")):
            list_item = xbmcgui.ListItem(label=episode["name"])
            list_item.setInfo("video", {"title": episode["name"], "mediatype": "video"})
            list_item.setProperty("IsPlayable", "true")
            url = self.get_url(action="play", video=episode["url"])
            is_folder = False
            xbmcplugin.addDirectoryItem(self.handle, url, list_item, is_folder)
        xbmcplugin.addSortMethod(self.handle, xbmcplugin.SORT_METHOD_LABEL_IGNORE_THE)
        xbmcplugin.endOfDirectory(self.handle)

    def play_video(self, path):
        """
        Play a video by the provided path.

        :param path: Fully-qualified video URL
        :type path: str
        """
        # Create a playable item with a path to play.
        play_item = xbmcgui.ListItem(path=path)
        # Pass the item to the Kodi player.
        xbmcplugin.setResolvedUrl(self.handle, True, listitem=play_item)

        """ play_item = xbmcgui.ListItem()
        play_item.setProperty("inputstream", "inputstream.adaptive")
        play_item.setProperty("inputstream.adaptive.manifest_type", "hls")
        play_item.setPath(path)
        xbmcplugin.setResolvedUrl(PLUGIN_HANDLE, True, play_item) """

    def router(self, paramstring):
        """
        Router function that calls other functions
        depending on the provided paramstring

        :param paramstring: URL encoded plugin paramstring
        :type paramstring: str
        """

        xbmcplugin.setSetting(self.handle, id="test", value="start")

        params = dict(parse_qsl(paramstring))
        # Check the parameters passed to the plugin
        if params:
            if params["action"] == "search":
                self.list_playlists()
            elif params["action"] == "listingepisodes":
                # Display the list of episodes in a provided playlist.
                self.list_episodes(
                    params["name"],
                    params["thumb"],
                    params["episodes"],
                    params["chunk_index"],
                )
            elif params["action"] == "play":
                # Play a video from a provided URL.
                self.play_video(params["video"])
            else:
                # If the provided paramstring does not contain a supported action
                # we raise an exception. This helps to catch coding errors,
                # e.g. typos in action names.
                raise ValueError("Invalid paramstring: {}!".format(paramstring))
        else:
            # If the plugin is called from Kodi UI without any parameters,
            # display the list of video categories
            # list_playlists()
            self.initial_list()


if __name__ == "__main__":
    asa = AnimeSaturnAddon()
    PLUGIN_HANDLE = int(sys.argv[1])
    asa.router(sys.argv[2][1:])
