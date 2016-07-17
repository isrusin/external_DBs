#! /usr/bin/python

import argparse as ap
import sys
import re

enz_p = re.compile(r"HREF=/rebase/enz/(?P<name>.+?)\.html")

if __name__ == "__main__":
    parser = ap.ArgumentParser(description="Parse REBASE azlist page.")
    parser.add_argument(
            "inhtml", metavar="IN_PAGE.html", type=ap.FileType("r"),
            help="input HTML page with enzyme list"
            )
    parser.add_argument(
            "-o", dest="ounms", metavar="OU_LIST.nms", default=sys.stdout,
            type=ap.FileType("w"), help="output file, default is stdout"
            )
    args = parser.parse_args()
    with args.inhtml as inhtml:
        html = inhtml.read()
    nms = set()
    for enz_m in enz_p.finditer(html):
        nms.add(enz_m.group("name"))
    with args.ounms as ounms:
        ounms.write("\n".join(sorted(nms)) + "\n")

