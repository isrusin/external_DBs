#! /usr/bin/python

import argparse as ap
import gzip
import update_acvs_dump

def parse(ingbk, wdir):
    gbk_file = "%s/gbk/%s.gbk.gz"
    fasta_file = "%s/fasta/%s.fasta.gz"
    count = 0
    while True:
        count += 1
        title = ""
        acv = ""
        gi = ""
        de = ""
        date = ""
        for line in ingbk:
            title += line
            if line.startswith("LOCUS"):
                date = line.split()[-1]
            elif line.startswith("DEFINITION") or line.startswith(" "):
                de += line[11:-1] # + leading " ", - trailing "\n"
            elif line.startswith("VERSION"):
                acv, gi = line.split()[1:]
                gi = gi[3:]
                break
        else:
            break # EOF
        with gzip.open(gbk_file % (wdir, acv), "w", 5) as ougbk:
            ougbk.write(title)
            for line in ingbk:
                ougbk.write(line)
                if line.startswith("ORIGIN"):
                    ougbk.write("//\n")
                    break
                if line.startswith("//"):
                    print "%s record has no sequence!\n" % acv
                    break
        with gzip.open(fasta_file % (wdir, acv), "w", 5) as oufasta:
            oufasta.write(">gi|%s|gb|%s%s [%s]\n" % (gi, acv, de, date))
            for line in ingbk:
                if line.startswith("//"):
                    continue
                if line == "\n":
                    break
                oufasta.write(line[10:].replace(" ", ""))
        print "%d\t%s was loaded." % (count, acv)
    update_acvs_dump.update(wdir)

if __name__ == "__main__":
    parser = ap.ArgumentParser(
            description="Gets .gbk file with multiple records and " +
            "splits it into .gbk (without sequence) and .fasta files."
            )
    parser.add_argument(
            "ingbk", metavar="input.gbk", type=ap.FileType("r"),
            help="input .gbk file with multiple records"
            )
    parser.add_argument(
            "-s", "--source", dest="wdir", default=".",
            help="working folder"
            )
    args = parser.parse_args()
    with args.ingbk as ingbk:
        parse(ingbk, args.wdir)

