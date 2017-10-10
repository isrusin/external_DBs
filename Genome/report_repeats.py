#! /usr/bin/env python

"""Search for and report about genomes with repeated values."""

import argparse
from collections import Counter
import sys


def report_repeats(counts, tag, number):
    print "%ss number is %d" % (tag, len(counts))
    if counts and sum(counts.values()) != len(counts):
        for key, count in counts.most_common(number):
            if count > 1:
                print "\t%s is repeated %d times" % (key, count)
    else:
        print "\tThere is no repeated %ss" % tag


def main(argv=None):
    parser = argparse.ArgumentParser(
        description="Get report about repeated genomes."
    )
    parser.add_argument(
        "intab", metavar="FILE", type=argparse.FileType("r"),
        help="input file with genomes"
    )
    parser.add_argument(
        "-n", "--top", type=int, default=10, help="number of the most"
        " frequently repeated tags to print, use without value to print"
        " all repeats; default 10"
    )
    args = parser.parse_args(argv)
    number = args.top
    asacs = Counter()
    taxids = Counter()
    bps = Counter()
    pairs = Counter()
    acs = Counter()
    with args.intab as intab:
        columns = intab.readline().strip("\n#").split("\t")
        c_index = dict([(col, ind) for ind, col in enumerate(columns)])
        for line in intab:
            vals = line.strip().split("\t")
            taxid = vals[c_index["TaxID"]]
            bp = vals[c_index["BioProject Accession"]]
            pair = taxid + "-" + bp
            asac = vals[c_index["Assembly Accession"]]
            asacs[asac] += 1
            taxids[taxid] += 1
            bps[bp] += 1
            pairs[pair] += 1
            replicons = vals[c_index["Replicons"]]
            if replicons == "-":
                continue
            for tag in replicons.split("; "):
                if ":" not in tag:
                    continue
                _seq, acvs = tag.strip(" /").split(":")
                for acv in acvs.split("/"):
                    acs[acv] += 1
    report_repeats(asacs, "Assembly AC", number)
    report_repeats(taxids, "TaxID", number)
    report_repeats(bps, "BioProject AC", number)
    report_repeats(pairs, "TaxID-BioProjectAC pair", number)
    report_repeats(acs, "AC", number)


if __name__ == "__main__":
    sys.exit(main())

