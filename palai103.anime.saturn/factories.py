from typing import List
from models import Episode, KodiDirectoryItem, Playlist
from utils import Config
import xbmcplugin
import xbmcgui


class KodiFactory:
    def set_handle(self, handle):
        self.handle = handle

    def set_config(self, config: Config):
        self.config = config


class KodiPlaylistItemsFactory(KodiFactory):
    def __init__(self, playlist_loader) -> None:
        self.playlist_loader = playlist_loader

    def create_playlists_items(self, query) -> List[KodiDirectoryItem]:
        xbmcplugin.setPluginCategory(self.handle, "Reasearch results")
        xbmcplugin.setContent(self.handle, "videos")

        playlist_list_items = []
        playlist: Playlist
        for playlist in self.playlist_loader.get_playlists(query=query):
            list_item = xbmcgui.ListItem(label=playlist.name)
            list_item.setArt(
                {
                    "thumb": playlist.thumb,
                    "icon": playlist.thumb,
                    "fanart": playlist.thumb,
                }
            )
            list_item.setInfo("video", {"title": playlist.name, "mediatype": "video"})
            list_item_url = self.config.get_url(
                action="listingepisodes",
                name=playlist.name,
                thumb=playlist.thumb,
                episodes_url=playlist.episodes_url,
                chunk_index=0,
            )
            playlist_list_items.append(
                KodiDirectoryItem(
                    handle=self.handle,
                    url=list_item_url,
                    listitem=list_item,
                    isFolder=True,
                )
            )

        return playlist_list_items


class KodiEpisodeItemsFactory(KodiFactory):
    def __init__(self, episode_loader, episodes_chunk_limit=50) -> None:
        self.episode_loader = episode_loader
        self.episodes_chunk_limit = episodes_chunk_limit

    def create_episodes_items(
        self, episodes_url, playlist_name, playlist_thumb, chunk_index
    ) -> List[KodiDirectoryItem]:
        xbmcplugin.setPluginCategory(self.handle, playlist_name)
        xbmcplugin.setContent(self.handle, "videos")
        playlist_episodes = self.episode_loader.get_episodes(episodes_url=episodes_url)

        episode_list_items = []
        if len(playlist_episodes) > self.episodes_chunk_limit:
            episodes_chunks = [
                playlist_episodes[i : i + self.episodes_chunk_limit]
                for i in range(0, len(playlist_episodes), self.episodes_chunk_limit)
            ]
            current_chunk_episodes = episodes_chunks[int(chunk_index)]
            del episodes_chunks[int(chunk_index)]

            for index, chunk in enumerate(episodes_chunks):
                if index < int(chunk_index):
                    actual_index = int(index)
                else:
                    actual_index = int(index) + 1

                chunk_range_string = f"{playlist_name} Episodes [{playlist_episodes.index(chunk[0])+1}-{playlist_episodes.index(chunk[-1])+1}]"
                list_item = xbmcgui.ListItem(label=chunk_range_string)
                list_item_url = self.config.get_url(
                    action="listingepisodes",
                    name=chunk_range_string,
                    thumb=playlist_thumb,
                    episodes_url=episodes_url,
                    chunk_index=actual_index,
                )
                episode_list_items.append(
                    KodiDirectoryItem(
                        handle=self.handle,
                        url=list_item_url,
                        listitem=list_item,
                        isFolder=True,
                    )
                )

            playlist_episodes = current_chunk_episodes

        episode: Episode
        for episode in playlist_episodes:
            list_item = xbmcgui.ListItem(label=episode.name)
            list_item.setArt(
                {
                    "thumb": episode.thumb,
                    "icon": episode.thumb,
                    "fanart": episode.thumb,
                }
            )
            list_item.setInfo("video", {"title": episode.name, "mediatype": "video"})
            list_item.setProperty("IsPlayable", "true")
            list_item_url = self.config.get_url(action="play", video=episode.url)
            episode_list_items.append(
                KodiDirectoryItem(
                    handle=self.handle,
                    url=list_item_url,
                    listitem=list_item,
                    isFolder=False,
                )
            )

        return episode_list_items
