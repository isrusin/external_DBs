#! /usr/bin/python

import argparse as ap

def find_acs(sgpath, nm, acs, gid):
    with open(sgpath.format(nm)) as inhtml:
        sgpage = inhtml.read()
    if sgpage == "<br><br>None found.<br><br>\n":
        print "Warning: %s (%s) seqget page is empty." % (nm, gid)
        return None
    for chunk in sgpage.split("TABLE"):
        if "Genbank Notes:" in chunk:
            found_acs = []
            for ac in acs:
                if ac.endswith("00000000"):
                    if ">"+ac.strip("0") in chunk or ">"+ac in chunk:
                        found_acs.append(ac)
                elif ac in chunk:
                    found_acs.append(ac)
            return found_acs
    else:
        print "Warning: %s seqget page has no Genbank section." % nm
        return None

if __name__ == "__main__":
    parser = ap.ArgumentParser(description="Solve REBASE summary pages.")
    parser.add_argument(
            "inpath", metavar="UNFINISHED_PATH",
            help="unfinished summaries path, use {} placeholder for gid"
            )
    parser.add_argument(
            "sgpath", metavar="SEQGET_PATH",
            help="seqget pages path, use {} placeholder for R-M name"
            )
    parser.add_argument(
            "-l", metavar="IN_GIDS", dest="ingids", type=ap.FileType("r"),
            required=True, help="input list unfinished genome IDs"
            )
    parser.add_argument(
            "-a", metavar="OUT_SUMS", dest="outab", type=ap.FileType("a"),
            required=True, help="output file with summaries (appending)"
            )
    args = parser.parse_args()
    with args.ingids as ingids:
        gids = sorted(ingids.read().strip().split("\n"))
    with args.outab as outab:
        for gid in gids:
            with open(args.inpath.format(gid)) as insmr:
                acs = dict()
                wgsacs = []
                line = insmr.readline()
                while line.startswith("#Sequence:"):
                    etc, ac, tag = line.strip().split("\t")
                    if ac.endswith("00000000"):
                        wgsacs.append(ac)
                    dnas = acs.get(tag, [])
                    dnas.append(ac)
                    acs[tag] = dnas
                    line = insmr.readline()
                enz_dict = dict()
                wgsnms = set()
                while line:
                    tag = line.strip("\n\t\r#")
                    line = insmr.readline()
                    tag_nms = set()
                    while line and not line.startswith("#"):
                        tp, nm, enz = line.strip().split("\t", 2)
                        if nm in tag_nms:
                            wgsnms.add(nm)
                        tag_nms.add(nm)
                        enzs = enz_dict.get((nm, tag), [])
                        enzs.append((tp, enz))
                        enz_dict[(nm, tag)] = enzs
                        line = insmr.readline()
                for (nm, tag), enzs in enz_dict.items():
                    if nm in wgsnms and len(wgsacs) == 1:
                        for (tp, enz) in enzs:
                            outab.write("\t".join([gid, wgsacs[0], tp,
                                                   nm, enz]) + "\n")
                        continue
                    dnas = find_acs(args.sgpath, nm, acs[tag], gid)
                    if not dnas:
                        continue
                    if len(dnas) == len(enzs):
                        for ac, (tp, enz) in zip(dnas, enzs):
                            outab.write("\t".join([gid, ac, tp,
                                                   nm, enz]) + "\n")
                    else:
                        print "Error: %s ACs for %s disagree!" % (gid, nm)

