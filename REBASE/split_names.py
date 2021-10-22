#! /usr/bin/env python3

"""Split REBASE names by components."""

import argparse
import re
import sys


NAME_PATTERN = re.compile(
"""
    H- (?P<hybrid> .+) |
    (?:
        (?: (?P<homing> P?I|F)-)?
        (?: (?P<activity> (?P<ptypeII> S|R|RM|M|H|V|Nt|Nb|N|C) \d*)\.)?
        (?P<acronim> [a-zA-Z0-9]+?)
        (?P<index>
            [IVX]+ |
            (?: (?: ORF)? (?P<ptypeI>
                Mrr | McrA | McrB | McrC | Dam | Dcm | GmrS | GmrD |
                GmrSD | Dnmt | CMT | DRM | MET | DndA | DndB | DndC |
                DndD | DndE | DptF | DptG | DptH |
                SspB | SspC | SspD | SspF | SspG | SspH
            ) \d*b?) | # b? is for the only eukaryotic MTase MET2b
            (?: ORF [a-zA-Z0-9]+?)
        )?
        (?P<subunit> [A-Z])??
        (?P<predicted> P)?
        (?: -(?P<mutant> [^.]+) )?
        (?: \.(?P<unknown> .+) )?$
    )
""", re.X)

def main(argv=None):
    parser = argparse.ArgumentParser(description="Split REBASE names.")
    parser.add_argument(
        "inlist", metavar="LIST", type=argparse.FileType("r"),
        help="input list of REBASE names"
    )
    parser.add_argument(
        "-o", dest="oufile", metavar="FILE", type=argparse.FileType("w"),
        default=sys.stdout, help="output file, default is STDOUT"
    )
    args = parser.parse_args(argv)
    with args.inlist as inlist, args.oufile as oufile:
        oufile.write(
            "#:Name\tSystem\tAcronim\tIndex\tHybrid\tSubunit\tPredicted"
            "\tActivity\tHoming tag\tMutant\tUnknown\tProtein type (by name)\n"
        )
        for line in inlist:
            name = line.strip()
            name_match = NAME_PATTERN.match(name)
            if not name_match:
                print("Can't parse %s" % name)
                continue
            else:
                tags = name_match.groupdict("")
                homing_tag = tags["homing"]
                activity = tags["activity"]
                acronim = tags["acronim"]
                index = tags["index"]
                subunit = tags["subunit"]
                predicted = tags["predicted"]
                mutant_tag = tags["mutant"]
                hybrid = tags["hybrid"]
                unknown = tags["unknown"]
                ptype = tags["ptypeI"] or tags["ptypeII"] or "R/RM"
                if ptype == "Dcm": # Dcm could be either M or V
                    ptype = tags["ptypeII"] + "." + ptype
                if not index and subunit:
                    acronim += subunit
                    subunit = ""
                if hybrid:
                    homing_tag = "H"
                system = hybrid or acronim + index
                if homing_tag:
                    system = homing_tag + "-" + system
                if mutant_tag:
                    system += "-" + mutant_tag
                oufile.write("\t".join((
                    name, system, acronim, index, hybrid, subunit, predicted,
                    activity, homing_tag, mutant_tag, unknown, ptype
                )) + "\n")


if __name__ == "__main__":
    sys.exit(main())

