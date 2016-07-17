#! /usr/bin/python

import argparse as ap
import os

def update(wdir):
    gacvs = set()
    for name in os.listdir(wdir + "/gbk/"):
        gacvs.add(name.split(".gbk")[0])
    facvs = set()
    for name in os.listdir(wdir + "/fasta/"):
        facvs.add(name.split(".fasta")[0])
    acvs = list(gacvs.intersection(facvs))
    acvs.sort()
    with open(wdir + "/.acvs", "w") as ouacvs:
        ouacvs.write("\n".join(acvs) + "\n")
    print "%d records in database." % len(acvs)

if __name__ == "__main__":
    parser = ap.ArgumentParser(
            description="Updates list of loaded INSDC records (.acvs)."
            )
    parser.add_argument(
            "-s", "--source", dest="wdir", default=".",
            help="working folder"
            )
    args = parser.parse_args()
    update(args.wdir)

