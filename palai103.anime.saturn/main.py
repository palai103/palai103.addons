import sys
from addons import AnimeSaturnAddon
from factories import KodiEpisodeItemsFactory, KodiPlaylistItemsFactory
from loaders import EpisodeLoader, PlaylistLoader
from players import KodiPlayer
from streamers import AnimeSaturnStreamer, StreamHideStreamer


if __name__ == "__main__":
    asa = AnimeSaturnAddon(
        handle=int(sys.argv[1]),
        playlist_items_factory=KodiPlaylistItemsFactory(
            playlist_loader=PlaylistLoader()
        ),
        episode_items_factory=KodiEpisodeItemsFactory(episode_loader=EpisodeLoader()),
        player=KodiPlayer(
            main_streamer=StreamHideStreamer(), backup_streamer=AnimeSaturnStreamer()
        ),
    )
    asa.router(sys.argv[2][1:])
