#! /usr/bin/python

import argparse as ap

if __name__ == "__main__":
    parser = ap.ArgumentParser(
            description="Return genomes with specified status[es]."
            )
    parser.add_argument(
            "status", metavar="STATUS", nargs="+",
            help="status to return, replace spaces with '-'"
            )
    parser.add_argument(
            "-i", dest="intxt", required=True, type=ap.FileType("r"),
            help="input prokaryotes.txt file loaded from NCBI server"
            )
    parser.add_argument(
            "-o", dest="outab", required=True, type=ap.FileType("w"),
            help="output tabular file"
            )
    parser.add_argument(
            "--no-wgs", dest="no_wgs", action="store_true",
            help="do not include genomes that have WGS accession"
            )
    parser.add_argument(
            "--with-chromosomes", dest="with_chr", action="store_true",
            help="do not include genomes without chromosomes (INSDC)"
            )
    parser.add_argument(
            "--min-size", dest="min_size", type=float, default=0,
            help="minimum genome size (Mb), default is 0 Mb"
            )
    args = parser.parse_args()
    status = set([tag.replace("_", " ") for tag in args.status])
    with args.intxt as intxt, args.outab as outab:
        title = intxt.readline()
        columns = title.strip("\n#").split("\t")
        c_index = dict([(col, ind) for ind, col in enumerate(columns)])
        outab.write(title)
        for line in intxt:
            vals = line.strip().split("\t")
            bioproject = vals[c_index["BioProject Accession"]]
            if vals[c_index["Status"]] not in status:
                continue
            if args.with_chr and vals[c_index["Chromosomes/INSDC"]] == "-":
                print "%s has no INSDC chromosomes, skipped" % bioproject
                continue
            if args.no_wgs and vals[c_index["WGS"]] != "-":
                print "%s has WGS accession, skipped" % bioproject
                continue
            if float(vals[c_index["Size (Mb)"]]) < args.min_size:
                print "%s is too short, skipped" % bioproject
                continue
            outab.write(line)

