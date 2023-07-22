from urllib.parse import urlencode


class Config:
    def __init__(self, kodi_url) -> None:
        self.kodi_url = kodi_url

    def get_url(self, **kwargs):
        """
        Create a URL for calling the plugin recursively from the given set of keyword arguments.

        :param kwargs: "argument=value" pairs
        :return: plugin call URL
        :rtype: str
        """
        return "{}?{}".format(self.kodi_url, urlencode(kwargs))
