#! /usr/bin/env python

"""Search for and report about genomes with repeated values."""

import argparse
import sys


def report_repeats(counts, tag):
    print "%ss number is %d" % (tag, len(counts))
    if not counts:
        print "\tThere is no repeated %ss" % tag
    for key, count in sorted(counts.items()):
        if count > 1:
            print "\t%s is repeated %d times" % (key, count)


def main(argv=None):
    parser = argparse.ArgumentParser(
        description="Get report about repeated genomes."
    )
    parser.add_argument(
        "intab", metavar="FILE", type=argparse.FileType("r"),
        help="input file with genomes"
    )
    args = parser.parse_args(argv)
    taxids = dict()
    bps = dict()
    pairs = dict()
    acs = dict()
    with args.intab as intab:
        columns = intab.readline().strip("\n#").split("\t")
        c_index = dict([(col, ind) for ind, col in enumerate(columns)])
        for line in intab:
            vals = line.strip().split("\t")
            taxid = vals[c_index["TaxID"]]
            bp = vals[c_index["BioProject Accession"]]
            pair = taxid + "-" + bp
            taxids[taxid] = taxids.get(taxid, 0) + 1
            bps[bp] = bps.get(bp, 0) + 1
            pairs[pair] = pairs.get(pair, 0) + 1
            for tag in vals[c_index["Replicons"]].split("; "):
                _seq, acvs = tag.strip(" /").split(":")
                for acv in acvs.split("/"):
                    acs[acv] = acs.get(acv, 0) + 1
    report_repeats(taxids, "TaxID")
    report_repeats(bps, "BioProjectAC")
    report_repeats(pairs, "TaxID-BioProjectAC pair")
    report_repeats(acs, "AC")


if __name__ == "__main__":
    sys.exit(main())

