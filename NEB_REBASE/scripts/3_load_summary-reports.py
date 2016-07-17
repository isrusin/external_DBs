#! /usr/bin/python

import argparse as ap
import urllib2
import ctypes
from multiprocessing import Process, Lock, Array, Value

def get_page(url, try_number):
    req = urllib2.Request(url, None, {"User-agent": "Mozilla"})
    for i in range(try_number):
        try:
            page = urllib2.urlopen(req).read()
            if page.startswith("DB-Library:"):
                continue
            return page
        except urllib2.URLError:
            print "try #%d failed, next try" % (i+1)
    return "Page was not loaded."

requrl = "http://tools.neb.com/~vincze/genomes/{type}.php?genome_id={gid}"

def download_pages(oupath, gids, index, l):
    while(index.value < len(gids)):
        l.acquire()
        gid = gids[index.value]
        index.value += 1
        l.release()
        with open(oupath.format(gid=gid, type="summary"), "w") as ouhtml:
            page = get_page(requrl.format(gid=gid, type="summary"), 20)
            ouhtml.write(page)
        with open(oupath.format(gid=gid, type="report"), "w") as ouhtml:
            page = get_page(requrl.format(gid=gid, type="report"), 20)
            ouhtml.write(page)

if __name__ == "__main__":
    parser = ap.ArgumentParser(
            description="Load summary and report pages."
            )
    parser.add_argument(
            "ingids", metavar="LIST.gids", type=ap.FileType("r"),
            help="input list of REBASE genome IDs"
            )
    parser.add_argument(
            "-o", dest="oupath", required=True,
            help="output path, use '{type}' and {gid} placeholders"
            )
    parser.add_argument(
            "-p", metavar="N", dest="p_number", default=20, type=int,
            help="number of page loading subprocesses, default is 20"
            )
    args = parser.parse_args()
    with args.ingids as ingids:
        gids = sorted(ingids.read().strip().split("\n"))
    print "Loading %d x 2 pages ..." % len(gids)
    sh_gids = Array(ctypes.c_char_p, gids)
    sh_index = Value("i", 0)
    l = Lock()
    for i in range(args.p_number):
        Process(target=download_pages,
                args=(args.oupath, sh_gids, sh_index, l)).start()

