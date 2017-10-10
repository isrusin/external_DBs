#! /usr/bin/env python

"""Filter NCBI list of prokaryotic genomes by status, length, etc."""

from __future__ import print_function
import argparse
import sys


def main(argv=None):
    parser = argparse.ArgumentParser(
        description="Filter input list of genomes by status, length, etc."
    )
    parser.add_argument(
        "intxt", metavar="FILE", type=argparse.FileType("r"),
        help="prokaryotes.txt file from the NCBI FTP server"
    )
    parser.add_argument(
        "status", metavar="STATUS", nargs="+",
        help="status to keep, you could replace spaces with '_'"
    )
    parser.add_argument(
        "-o", dest="outab", metavar="FILE", type=argparse.FileType("w"),
        default=sys.stdout, help="output tabular file, default STDOUT"
    )
    parser.add_argument(
        "--no-wgs", dest="no_wgs", action="store_true",
        help="do not include genomes that have WGS accession"
    )
    parser.add_argument(
        "--with-chromosomes", dest="with_chr", action="store_true",
        help="do not include genomes without chromosomes"
    )
    parser.add_argument(
        "--min-size", dest="min_size", metavar="SIZE", type=float,
        default=0, help="minimum genome size (Mb), default is 0 Mb"
    )
    args = parser.parse_args(argv)
    status = set([tag.replace("_", " ") for tag in args.status])
    with args.intxt as intxt, args.outab as outab:
        title = intxt.readline()
        columns = title.strip("\n#").split("\t")
        c_index = dict([(col, ind) for ind, col in enumerate(columns)])
        outab.write(title)
        for line in intxt:
            vals = line.strip().split("\t")
            project = vals[c_index["BioProject Accession"]]
            if vals[c_index["Status"]] not in status:
                continue
            if args.with_chr:
                repls = vals[c_index["Replicons"]]
                if repls == "-":
                    print(
                        "%s has no replicons, skipped" % project,
                        file=sys.stderr
                    )
                    continue
                for repl_tag in repls.split(";"):
                    seq_tag, acv_tag = repl_tag.strip().rsplit(":", 1)
                    if seq_tag.startswith("chromosome"):
                        break
                else:
                    print(
                        "%s has no chromosomes, skipped" % project,
                        file=sys.stderr
                    )
                    continue
            if args.no_wgs and vals[c_index["WGS"]] != "-":
                print(
                    "%s has WGS accession, skipped" % project,
                    file=sys.stderr
                )
                continue
            if float(vals[c_index["Size (Mb)"]]) < args.min_size:
                print(
                    "%s is too short, skipped" % project,
                    file=sys.stderr
                )
                continue
            outab.write(line)


if __name__ == "__main__":
    sys.exit(main())

