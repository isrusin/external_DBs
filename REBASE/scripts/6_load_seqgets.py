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

requrl = "http://rebase.neb.com/cgi-bin/seqget?{}"
def download_pages(oupath, nms, index, l):
    while(index.value < len(nms)):
        l.acquire()
        nm = nms[index.value]
        index.value += 1
        l.release()
        with open(oupath.format(nm), "w") as ouhtml:
            page = get_page(requrl.format(nm), 20)
            ouhtml.write(page)

if __name__ == "__main__":
    parser = ap.ArgumentParser(
            description="Load seqget pages."
            )
    parser.add_argument(
            "innms", metavar="IN_NMS", type=ap.FileType("r"),
            help="input list of REBASE R-M names"
            )
    parser.add_argument(
            "-o", metavar="SEQGET_PATH", dest="oupath", required=True,
            help="output path, use {} placeholder"
            )
    parser.add_argument(
            "-p", metavar="N", dest="p_number", default=10, type=int,
            help="number of page loading subprocesses, default is 10"
            )
    args = parser.parse_args()
    with args.innms as innms:
        nms = sorted(innms.read().strip().split("\n"))
    print "Loading %d pages ..." % len(nms)
    sh_nms = Array(ctypes.c_char_p, nms)
    sh_index = Value("i", 0)
    l = Lock()
    for i in range(args.p_number):
        Process(target=download_pages,
                args=(args.oupath, sh_nms, sh_index, l)).start()

