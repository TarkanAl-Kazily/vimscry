from database import Database
from parser import QueryParser
from formatter import Formatter, display
import vim
import sys
import webbrowser
import random
from os.path import join

class VimScry(object):

    def __init__(self, cache_path):
        self.database = None
        self.buf_name = "VimScry"
        self.buf = None
        self.qp = None
        self.initialized = False
        self.cache_path = cache_path

    def setup(self):
        self.database = Database(cache_dir=self.cache_path)
        self.database.load()
        self.qp = QueryParser()
        self.initialized = True

    def random_card(self):
        if not self.initialized:
            self.setup()
        print(str(Formatter(random.choice(self.database.data()))))

    def search(self, query, extras=False):
        if not self.initialized:
            self.setup()
        if not extras:
            query = "-(layout:planar or layout:scheme or layout:vanguard or layout:token or layout:emblem) ({})".format(query)
        n = self.qp.parse(query)
        res = [ c for c in self.database.data() if n.verify(c) ]
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
        self.create_buffer()
        self.buf[0] = '{} cards found for query `{}`'.format(len(res), query)
        for c in res:
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

    def copy_card_names(self):
        """Copies the name of the current card"""
        if vim.current.buffer != self.buf:
            return
        start = int(vim.eval('a:firstline'))
        end = int(vim.eval('a:lastline'))
        pos = vim.current.window.cursor
        if start == 1 and end == 1:
            print("No card selected")
            return
        if start == 1:
            start = 2
        card_names = []
        for row in range(start, 0, -1):
            if not self.buf[row][0:3] == " | ":
                card_names.append(self.buf[row])
                break
        for card in self.buf[start:end]:
            if not card[0:3] == " | ":
                card_names.append(card)
        vim.command("setlocal ma")
        for card in reversed(card_names):
            self.buf.append(card, 0)
        vim.command('silent 1,{}d'.format(len(card_names)))
        vim.command("setlocal noma")
        vim.current.window.cursor = pos
        print("{} cards copied".format(len(card_names)))

cache_dir = join(vim.eval('s:plugin_root_dir'), '..', '_cache')

scry = VimScry(cache_dir)
