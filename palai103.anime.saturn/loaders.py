import os
from typing import List
import requests
from bs4 import BeautifulSoup
from const import ANIME_SATURN_URL

from models import Episode, Playlist


class PlaylistLoader:
    def get_playlists(self, query) -> List[Playlist]:
        html_search_string = "%20".join(query.split(" "))
        playlist_url = os.path.join(
            ANIME_SATURN_URL, f"animelist?search={html_search_string}"
        )
        page = requests.get(playlist_url)
        page_soup = BeautifulSoup(page.content, "html.parser")
        search_results = page_soup.find_all("ul", class_="list-group")

        playsits_to_return: List[Playlist] = []
        for res in search_results:
            playsits_to_return.append(
                Playlist(
                    name=res.find("a", class_="badge").get_text(),
                    thumb=res.find("img", class_="locandina-archivio")["src"],
                    episodes_url=res.find("a", class_="thumb")["href"],
                )
            )

        return playsits_to_return


class EpisodeLoader:
    def get_episodes(self, episodes_url) -> List[Episode]:
        episodes_page = requests.get(episodes_url)
        episodes_page_soup = BeautifulSoup(episodes_page.content, "html.parser")

        cover_anime = episodes_page_soup.find("img", class_="cover-anime")["src"]

        episodes_to_return: List[Episode] = []
        for episode in episodes_page_soup.find("div", class_="tab-content").find_all(
            "a", class_="bottone-ep"
        ):
            episodes_to_return.append(
                Episode(
                    name=episode.text.strip(), thumb=cover_anime, url=episode["href"]
                )
            )

        return episodes_to_return


""" pll = PlaylistLoader()
pll.get_playlists("One Piece")
playlist = pll.get_playlists("One Piece")[0]
el = EpisodeLoader(playlist)
print([e.dict() for e in el.get_episodes(playlist.episodes_url)])
print(el.get_playlist().thumb) """
