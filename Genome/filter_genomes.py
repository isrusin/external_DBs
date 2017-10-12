#! /usr/bin/env python

"""Filter a list of prokaryotic genomes by status, length, etc."""

from __future__ import print_function
import argparse
import sys


def message(msg, *args, **kwargs):
    level = kwargs.pop("level", "info")
    stream = kwargs.pop("stream", sys.stderr)
    print(
        "%s: %s" % (level.capitalize(), msg.format(*args, **kwargs)),
        file=stream
    )


def main(argv=None):
    parser = argparse.ArgumentParser(
        description="Filter input list of genomes by status, length, etc."
    )
    parser.add_argument(
        "intsv", metavar="FILE", type=argparse.FileType("r"),
        help="a list of genomes with taxonomy"
    )
    parser.add_argument(
        "status", metavar="STATUS", nargs="+",
        choices={"Contig", "Scaffold", "Chromosome", "Genome"},
        help="status to keep; any of 'Contig', 'Scaffold', 'Chromosome', "
        "and 'Genome'"
    )
    parser.add_argument(
        "-o", dest="outsv", metavar="FILE", type=argparse.FileType("w"),
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
        "--with-species", dest="with_sp", action="store_true",
        help="do not include genomes without species"
    )
    parser.add_argument(
        "--min-size", dest="min_size", metavar="SIZE", type=float,
        default=0, help="minimum genome size (Mb), default is 0 Mb"
    )
    args = parser.parse_args(argv)
    statuses = set(args.keep_status)
    with args.intsv as intsv, args.outsv as outsv:
        title = intsv.readline()
        outsv.write(title)
        columns = title.strip("\t#: ").split("\t")
        c_index = dict([(col, ind) for ind, col in enumerate(columns)])
        for line in intxt:
            vals = line.strip().split("\t")
            asac = vals[c_index["Assembly AC"]]
            if vals[c_index["Status"]] not in statuses:
                message("{} has bad status, skipped", asac)
                continue
            if args.with_chr and not vals[c_index["Chromosomes"]]:
                message("{} has no chromosomes, skipped", asac)
                continue
            if args.with_sp and not vals[c_index["Species taxID"]]:
                message("{} has no species, skipped", asac)
                continue
            if args.no_wgs and vals[c_index["WGS"]]:
                message("{} has WGS accession, skipped", asac)
                continue
            if float(vals[c_index["Size, Mb"]]) < args.min_size:
                message("{} is too short, skipped", asac)
                continue
            outsv.write(line)


if __name__ == "__main__":
    sys.exit(main())

