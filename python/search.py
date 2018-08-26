from urllib import request, parse, error
import time
import json
from datetime import date
import queue
import threading

class Search(object):
    """Handles accessing scryfall for new data"""
    def __init__(self, delay=0.1):
        self.api = "https://api.scryfall.com"
        self.encoding = "utf-8"
        self.delay = delay
        self.work = queue.SimpleQueue()
        self.out = queue.SimpleQueue()
        self.thread = threading.Thread(target=self._worker)

    def _url_search(self, query):
        """Returns a url corresponding to the search query"""
        res = self.api + "/cards/search?q=" + parse.quote(query)
        return res

    def _url_random(self):
        """Returns a url corresponding to the random query"""
        res = self.api + "/cards/random"
        return res

    def _worker(self):
        while True:
            url = self.work.get()
            if url is None:
                break
            self.out.put(self._download(url))
            time.sleep(self.delay)

    def _download(self, url):
        try:
            handle = request.urlopen(url)
            return json.loads(handle.read().decode(self.encoding))
        except error.HTTPError as e:
            return json.loads(e.read().decode(self.encoding))

    def _fetch(self, url):
        if not self.thread.is_alive():
            self.thread.start()
        self.work.put(url)
        return self.out.get()

    def search(self, query):
        """Performs a search on scryfall - returns List"""
        url = self._url_search(query)
        page = self._fetch(url)
        if page["object"] == "error":
            page["url"] = url
            page["query"] = query
            page["date"] = str(date.today())
            return page
        elif page["object"] == "list":
            cards = page["data"]
            while page["has_more"]:
                page = self._fetch(page["next_page"])
                if page["object"] == "error":
                    page["url"] = url
                    page["query"] = query
                    page["date"] = str(date.today())
                    return page
                cards += page["data"]
        result = {
                "object" : "list",
                "query" : query,
                "url" : url,
                "total_cards" : page["total_cards"],
                "data" : cards,
                "date" : str(date.today())
                }
        return result

    def random(self):
        """Performs random on scryfall - return Card"""
        url = self._url_random()
        page = self._fetch(url)
        page["date"] = str(date.today())
        if page["object"] == "error":
            page["url"] = url
            return page
        return page

    def stop(self):
        self.work.put(None)
        self.thread.join()
