#! /usr/bin/python

import argparse as ap
import gzip

if __name__ == "__main__":
    parser = ap.ArgumentParser(
            description="Get sequence lengths by ACv list."
            )
    parser.add_argument(
            "inpath", metavar="GBK_PATH",
            help="input gbk path, use {} placeholder instead of ACv"
            )
    parser.add_argument(
            "-l", metavar="IN.acv", dest="inacv", type=ap.FileType("r"),
            required=True, help="input list of ACvs"
            )
    parser.add_argument(
            "-o", metavar="OUT.dct", dest="oudct", type=ap.FileType("w"),
            required=True, help="output dict file with lengths"
            )
    args = parser.parse_args()
    with args.inacv as inacv:
        acvs = sorted(set(inacv.read().strip().split("\n")))
    inpath = args.inpath
    if "{" not in inpath:
        inpath += "/{}.gbk.gz"
    with args.oudct as oudct:
        for acv in acvs:
            with gzip.open(inpath.format(acv)) as ingbk:
                length = ingbk.readline().split()[2]
            oudct.write("%s\t%s\n" % (acv, length))

