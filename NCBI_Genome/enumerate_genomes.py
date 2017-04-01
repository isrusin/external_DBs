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
            "Plasmid ACs\tTaxonomy (rank|taxid|name) ...\n"
        )
        num = 0
        for line in intab:
            vals = line.strip().split("\t")
            taxid = vals[index["TaxID"]]
            taxonomy = []
            while taxid in taxons:
                parent, sname, rank = taxons[taxid]
                if taxonomy or rank == "species":
                    taxonomy.append("%s|%s|%s" % (rank, taxid, sname))
                taxid = parent
            if not taxonomy:
                print "%s has invalid taxID or no species, skipped!" % name
                continue
            name = vals[index["Organism/Name"]]
            ouline = [idtag.format(num), taxid, name]
            acs = set(vals[index["Chromosomes/INSDC"]].split(","))
            ouline.append(",".join(sorted(acs)))
            acs = set(vals[index["Plasmids/INSDC"]].split(","))
            acs.discard("-")
            ouline.append(",".join(sorted(acs)))
            ouline.extend(taxonomy)
            outab.write("\t".join(ouline) + "\n")
            num += 1
    print "%d genomes were enumerated." % num


if __name__ == "__main__":
    sys.exit(main())

