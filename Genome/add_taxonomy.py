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
            "#:Assembly AC\tTaxID\tOrganism name\tStatus\tWGS\t"
            "Chromosomes\tPlasmids\tOther\tTaxonomy (rank|taxid|name)\n"
        )
        num = 0
        for line in intab:
            vals = line.strip().split("\t")
            name = vals[index["Organism/Name"]]
            taxid = vals[index["TaxID"]]
            asac = vals[index["Assembly Accession"]]
            status = vals[index["Status"]].split(" ")[-1]
            wgs = vals[index["WGS"]].strip("-")
            ouline = [asac, taxid, name, status, wgs]
            taxonomy = []
            while taxid in taxons:
                parent, sname, rank = taxons[taxid]
                if taxonomy or rank == "species":
                    taxonomy.append("%s|%s|%s" % (rank, taxid, sname))
                taxid = parent
            if not taxonomy:
                print(
                    "Warning: assembly %s has invalid taxID" % asac,
                    "or no species, skipped!", file=sys.stderr
                )
                continue
            chromosomes = set()
            plasmids = set()
            other = set()
            replicons = vals[index["Replicons"]]
            if replicons != "-":
                for tag in replicons.split("; "):
                    if ":" not in tag:
                        print(
                            "Info: assembly %s contains replicon" % asac,
                            "'%s' without sequence AC." % tag,
                            file=sys.stderr
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
                print(
                    "Info: assembly %s has no replicons." % asac,
                    file=sys.stderr
                )
            ouline.append(",".join(sorted(chromosomes)))
            ouline.append(",".join(sorted(plasmids)))
            ouline.append(",".join(sorted(other)))
            ouline.extend(taxonomy)
            outab.write("\t".join(ouline) + "\n")
            num += 1
    print(
        "There are %d genomes in the resulted table." % num,
        file=sys.stderr
    )


if __name__ == "__main__":
    sys.exit(main())

