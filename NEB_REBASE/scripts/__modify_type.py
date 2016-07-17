#! /usr/bin/python

import argparse as ap

if __name__ == "__main__":
    parser = ap.ArgumentParser(
            description="Modify R-M system Type with subtype symbol."
            )
    parser.add_argument(
            "iotab", metavar="TARGET.tab", type=ap.FileType("r"),
            help="target tabular file to modify Type in"
            )
    parser.add_argument(
            "-n", dest="innms", metavar="IN_LIST.nms", required=True,
            type=ap.FileType("r"), help="output file, default is stdout"
            )
    parser.add_argument(
            "--subtype", dest="stype", metavar="SYMBOL", required=True,
            help="symbol of subtype to add"
            )
    parser.add_argument(
            "--name-column", dest="name_index", metavar="N", default=3,
            type=int, help="name column index, default is 3"
            )
    parser.add_argument(
            "--type-column", dest="type_index", metavar="N", default=2,
            type=int, help="type column index, default is 2"
            )
    args = parser.parse_args()
    out_str = ""
    with args.innms as innms:
        nms = set(innms.read().strip().split("\n"))
    with args.iotab as intab:
        for line in intab:
            vals = line.strip().split("\t")
            if vals[args.name_index] in nms:
                vals[args.type_index] += args.stype
                line = "\t".join(vals) + "\n"
            out_str += line
    with open(args.iotab.name, "w") as outab:
        outab.write(out_str)

