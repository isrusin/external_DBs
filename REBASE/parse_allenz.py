#! /usr/bin/python

"""Parse allenz.txt file from the REBASE FTP server."""

import argparse
import re
import sys


TOTAL = 8
NAME, PROT, ORG, SRC, SITE, METH, COMM, REF = range(TOTAL)
TITLE = [
    "Name", "Prototype", "Organism", "Organism source", "Recognition site",
    "Methylation", "Commercial source", "References"
]


def main(argv=None):
    parser = argparse.ArgumentParser(
        description="Parse allenz.txt file from the REBASE FTP server."
    )
    parser.add_argument(
        "allenz", metavar="ALLENZ", type=argparse.FileType("r"),
        help="allenz.txt file from the REBASE FTP server"
    )
    parser.add_argument(
        "-o", dest="outsv", metavar="FILE", type=argparse.FileType("w"),
        default=sys.stdout, help="output file name, default STDOUT"
    )
    args = parser.parse_args(argv)
    with args.allenz as allenz:
        comm_dict = dict()
        while not allenz.readline().startswith("REBASE codes"):
            continue
        for line in allenz:
            line = line.strip()
            if line.startswith("<"):
                break
            elif line:
                comm, tag = line.split(None, 1)
                comm_dict[comm] = tag
        entries = []
        vals = [""] * TOTAL
        for line in allenz:
            m_line = re.match("<(\d)>(.*)", line)
            if m_line:
                key = int(m_line.group(1)) - 1
                value = m_line.group(2)
                vals[key] = value
                if key == REF:
                    entries.append(vals)
                    vals = [""] * TOTAL
            elif line.startswith("References:"):
                break
        ref_dict = dict()
        for line in allenz:
            line = line.strip()
            if line:
                index, ref = line.split(".", 1)
                ref_dict[index] = ref.strip()
    for vals in entries:
        vals[SITE] = vals[SITE].replace("^", "").strip("0123456789()-/N?")
        vals[COMM] = "; ".join(comm_dict[comm] for comm in vals[COMM])
        vals[REF] = "; ".join(
            ref_dict[ref] for ref in vals[REF].split(",")
        )
    with args.outsv as outsv:
        outsv.write("#:%s\n" % "\t".join(TITLE))
        for vals in sorted(entries):
            outsv.write("\t".join(vals) + "\n")


if __name__ == "__main__":
    sys.exit(main())

