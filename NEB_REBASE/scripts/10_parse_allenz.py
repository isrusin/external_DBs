#! /usr/bin/python

import argparse as ap
import re

if __name__ == "__main__":
    parser = ap.ArgumentParser(
            description="Parse allenz.txt file from REBASE ftp server."
            )
    parser.add_argument(
            "allenz", metavar="ALLENZ.txt", type=ap.FileType("r"),
            help="allenz.txt file"
            )
    parser.add_argument(
            "-o", dest="outab", type=ap.FileType("w"), required=True,
            help="output file name"
            )
    args = parser.parse_args()
    with args.allenz as allenz, args.outab as outab:
        refs_dict = dict()
        comms_dict = dict()
        entries = []
        while not allenz.readline().startswith("REBASE codes"):
            continue
        for line in allenz:
            line = line.strip()
            if line.startswith("<"):
                break
            elif line:
                comm, tag = line.split(" ", 1)
                comms_dict[comm] = tag.strip()
        vals = [""] * 8
        for line in allenz:
            m_line = re.match("<(\d)>(.*)", line)
            if m_line:
                key = int(m_line.group(1))
                value = m_line.group(2)
                vals[key-1] = value
                if key == 8:
                    entries.append(vals)
                    vals = [""] * 8
            elif line.startswith("References:"):
                break
        for line in allenz:
            line = line.strip()
            if line:
                index, ref = line.split(".", 1)
                refs_dict[index] = ref.strip()
        for vals in entries:
            vals[5-1] = vals[5-1].replace("^", "").strip(
                    "0123456789()-/N?"
                    )
            vals[7-1] = "; ".join([comms_dict[comm] for comm in vals[7-1]])
            vals[8-1] = "; ".join([
                    refs_dict[ref] for ref in vals[8-1].split(",")
                    ])
        entries.sort()
        outab.write(
                "Name\tPrototype\tOrganism\tOrganism source\t" +
                "Recognition site\tMethylation site\tCommercial " +
                "source\tReferences\n"
                )
        for vals in entries:
            outab.write("\t".join(vals)+"\n")

