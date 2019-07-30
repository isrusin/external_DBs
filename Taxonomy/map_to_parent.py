#! /usr/bin/env python

"""Map taxIDs to parent taxIDs of the specified rank."""

from __future__ import print_function
import argparse
import sys


def main(argv=None):
    parser = argparse.ArgumentParser(
        description="Map taxIDs to parent taxIDs of the specified rank."
    )
    parser.add_argument(
        "intax", metavar="TAXONOMY", type=argparse.FileType("r"),
        help="input taxonomy file"
    )
    parser.add_argument(
        "-l", "--taxids", dest="inlist", metavar="LIST",
        type=argparse.FileType("r"), default=sys.stdin,
        help="list of taxIDs, default if STDIN"
    )
    parser.add_argument(
        "-p", "--parent", metavar="RANK", default="species",
        help="rank of the parent to match with, default is species"
    )
    parser.add_argument(
        "-k", "--keep-unmapped", metavar="STR", nargs="?", const="-",
        help="""keep unmapped taxIDs and match them with the specified tag,
        default tag is '-', default behaviour is to skip unmapped taxIDs"""
    )
    parser.add_argument(
        "-o", dest="oumap", metavar="MAP", type=argparse.FileType("w"),
        default=sys.stdout, help="output map file, default is STDOUT"
    )
    args = parser.parse_args(argv)
    ptaxids = dict()
    ranks = dict()
    with args.intax as intax:
        intax.readline()
        for line in intax:
            taxid, ptaxid, name, rank = line.strip().split("\t")
            ptaxids[taxid] = ptaxid
            ranks[taxid] = rank
    all_ranks = set(ranks.values())
    parent = args.parent
    if parent not in all_ranks:
        parser.error("Unknown rank '%s', proper ranks are:\n\t%s\n" % (
            parent, "\n\t".join(sorted(all_ranks))
        ))
    with args.inlist as inlist, args.oumap as oumap:
        oumap.write("#:TaxID\t%s taxID\n" % parent.capitalize())
        for line in inlist:
            taxid = itaxid = line.strip()
            if itaxid not in ptaxids:
                print("%s is not found, skipped." % taxid, file=sys.stderr)
                continue
            rank = ranks[itaxid]
            while rank != parent:
                itaxid = ptaxids[itaxid]
                if itaxid not in ptaxids:
                    itaxid = None
                    break
                rank = ranks[itaxid]
            itaxid = itaxid or args.keep_unmapped
            if itaxid is not None:
                oumap.write("%s\t%s\n" % (taxid, itaxid))


if __name__ == "__main__":
    sys.exit(main())

