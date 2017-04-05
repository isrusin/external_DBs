#! /usr/bin/env python

"""Assign IDs for genomes from a list."""

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
        description="Generate enumerated list of complete genomes."
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
        "-I", dest="idtag", metavar="STUB", default="{}",
        help="ID stub, use {} as genome number placeholder; default '{}'"
    )
    parser.add_argument(
        "-o", dest="outab", metavar="FILE", type=argparse.FileType("w"),
        default=sys.stdout, help="output file, default STDOUT"
    )
    args = parser.parse_args(argv)
    idtag = args.idtag
    taxons = load_taxons(args.intax)
    with args.intab as intab, args.outab as outab:
        columns = intab.readline().strip("\n#").split("\t")
        index = dict((col, ind) for ind, col in enumerate(columns))
        outab.write(
            "Genome ID\tTaxID\tOrganism name\tChromosome ACs\t"
            "Plasmid ACs\tOther ACs\tTaxonomy (rank|taxid|name) ...\n"
        )
        num = 0
        for line in intab:
            vals = line.strip().split("\t")
            name = vals[index["Organism/Name"]]
            taxid = vals[index["TaxID"]]
            ouline = [idtag.format(num), taxid, name]
            taxonomy = []
            while taxid in taxons:
                parent, sname, rank = taxons[taxid]
                if taxonomy or rank == "species":
                    taxonomy.append("%s|%s|%s" % (rank, taxid, sname))
                taxid = parent
            if not taxonomy:
                print "%s has invalid taxID or no species, skipped!" % name
                continue
            chromosomes = set()
            plasmids = set()
            other = set()
            for tag in vals[index["Replicons"]].split("; "):
                seq_name, acv = tag.strip().split(":")
                if seq_name.startswith("chromosome"):
                    chromosomes.add(acv.strip("/"))
                elif seq_name.startswith("plasmid"):
                    plasmids.add(acv.strip("/"))
                else:
                    other.add(acv.strip("/"))
            ouline.append(",".join(sorted(chromosomes)))
            ouline.append(",".join(sorted(plasmids)))
            ouline.append(",".join(sorted(other)))
            ouline.extend(taxonomy)
            outab.write("\t".join(ouline) + "\n")
            num += 1
    print "%d genomes were enumerated." % num


if __name__ == "__main__":
    sys.exit(main())

