#! /usr/bin/python

import argparse as ap

if __name__ == "__main__":
    parser = ap.ArgumentParser(
            description="Generate enumerated list of complete genome."
            )
    parser.add_argument(
            "-i", dest="intab", required=True, type=ap.FileType("r"),
            help="input tabular file with genomes"
            )
    parser.add_argument(
            "-t", dest="intax", metavar="taxonomy.tab", required=True,
            type = ap.FileType("r"), help="input taxonomy file"
            )
    parser.add_argument(
            "-o", dest="outab", required=True, type=ap.FileType("w"),
            help="output file"
            )
    args = parser.parse_args()
    taxons = dict()
    ptaxids = dict()
    with args.intax as intax:
        intax.readline()
        for line in intax:
            taxid, ptaxid, name, rank = line.strip().split("\t")
            taxons[taxid] = (name, rank)
            ptaxids[taxid] = ptaxid
    with args.intab as intab, args.outab as outab:
        columns = intab.readline().strip("\n#").split("\t")
        c_index = dict([(col, ind) for ind, col in enumerate(columns)])
        outab.write("GenomeID\tTaxID\tOrganism name\tChromosome ACs\t" +
                    "Plasmid ACs\tTaxonomy (rank|taxid|name) ...\n")
        num = 0
        for line in intab:
            vals = line.strip().split("\t")
            name = vals[c_index["Organism/Name"]]
            itaxid = taxid = vals[c_index["TaxID"]]
            if itaxid not in ptaxids:
                print "%s is not valid, %s is skipped!" % (taxid, name)
                continue
            l_acvs = set(vals[c_index["Chromosomes/INSDC"]].split(","))
            acvs = ",".join(sorted(l_acvs))
            s_acvs = set(vals[c_index["Plasmids/INSDC"]].split(","))
            s_acvs.discard("-")
            acvs += "\t" + ",".join(sorted(s_acvs))
            taxonomy = []
            ptaxid = ptaxids[itaxid]
            sname, rank = taxons[itaxid]
            while rank != "species":
                itaxid = ptaxid
                if itaxid not in ptaxids:
                    print "%s has no species, skipped!" % name
                    break
                ptaxid = ptaxids[itaxid]
                sname, rank = taxons[itaxid]
            else:
                while ptaxid in ptaxids:
                    taxonomy.append("%s|%s|%s" % (rank, itaxid, sname))
                    itaxid = ptaxid
                    ptaxid = ptaxids[itaxid]
                    sname, rank = taxons[itaxid]
                taxonomy.append("%s|%s|%s" % (rank, itaxid, sname))
                tax_str = "\t".join(taxonomy)
                outab.write("{}\t{}\t{}\t{}\t{}\n".format(num, taxid, name,
                                                          acvs, tax_str))
                num += 1
    print "%d genomes were enumerated." % num
