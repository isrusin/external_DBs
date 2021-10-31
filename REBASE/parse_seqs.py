#! /usr/bin/python

"""Parse REBASE sequence files."""

import argparse
import sys


def parse_EnzType(tag):
    tp = "-"
    act = ""
    put = "no"
    for tptag in tag.replace("/", " ").split(" "):
        if tptag == "putative":
            put = "yes"
        elif tptag in ["I", "II", "IIG", "III", "IV"]:
            tp = "Type " + tptag
        elif tptag == "homing":
            tp = "Homing"
            act = "R"
        elif tptag == "orphan":
            tp = "Orphan M"
        elif tptag == "restriction":
            act = "R"
        elif tptag == "methyltransferase":
            act += "M"
        elif tptag == "control":
            act = "C"
        elif tptag == "nicking":
            act = "V"
        elif tptag == "specificity":
            act = "S"
        elif tptag == "helicase":
            act = "H"
        elif tptag == "methyl-directed" and tp == "Type II":
            tp += "M"
    return tp, act, put


def add_entry(key, entry, entries):
    if key in entries:
        print "Note: repeated %s." % key
        old_entry = entries[key]
        for tag in old_entry.keys():
            if tag in entry and entry[tag] != old_entry[tag]:
                print "Warning: %s differ in %s!" % (key, tag)
                entry[tag] = old_entry[tag] + ";" + entry[tag]
        old_entry.update(entry)
    else:
        entries[key] = entry


def main(argv=None):
    parser = argparse.ArgumentParser(description="Parse REBASE seqs file.")
    parser.add_argument(
        "inseq", metavar="FASTA<", type=argparse.FileType("r"),
        help="input REBASE FastA (preformatted) file"
    )
    parser.add_argument(
        "outsv", metavar="TSV>", type=argparse.FileType("w"),
        help="output TSV file"
    )
    parser.add_argument(
        "ouseq", metavar="FASTA>", type=argparse.FileType("w"),
        help="output FastA file"
    )
    args = parser.parse_args(argv)
    entries = dict()
    with args.inseq as inseq:
        vals = dict()
        key = None
        seq = ""
        for line in inseq:
            if line.startswith(">"):
                if key:
                    vals["Seq"] = seq
                    add_entry(key, vals, entries)
                seq = ""
                vals = dict()
                nm = ""
                ac = ""
                for kv in line.strip("\n>").split("\t"):
                    k, v = kv.split(":", 1)
                    if k == "REBASE":
                        if "(" in v:
                            v, nm = v.split(" ")
                            nm = nm.strip("()")
                        else:
                            nm = v
                            v = "-"
                    elif k == "EnzType":
                        tp, v, put = parse_EnzType(v)
                        vals["SysType"] = tp
                        vals["Putative"] = put
                    vals[k] = v
                key = nm
            else:
                if "<>" in line:
                    line = line.replace("<>", "")
                seq += line.replace(" ", "")
        vals["Seq"] = seq
        add_entry(key, vals, entries)
    with args.ouseq as ouseq, args.outsv as outsv:
        outsv.write(
            "#:REBASE name\tSequence AC\tSystem type\tProtein type\t"
            "Recognition site\tLength\tLocus\tProtein ID\tUniprot AC\t"
            "GI\tPutative\tComplex name\n"
        )
        index = {
            "REBASE": 11, "EnzType": 3, "SysType": 2, "Putative": 10,
            "RecSeq": 4, "GenBank": 1, "SeqLength": 5, "Locus": 6,
            "ProteinId": 7, "UniProt": 8, "GI": 9
        }
        for nm, entry in sorted(entries.items()):
            vals = ["-"] * 12
            vals[0] = nm
            for key, value in entry.items():
                if key == "Seq":
                    ouseq.write(">%s\n%s\n" % (nm, value))
                else:
                    vals[index[key]] = value
            outsv.write("\t".join(vals) + "\n")


if __name__ == "__main__":
    sys.exit(main())

