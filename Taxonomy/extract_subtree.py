#! /usr/bin/env python

"""Truncate taxonomy file by root taxIDs."""

import argparse
import sys


def main(argv=None):
    parser = argparse.ArgumentParser(
        description="Truncate taxonomy file by root taxID(s)."
    )
    parser.add_argument(
        "root", metavar="TaxID", nargs="+", help="root TaxID"
    )
    parser.add_argument(
        "-i", dest="intab", type=argparse.FileType("r"), required=True,
        help="input taxonomy file"
    )
    parser.add_argument(
        "-o", dest="outab", type=argparse.FileType("w"), required=True,
        help="truncated taxonomy file"
    )
    args = parser.parse_args(argv)
    ptaxids = dict()
    with args.intab as intab:
        for line in intab:
            taxid, ptaxid, etc = line.strip().split("\t", 2)
            ptaxids[taxid] = ptaxid
        taxids = set(args.root)
        size = 0
        while len(taxids) != size:
            size = len(taxids)
            for taxid, ptaxid in ptaxids.items():
                if ptaxid in taxids:
                    taxids.add(taxid)
        print "%d TaxIDs were selected." % size
        intab.seek(0)
        with args.outab as outab:
            outab.write(intab.readline())
            for line in intab:
                taxid, etc = line.split("\t", 1)
                if taxid in taxids:
                    outab.write(line)


if __name__ == "__main__":
    sys.exit(main())

