#! /usr/bin/python

import argparse as ap

if __name__ == "__main__":
    parser = ap.ArgumentParser(
            description="Truncate taxonomy file by root taxID(s)."
            )
    parser.add_argument(
            "root", metavar="TaxID", nargs="+", help="root TaxID"
            )
    parser.add_argument(
            "-i", dest="intab", type=ap.FileType("r"),
            help="input taxonomy file"
            )
    parser.add_argument(
            "-o", dest="outab", type=ap.FileType("w"),
            help="truncated taxonomy file"
            )
    args = parser.parse_args()
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

