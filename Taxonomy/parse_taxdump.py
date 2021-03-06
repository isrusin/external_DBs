#! /usr/bin/env python

"""Parse NCBI taxdump archive and write data to TSV file."""

from __future__ import print_function
import argparse
import sys
import tarfile


def main(argv=None):
    parser = argparse.ArgumentParser(
        description="Prepare taxonomy data file."
    )
    parser.add_argument(
        "taxdump", metavar="TAXDUMP.tgz", type=argparse.FileType("rb"),
        help="NCBI taxdump file"
    )
    parser.add_argument(
        "-o", dest="outab", metavar="FILE", required=True,
        type=argparse.FileType("w"), help="output file"
    )
    args = parser.parse_args(argv)
    names = dict()
    taxids = set()
    intar = tarfile.open(fileobj=args.taxdump)
    innames = intar.extractfile("names.dmp")
    for line in innames:
        vals = line.strip("\n\t|").split("\t|\t")
        taxid, name = vals[:2]
        taxids.add(taxid)
        if vals[3] == "scientific name":
            names[taxid] = name
    innames.close()
    print("%d taxons were loaded." % len(taxids), file=sys.stderr)
    missed = len(taxids) - len(names)
    if missed:
        print(
            "%d taxids have no scientific names!" % missed,
            file=sys.stderr
        )
    ranks = dict()
    innodes = intar.extractfile("nodes.dmp")
    for line in innodes:
        vals = line.strip("\n\t|").split("\t|\t")
        taxid, ptaxid, rank = vals[:3]
        if taxid not in taxids:
            print(
                "Warning: %s has no name at all!" % taxid,
                file=sys.stderr
            )
        if taxid not in names:
            print(
                "Warning: %s has no scientific name!" % taxid,
                file=sys.stderr
            )
        ranks[taxid] = (rank, ptaxid)
    innodes.close()
    print("%d nodes were loaded." % len(ranks), file=sys.stderr)
    with args.outab as outab:
        outab.write("#:TaxID\tParent taxID\tScientific name\tRank\n")
        for taxid in taxids:
            name = names.get(taxid, "?")
            if taxid not in ranks:
                print(
                    "%s has no rank and parent, skipped" % taxid,
                    file=sys.stderr
                )
                continue
            rank, ptaxid = ranks[taxid]
            outab.write("\t".join((taxid, ptaxid, name, rank)) + "\n")


if __name__ == "__main__":
    sys.exit(main())

