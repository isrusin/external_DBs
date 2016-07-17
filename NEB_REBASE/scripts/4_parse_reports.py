#! /usr/bin/python

import argparse as ap
import re

tag_p = re.compile(r"<p>Sequence name: (?P<tag>.+?)</p>", re.S)
row_p = re.compile(
    r"""<tr[^<]+
      <td \s class="repo_orfs_td"> (?P<type>.*?) </td> \s* # R-M type
      <td \s class="repo_orfs_td"> (?P<act>.*?) </td> \s* # activity
      <td \s class="repo_orfs_td"> (?P<name>.*?) </td> \s* # name
      <td \s class="repo_orfs_td"> (?P<site>.*?) </td> \s* # site
      <td \s class="repo_orfs_td"> (?P<ctg>.*?) </td> \s* # contig
      <td \s class="repo_orfs_td"> (?P<crd>.*?) </td> \s* # coords
    </tr>""", re.S | re.X
)

if __name__ == "__main__":
    parser = ap.ArgumentParser(description="Parse REBASE report pages.")
    parser.add_argument(
            "inpath", metavar="REPORT_DIR",
            help="input folder or path with {} placeholder"
            )
    parser.add_argument(
            "-l", dest="ingids", metavar="LIST.gids", required=True,
            type=ap.FileType("r"), help="list of REBASE genome IDs"
            )
    parser.add_argument(
            "-o", dest="outab", metavar="FILE", required=True,
            type=ap.FileType("w"), help="output file"
            )
    args = parser.parse_args()
    with args.ingids as ingids:
        gids = sorted(ingids.read().strip().split("\n"))
    with args.outab as outab:
        outab.write(
                "REBASE genome ID\tSequence tag\tR-M system type\t" +
                "Gene type\tREBASE name\tRecognition site\tContig\t" +
                "Coordinates\n"
                )
        for gid in gids:
            with open(args.inpath.format(gid)) as inhtml:
                html = inhtml.read().split('"repo_orfs"')
            if len(html) == 1:
                print "Note: %s is empty." % gid
                continue
            tags = set()
            for i in range(1, len(html)):
                tag_m = tag_p.search(html[i-1])
                tag = tag_m.group("tag") if tag_m else ""
                tags.add(tag)
                for row_m in row_p.finditer(html[i]):
                    tp = row_m.group("type").replace("<br />", " ")
                    act = row_m.group("act")
                    nm = row_m.group("name")
                    st = row_m.group("site").strip()
                    if "not in REBASE" in st:
                        st = "not in REBASE"
                    ctg = row_m.group("ctg")
                    crd = row_m.group("crd").replace("&nbsp;", " ")
                    outab.write("\t".join([gid, tag, tp, act, nm,
                                           st, ctg, crd]) + "\n")
            if len(tags) != len(html) - 1:
                print "Warning: %s with repeated sequence tags!" % gid

