#!/usr/local/bin/python3
import argparse
import sys
from cache import Cache
from search import Search
from formatter import Formatter, display

hist = Cache()
scry = Search()

def search(query):
    res = hist.get_search(query)
    if res:
        return res
    res = scry.search(query)
    hist.save_search(res)
    hist.save()
    return res

def arguments():
    parser = argparse.ArgumentParser(description="Perform Scryfall card searches")
    parser.add_argument("-c", "--clear",
            help="Clear cache of previous searches",
            action="store_true",
            dest="clear")
    parser.add_argument("-r", "--random",
            help="Get a random card",
            action="store_true",
            dest="random")
    parser.add_argument("-f", "--file",
            help="Output list of card names to a file",
            dest="file")
    parser.add_argument("--overwrite",
            help="Overwrites file (requires -f)",
            action="store_true",
            dest="overwrite")
    parser.add_argument("--history",
            help="Prints search history",
            action="store_true",
            dest="history")
    return parser.parse_args()

def main(args):
    if args.clear:
        hist.clear()
    if args.history:
        print(str(hist))
    if args.random:
        display(scry.random())
    else:
        fp = None
        if args.file:
            fp = open(args.file, 'w' if args.overwrite else 'a')

        for line in sys.stdin:
            res = search(line.lower())
            if fp:
                try:
                    fp.write(Formatter(res).names())
                except FormatException:
                    pass
            else:
                display(res)

        if args.file:
            fp.close()

    scry.stop()

if __name__ == "__main__":
    args = arguments()
    main(args)
