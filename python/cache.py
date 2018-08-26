import os, os.path
import json
from uuid import uuid4
from datetime import date

class Cache(object):
    """Handles loading, storage, and history of searches"""
    def __init__(self, cache_dir="_cache", clear=False):
        self.dir = cache_dir
        self.history_path = os.path.join(self.dir, "history.json")
        self.history = None

        # Create cache dir
        if not os.path.exists(self.dir):
            os.mkdir(self.dir)
        elif not os.path.isdir(self.dir):
            raise FileExistsError("{} already exists".format(self.dir))

        self.load()
        if clear:
            self.clear()

    def _init_history(self):
        with open(self.history_path, 'w') as f:
            history = {
                    "length" : 0,
                    "searches" : [],
                    }
            json.dump(history, f)

    def load(self):
        """Initialize the history object"""
        if not os.path.exists(self.history_path):
            self._init_history()
        elif not os.path.isfile(self.history_path):
            raise IsADirectoryError("{} is a directory".format(self.history_path))

        try:
            with open(self.history_path) as f:
                self.history = json.load(f)

        except json.decoder.JSONDecodeError as e:
            os.remove(self.history_path)
            self._init_history()
            with open(self.history_path) as f:
                self.history = json.load(f)

    def save(self):
        """Saves the history object to a file"""
        with open(self.history_path, 'w') as f:
            json.dump(self.history, f)

    def save_search(self, search):
        """Saves a search to the cache"""
        filename = str(uuid4())
        while os.path.exists(os.path.join(self.dir, filename)):
            filename = str(uuid4())
        search = search.copy()
        with open(os.path.join(self.dir, filename), 'w') as f:
            json.dump(search, f)
        search.pop("data", None)
        search["file"] = filename
        self.history["searches"].append(search)
        self.history["length"] = len(self.history["searches"])

    def clear(self):
        """Removes all data from the cache"""
        for f in os.listdir(self.dir):
            f = os.path.join(self.dir, f)
            if os.path.isfile(f):
                os.remove(f)
        self.load()

    def get_search(self, query):
        """Returns the latest search corresponding to query, or None"""
        res = None
        res_date = None
        for s in self.history["searches"]:
            if s["query"] == query:
                if not res:
                    res = s
                    res_date = date.fromisoformat(res["date"])
                else:
                    s_date = date.fromisoformat(s["date"])
                    if s_date > res_date:
                        res = s
                        res_date = s_date
        if not res:
            return None
        with open(os.path.join(self.dir, res["file"])) as f:
            return json.load(f)


    def __str__(self):
        res = ""
        for entry in self.history["searches"]:
            res += entry["query"]
        return res

    def __repr__(self):
        res = "dir: {}, ".format(self.dir)
        res += "history_path: {}, ".format(self.history_path)
        res += "history: {}, ".format(self.history)
        return res
