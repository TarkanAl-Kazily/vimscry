from cache import Cache
from search import Search
from formatter import Formatter, display
import vim
import sys

hist = Cache()
searcher = Search()

def random_card():
    print(str(Formatter(searcher.random())))

def insert_random_card():
    card = searcher.random()
    row, col = vim.current.window.cursor
    current_line = vim.current.buffer[row-1]
    new_line = current_line[:col] + card["name"] + current_line[col:]
    vim.current.buffer[row-1] = new_line

def search(query):
    query.lower()
    res = hist.get_search(query)
    if res:
        return res
    res = searcher.search(query)
    hist.save_search(res)
    hist.save()
    return res

def scry():
    """Performs a search, and opens a new window (split vertically) with the results.
    Prints any errors out."""
    query = vim.eval("a:query")
    res = search(query)
    if res["object"] == "error":
        print("Error:", res["details"])
    else:
        vim.command("vnew")
        if res["object"] == "list":
            print("Cards found:", res["total_cards"])
            for c in res["data"]:
                buf = vim.current.buffer
                buf.append(c["name"])
        if res["object"] == "card":
            print("Cards found:", 1)
            buf.append(res["name"])
    
