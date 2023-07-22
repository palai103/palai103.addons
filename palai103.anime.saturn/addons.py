import ast
import sys
from typing import List
from models import KodiDirectoryItem
from utils import Config
import xbmc
import xbmcplugin
import xbmcgui
import xbmcaddon
from urllib.parse import parse_qsl


class AnimeSaturnAddon:
    def __init__(
        self, handle, playlist_items_factory, episode_items_factory, player
    ) -> None:
        self.addon = xbmcaddon.Addon("anime.saturn.addon")
        self.window = xbmcgui.Window(10000)

        self.config = Config(kodi_url=sys.argv[0])
        self.handle = handle
        self.playlist_items_factory = playlist_items_factory
        self.playlist_items_factory.set_handle(handle=self.handle)
        self.playlist_items_factory.set_config(config=self.config)
        self.episode_items_factory = episode_items_factory
        self.episode_items_factory.set_handle(handle=self.handle)
        self.episode_items_factory.set_config(config=self.config)
        self.player = player
        self.player.set_handle(handle=self.handle)

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
        search_url = self.config.get_url(action="search")
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
            previous_research_url = self.config.get_url(
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

    def get_user_input(self):
        kb = xbmc.Keyboard("", "Please enter the video title")
        kb.doModal()  # Onscreen keyboard appears
        if not kb.isConfirmed():
            return
        query = kb.getText()  # User input
        return query

    def add_directory_items(self, kdis: List[KodiDirectoryItem]):
        [
            xbmcplugin.addDirectoryItem(
                handle=kdi.handle,
                url=kdi.url,
                listitem=kdi.listitem,
                isFolder=kdi.isFolder,
            )
            for kdi in kdis
        ]
        xbmcplugin.addSortMethod(self.handle, xbmcplugin.SORT_METHOD_LABEL_IGNORE_THE)
        xbmcplugin.endOfDirectory(self.handle)

    def router(self, paramstring):
        """
        Router function that calls other functions
        depending on the provided paramstring

        :param paramstring: URL encoded plugin paramstring
        :type paramstring: str
        """
        params = dict(parse_qsl(paramstring))
        # Check the parameters passed to the plugin
        if params:
            if params["action"] == "search":
                # search the provided string query
                try:
                    self.add_directory_items(
                        self.playlist_items_factory.create_playlists_items(
                            self.get_user_input()
                        )
                    )
                except AttributeError as ae:
                    xbmc.log(
                        f"[ERROR] {ae}",
                        xbmc.LOGERROR,
                    )
                    self.initial_list()

            elif params["action"] == "listingepisodes":
                # display the list of episodes in a provided playlist
                self.add_directory_items(
                    self.episode_items_factory.create_episodes_items(
                        episodes_url=params["episodes_url"],
                        playlist_name=params["name"],
                        playlist_thumb=params["thumb"],
                        chunk_index=params["chunk_index"],
                    )
                )

            elif params["action"] == "play":
                # play a stream for the requested episode
                self.player.play_episode(episode_url=params["video"])
            else:
                # if the provided paramstring does not contain a supported action
                # we raise an exception. This helps to catch coding errors,
                # e.g. typos in action names.
                raise ValueError("Invalid paramstring: {}!".format(paramstring))
        else:
            # if the plugin is called from Kodi UI without any parameters,
            # call the initial function showing the search button and (if any)
            # the previous search
            self.initial_list()
