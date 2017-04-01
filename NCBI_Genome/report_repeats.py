#! /usr/bin/env python

"""Search for and report about genomes with repeated values."""

import argparse
import sys


def report_repeats(counts, tag):
    print "%ss number is %d" % (tag, len(counts))
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
    bpacs = dict()
    pairs = dict()
    gcacs = dict()
    with args.intab as intab:
        columns = intab.readline().strip("\n#").split("\t")
        c_index = dict([(col, ind) for ind, col in enumerate(columns)])
        for line in intab:
            vals = line.strip().split("\t")
            taxid = vals[c_index["TaxID"]]
            bpac = vals[c_index["BioProject Accession"]]
            pair = taxid + "-" + bpac
            taxids[taxid] = taxids.get(taxid, 0) + 1
            bpacs[bpac] = bpacs.get(bpac, 0) + 1
            pairs[pair] = pairs.get(pair, 0) + 1
            for gcac in vals[c_index["Chromosomes/INSDC"]].split(","):
                gcacs[gcac] = gcacs.get(gcac, 0) + 1
            if vals[c_index["Plasmids/INSDC"]] != "-":
                for gcac in vals[c_index["Plasmids/INSDC"]].split(","):
                    gcacs[gcac] = gcacs.get(gcac, 0) + 1
    report_repeats(taxids, "TaxID")
    report_repeats(bpacs, "BioProjectAC")
    report_repeats(pairs, "TaxID-BioProjectAC pair")
    report_repeats(gcacs, "INSDC AC")


if __name__ == "__main__":
    sys.exit(main())

