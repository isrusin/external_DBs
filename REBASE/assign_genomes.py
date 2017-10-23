#! /usr/bin/env python

"""Assign assembly AC to R-M components by sequence ACs."""

import argparse
import re
import sys


def read_dict(infile):
    oudict = dict()
    with infile:
        for line in infile:
            if line.startswith("#"):
                continue
            key, value = line.strip().split("\t", 1)
            oudict[key] = value
    return oudict


def main(argv=None):
    parser = argparse.ArgumentParser(
        description="Assign assembly AC to R-M components by sequence ACs."
    )
    parser.add_argument(
        "intsv", metavar="TSV", type=argparse.FileType("r"),
        help="input TSV file with sequence ACs (genes.tsv or proteins.tsv)"
    )
    parser.add_argument(
        "indct", metavar="DICT", type=argparse.FileType("r"),
        help="input dictionary with 'sequence AC'-'assembly AC' mapping"
    )
    parser.add_argument(
        "-o", dest="outsv", metavar="FILE", type=argparse.FileType("w"),
        default=sys.stdout, help="output file"
    )
    args = parser.parse_args(argv)
    asacs = read_dict(args.indct)
    asacs["Sequence AC"] = "Assembly AC"
    with args.intsv as intsv, args.outsv as outsv:
        for line in intsv:
            nm, ac, etc = line.strip().split("\t", 2)
            ac = ac.rsplit(".", 1)[0]
            asac = asacs.get(ac, "")
            if not asac:
                tag_m = re.match(
                    "(?:[A-Z]{2}_)?"
                    "(?P<tag>[A-Z]{4})"
                    "[0-9]{8,10}(?:\.[0-9]+)?",
                    ac
                )
                if tag_m:
                    asac = asacs.get(tag_m.group("tag"), "")
            outsv.write("\t".join([nm, ac, asac, etc]) + "\n")


if __name__ == "__main__":
    sys.exit(main())
