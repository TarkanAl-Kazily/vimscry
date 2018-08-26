import os
from cache import Cache
from search import Search
from formatter import Formatter

hist = Cache()
scry = Search()

def display(result):
    print(str(Formatter(result)))

def random_card():
    display(scry.random())
