from urllib import request, parse, error
import time
import json
from datetime import date
import queue
import threading
import os, os.path

class DatabaseError(Exception):
    pass

class Database(object):
    """Assembles the scryfall database from bulk data"""
    def __init__(self, delay=0.1, cache_dir="_cache", bulk_database="oracle_cards"):
        self.api_bulk_info = "https://api.scryfall.com/bulk-data"
        self.bulk_database = "oracle_cards"
        self.encoding = "utf-8"
        self.bulk_data_uri = None

        self.work = queue.SimpleQueue()
        self.out = queue.SimpleQueue()
        self.thread = None
        self.delay = delay

        self.dir = cache_dir
        # Create cache dir
        if not os.path.exists(self.dir):
            os.mkdir(self.dir)
        elif not os.path.isdir(self.dir):
            raise FileExistsError("{} already exists".format(self.dir))
        
        self.bulk_info = os.path.join(self.dir, "bulk_info.json")
        self.bulk_data = os.path.join(self.dir, "bulk_data.json")
        self.bulk_data_json = None

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
        if not self.thread:
            self.thread = threading.Thread(target=self._worker)
            self.thread.start()
        self.work.put(url)
        return self.out.get()

    def stop(self):
        self.work.put(None)
        self.thread.join()
        self.thread = None

    def check_bulk_info(self):
        start_time = time.time()
        if os.path.exists(self.bulk_info):
            with open(self.bulk_info, 'r') as f:
                cur_info = json.load(f)
            bulk_database_info = None
            for i in cur_info["data"]:
                if i["type"] == self.bulk_database:
                    bulk_database_info = i
                    break
            if not bulk_database_info:
                raise DatabaseError("{} not found in bulk-data".format(self.bulk_database))
            old_date = date.fromisoformat(bulk_database_info["updated_at"][:10])
            self.bulk_data_uri = bulk_database_info["permalink_uri"]
            if old_date < date.today():
                self.update_bulk_info(old_date)
        else:
            self.update_bulk_info(None)
        if not os.path.exists(self.bulk_data):
            self.update_bulk_data()
        print("Bulk data updated in {} seconds".format(time.time() - start_time))

    def update_bulk_info(self, old_date):
        new_info = self._fetch(self.api_bulk_info)
        if new_info["object"] == "error":
            raise DatabaseError("Error updating bulk info")
        bulk_database_info = None
        for i in new_info["data"]:
            if i["type"] == self.bulk_database:
                bulk_database_info = i
                break
        if not bulk_database_info:
            raise DatabaseError("{} not found in bulk-data".format(self.bulk_database))
        if old_date is None or old_date < date.fromisoformat(bulk_database_info["updated_at"][:10]):
            self.bulk_data_uri = bulk_database_info["permalink_uri"]
            self.update_bulk_data()
        with open(self.bulk_info, 'w') as f:
            json.dump(new_info, f)
        self.stop()

    def update_bulk_data(self):
        print("Updating bulk data")
        start_time = time.time()
        self.bulk_data_json = self._fetch(self.bulk_data_uri)
        with open(self.bulk_data, 'w') as f:
            json.dump(self.bulk_data_json, f)
        print("Bulk data downloaded and saved in {} seconds".format(time.time() - start_time))

    def load(self):
        start_time = time.time()
        self.check_bulk_info()
        if self.bulk_data_json is None:
            with open(self.bulk_data, 'r') as f:
                self.bulk_data_json = json.load(f)
        print("Loaded database in {} seconds".format(time.time() - start_time))

    def data(self):
        return self.bulk_data_json
