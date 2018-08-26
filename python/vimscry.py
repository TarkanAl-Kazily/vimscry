from cache import Cache
from search import Search
from formatter import Formatter, display
import vim
import sys
import webbrowser

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
        if res and res["object"] == "list" and res["total_cards"] == len(res["data"]):
            return res
        res = self.searcher.search_confirm(query)
        self.hist.save_search(res)
        self.hist.save()
        return res

    def create_buffer(self):
        vim.command("set switchbuf +=useopen")
        if not self.buf:
            vim.command("vnew")
            vim.command("set filetype=vimscry")
            self.buf = vim.current.buffer
            self.buf.name = self.buf_name
        else:
            vim.command("vert sbuffer {}".format(self.buf_name))
        vim.command("setlocal ma")
        self.buf[:] = None
        vim.current.window.width = 80

    def scry(self):
        """Performs a search, and opens a new window (split vertically) with the results.
        Prints any errors out."""
        query = vim.eval("a:query")
        res = self.search(query)
        if res["object"] == "error":
            print("Error:", res["details"])
        else:
            self.create_buffer()
            self.buf[0] = '{} cards found for query `{}`'.format(res["total_cards"], res["query"])
            for c in res["data"]:
                self.buf.append(c["name"])
                face = str(Formatter(c))
                for line in face.splitlines():
                    self.buf.append(" | " + line)
            vim.command("setlocal noma")

    def open_card_url(self):
        """Opens the current card in a web browser"""
        if vim.current.buffer != self.buf:
            return
        row, col = vim.current.window.cursor
        if row == 1:
            print("No card selected")
            return
        line = self.buf[row-1]
        while not 'https://scryfall.com' in line:
            row += 1
            line = self.buf[row-1]
        try:
            url_start = line.index('https://scryfall.com')
            webbrowser.open(line[url_start:])
        except ValueError as e:
            print("No url found")
        except webbrowser.Error as e:
            print("Error opening url")

scry = VimScry()
