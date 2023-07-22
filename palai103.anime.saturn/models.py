import json


class PyDanticByHand:
    def dict(self):
        return json.loads(self.__str__())

    def __str__(self):
        return json.dumps(self.__dict__)


class Playlist(PyDanticByHand):
    def __init__(self, name, thumb, episodes_url) -> None:
        self.name = name
        self.thumb = thumb
        self.episodes_url = episodes_url


class Episode(PyDanticByHand):
    def __init__(self, name, thumb, url) -> None:
        self.name = name
        self.thumb = thumb
        self.url = url


class KodiDirectoryItem(PyDanticByHand):
    def __init__(self, handle, url, listitem, isFolder) -> None:
        """
        handle integer - handle the plugin was started with.
        items List - list of (url, listitem[, isFolder]) as a tuple to add.
        """
        self.handle = handle
        self.url = url
        self.listitem = listitem
        self.isFolder = isFolder
