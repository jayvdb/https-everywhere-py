from requests import Session

from .adapter import HTTPSEverywhereAdapter, HTTPAdapter


class HTTPSEverywhereSession(Session):
    def __init__(self, *args, **kwargs):
        super(HTTPSEverywhereSession, self).__init__(*args, **kwargs)
        self.mount("https://", HTTPAdapter())
        self.mount("http://", HTTPSEverywhereAdapter())
