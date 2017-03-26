#! /usr/bin/env python

"""Parse sequence lengths from GenBank Flatfiles."""

import argparse
import gzip
import sys


def main(argv=None):
    parser = argparse.ArgumentParser(
        description="Get sequence lengths by ACv list."
    )
    parser.add_argument(
        "inpath", metavar="GBK_PATH",
        help="input gbk path, use {} placeholder instead of ACv"
    )
    parser.add_argument(
        "-l", metavar="LIST", dest="inacv", type=argparse.FileType("r"),
        required=True, help="input ACv list"
    )
    parser.add_argument(
        "-o", metavar="FILE", dest="oudct", type=argparse.FileType("w"),
        default=sys.stdout, help="output dict file with lengths"
    )
    args = parser.parse_args(argv)
    with args.inacv as inacv:
        acvs = sorted(set(inacv.read().split()))
    inpath = args.inpath
    if "{" not in inpath:
        inpath += "/{}.gbk.gz"
    with args.oudct as oudct:
        for acv in acvs:
            with gzip.open(inpath.format(acv)) as ingbk:
                length = ingbk.readline().split()[2]
            oudct.write("%s\t%s\n" % (acv, length))


if __name__ == "__main__":
    sys.exit(main())

