#! /usr/bin/python

import argparse as ap
import re

rsite_p = re.compile(
    r"""
      (?:
        (?P<seq>  [A-Z]+ | \? ), \s
        (?P<rst>  -? \d+ | \? );
      )
      (?: \s
        (?P<cseq> [A-Z]+      ), \s
        (?P<crst> -? \d+ | \? );
      )?
    """, re.S | re.X
)
msite_p = re.compile(
    r"""
      (?:
        (?P<mst>  -? \d+ | \? ) \(
        (?P<mtp>  N?[4-6]m[AC] | \? ) \)
      )
      (?: ,
        (?P<cmst>  -? \d+ | \? ) \(
        (?P<cmtp>  N?[4-6]m[AC] | \? ) \)
      )?;
    """, re.S | re.X
)
act_tags = {
        "M": ("Orphan M", "M"), "M1": ("I", "M"),
        "M2": ("II", "M"), "M3": ("III", "M"),
        "R1": ("I", "R"), "R2": ("II", "R"),
        "R2*": ("IIM", "R"), "R3": ("III", "R"),
        "RM1": ("I", "RM"), "RM2": ("IIG", "RM"),
        "IE": ("Homing", "R")
        }

if __name__ == "__main__":
    parser = ap.ArgumentParser(
            description="Parses bairoch.txt file from REBASE ftp server."
            )
    parser.add_argument(
            "intxt", metavar="BAIROCH.txt", type=ap.FileType("r"),
            help="bairoch.txt file"
            )
    parser.add_argument(
            "-o", dest="outab", type=ap.FileType("w"), required=True,
            help="output file name"
            )
    args = parser.parse_args()
    with args.intxt as intxt, args.outab as outab:
        refs_dict = dict()
        coms_dict = dict()
        entries = []
        outab.write(
                "Name\tType\tActivity\tAccession\tOrganism\tPrototype\t" +
                "Recognition site\tRestriction site\tMethylation site\t" +
                "Methylation type\tCommercial source\tReferences\n"
                )
        line = intxt.readline().strip()
        while line.startswith("CC"):
            if line.endswith(")"):
                com, tag = line[5:].split("=", 1)
                coms_dict[com] = tag
            line = intxt.readline().strip()
        nm = tp = act = rac = org = ptp = st = rst = com = ref = ""
        mst = mtp = "?"
        for line in intxt:
            line = line.strip("\n")
            if line.startswith("ID"):
                nm = line.split()[-1]
            elif line.startswith("ET"):
                tp, act = act_tags[line.split()[-1]]
            elif line.startswith("AC"):
                rac = line.split()[-1][:-1]
            elif line.startswith("OS"):
                org = line[5:]
            elif line.startswith("PT"):
                ptp = line.split()[-1]
            elif line.startswith("RS"):
                rsite_m = rsite_p.match(line[5:])
                st = rsite_m.group("seq")
                rst = rsite_m.group("rst")
                if rsite_m.group("crst"):
                    rst += ", " + rsite_m.group("crst")
            elif line.startswith("MS"):
                msite_m = msite_p.match(line[5:])
                mst = msite_m.group("mst")
                if msite_m.group("cmst"):
                    mst += ", " + msite_m.group("cmst")
                mtp = msite_m.group("mtp")
                if msite_m.group("cmtp"):
                    mtp += ", " + msite_m.group("cmtp")
            elif line.startswith("CR"):
                com = "; ".join([coms_dict[key] for key in line[5:-1]])
            elif line.startswith("RN"):
                if line[5:] != "[1]":
                    ref = ref[:-1] + "; "
            elif line.startswith("RA"):
                ref += line[5:]
            elif line.startswith("RL"):
                ref = ref[:-1] + " " + line[5:]
            elif line.startswith("//"):
                outab.write("\t".join([
                        nm, tp, act, rac, org, ptp, st, rst,
                        mst, mtp, com, ref
                        ]) + "\n")
                nm = tp = act = rac = org = ptp = st = rst = com = ref = ""
                mst = mtp = "?"

