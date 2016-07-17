#! /usr/bin/python

import argparse as ap

def parse_EnzType(tag):
    tp = "-"
    act = ""
    put = "no"
    for tptag in v.replace("/", " ").split(" "):
        if tptag == "putative":
            put = "yes"
        elif tptag in ["I", "II", "IIG", "III", "IV"]:
            tp = "Type "+tptag
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

if __name__ == "__main__":
    parser = ap.ArgumentParser(description="Parse REBASE seqs file.")
    parser.add_argument(
            "inseq", metavar="IN_SEQS.txt", type=ap.FileType("r"),
            help="input REBASE fasta (preformated) file"
            )
    parser.add_argument(
            "outab", metavar="OUT.tab", type=ap.FileType("w"),
            help="output tabular file"
            )
    parser.add_argument(
            "ouseq", metavar="OUT.fasta", type=ap.FileType("w"),
            help="output fasta file"
            )
    args = parser.parse_args()
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
                seq += line.replace(" ", "")
        vals["Seq"] = seq
        add_entry(key, vals, entries)
    with args.ouseq as ouseq, args.outab as outab:
        outab.write(
                "REBASE name\tGenBank AC\tR-M system type\t" +
                "Protein type\tRecognition site\tLength\tLocus\t" +
                "ProteinID\tUniprot AC\tGI\tPutative\tComplex name\n"
                )
        index = {"REBASE": 11, "EnzType": 3, "SysType": 2, "Putative": 10,
                 "RecSeq": 4, "GenBank": 1, "SeqLength": 5, "Locus": 6,
                 "ProteinId": 7, "UniProt": 8, "GI": 9}
        for nm, entry in sorted(entries.items()):
            vals = ["-"] * 12
            vals[0] = nm
            for k, v in entry.items():
                if k == "Seq":
                    ouseq.write(">%s\n%s\n" % (nm, v))
                else:
                    vals[index[k]] = v
            outab.write("\t".join(vals) + "\n")

