from cache import Cache
from search import Search
from formatter import Formatter, display
import vim
import sys

class VimScry(object):

    def __init__(self):
        self.hist = None
        self.searcher = None
        self.buf_name = "VimScry"
        self.buf = None
        self.initialized = False

    def setup(self):
        self.hist = Cache()
        self.searcher = Search()
        self.initialized = True

    def random_card(self):
        if not self.initialized:
            self.setup()
        print(str(Formatter(self.searcher.random())))

    def search(self, query):
        if not self.initialized:
            self.setup()
        query = query.lower()
        res = self.hist.get_search(query)
        if res:
            return res
        res = self.searcher.search(query)
        self.hist.save_search(res)
        self.hist.save()
        return res

    def create_buffer(self):
        vim.command("set switchbuf +=useopen")
        if not self.buf:
            vim.command("vnew")
            vim.command("setlocal buftype=nofile")
            vim.command("setlocal bufhidden=hide")
            vim.command("setlocal noswapfile")
            self.buf = vim.current.buffer
            self.buf.name = self.buf_name
        else:
            vim.command("vert sbuffer {}".format(self.buf_name))
        self.buf[:] = None
        vim.command("vertical resize 80")

    def scry(self):
        """Performs a search, and opens a new window (split vertically) with the results.
        Prints any errors out."""
        query = vim.eval("a:query")
        res = self.search(query)
        if res["object"] == "error":
            print("Error:", res["details"])
        else:
            self.create_buffer()
            if res["object"] == "list":
                self.buf[0] = '{} cards found for query "{}"'.format(res["total_cards"], res["query"])
                for c in res["data"]:
                    buf = vim.current.buffer
                    buf.append(c["name"])
            if res["object"] == "card":
                buf.append(res["name"])
                del buf[0]

scry = VimScry()
