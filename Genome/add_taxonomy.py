#! /usr/bin/env python

"""Add taxonomy to input table of genomes and reformat it."""

from __future__ import print_function
import argparse
import sys


def load_taxons(intax):
    taxons = dict()
    with intax:
        intax.readline()
        for line in intax:
            taxid, parent, name, rank = line.strip().split("\t")
            taxons[taxid] = (parent, name, rank)
    return taxons


def message(msg, *args, **kwargs):
    level = kwargs.pop("level", "info")
    stream = kwargs.pop("stream", sys.stderr)
    print(
        "%s: %s" % (level.capitalize(), msg.format(*args, **kwargs)),
        file=stream
    )


def main(argv=None):
    parser = argparse.ArgumentParser(
        description="Append taxonomy and reformat genomes table."
    )
    parser.add_argument(
        "intab", metavar="GENOMES", type=argparse.FileType("r"),
        help="tabular file with genomes"
    )
    parser.add_argument(
        "intax", metavar="TAXONS", type=argparse.FileType("r"),
        help="tabular file with taxons"
    )
    parser.add_argument(
        "-o", dest="outab", metavar="FILE", type=argparse.FileType("w"),
        default=sys.stdout, help="output file, default STDOUT"
    )
    args = parser.parse_args(argv)
    taxons = load_taxons(args.intax)
    with args.intab as intab, args.outab as outab:
        columns = intab.readline().strip("\n#").split("\t")
        index = dict((col, ind) for ind, col in enumerate(columns))
        outab.write(
            "#:Assembly AC\tStatus\tChromosomes\tPlasmids\tOther\tWGS\t"
            "Size, Mb\tTaxID\tOrganism name\tSpecies taxID\tSpecies name\t"
            "Full taxonomy |rank:taxid:name|\n"
        )
        num = 0
        for line in intab:
            vals = line.strip().split("\t")
            asac = vals[index["Assembly Accession"]]
            status = vals[index["Status"]].split(" ")[-1]
            wgs = vals[index["WGS"]].strip("-")
            size = vals[index["Size (Mb)"]]
            orid = taxid = vals[index["TaxID"]]
            name = vals[index["Organism/Name"]]
            spid = ""
            spname = ""
            taxonomy = []
            while taxid in taxons:
                parent, sname, rank = taxons[taxid]
                taxonomy.append(",".join([rank, taxid, sname]))
                if rank == "species":
                    spid = taxid
                    spname = sname
                taxid = parent
            if not taxonomy:
                message(
                    "assembly {} has invalid or outdated taxID, skipped",
                    asac, level="warning"
                )
                continue
            if not spid:
                message("assembly {} has no species", asac)
            chromosomes = set()
            plasmids = set()
            other = set()
            replicons = vals[index["Replicons"]]
            if replicons != "-":
                for tag in replicons.split("; "):
                    if ":" not in tag:
                        message(
                            "assembly {} contains replicon {} without "
                            "sequence AC", asac, tag
                        )
                        continue
                    seq_name, acv = tag.strip().split(":")
                    if seq_name.startswith("chromosome"):
                        chromosomes.add(acv.strip("/"))
                    elif seq_name.startswith("plasmid"):
                        plasmids.add(acv.strip("/"))
                    else:
                        other.add(acv.strip("/"))
            else:
                message("assembly {} has no replicons", asac)
            ouline = [
                asac, status,
                ",".join(sorted(chromosomes)),
                ",".join(sorted(plasmids)),
                ",".join(sorted(other)),
                wgs, size, orid, name, spid, spname,
                "|".join(taxonomy)
            ]
            outab.write("\t".join(ouline) + "\n")
            num += 1
    message("{} genomes in the resulted table", num, level="summary")


if __name__ == "__main__":
    sys.exit(main())

