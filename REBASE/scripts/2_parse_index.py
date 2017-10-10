#! /usr/bin/python

import argparse as ap
import re

pages = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"

row_pattern = re.compile(
        r"""<tr[^<]+
          <td[^>]*> \s*
            <a \s name="sq (?P<sid>\d+) "> \s* </a> \s* # sequence ID
           (<a \s name="gn (?P<gid>\d+) "> \s* </a> \s*)? # ?genome ID
            <a \s* ([^\d>]+ ((?P<pid>\d+) ")?)? > \s* # ?bioproject ID
              <i> (?P<sp>[^<]+) </i> (?P<st>[^<]*) # species, strain
            </a> \s*
          </td> \s*
          <td[^>]*> (?P<slen>[^<]*) </td> \s* # sequence length
          <td[^>]*> (?P<gnum>[^<]*) </td> \s* # genes number
          <td[^>]*>  (?P<sgun>.+?)  </td> \s* # shotgun data
          <td[^>]*>  (?P<mnum>.+?)  </td> \s* # M genes number
         (<td[^>]*> .+? </td> \s*)?
        </tr>""", re.S | re.X
        )

def parse_chunk(page_chunk):
    seqs = []
    for row_match in row_pattern.finditer(page_chunk):
        sid = row_match.group("sid")
        gid = row_match.group("gid") or gid
        pid = row_match.group("pid") or "-"
        sp = row_match.group("sp")
        st = row_match.group("st").strip()
        nm = sp
        if st:
            nm += " " + st
        slen = row_match.group("slen")
        gnum = row_match.group("gnum")
        sgun = row_match.group("sgun")
        if sgun.endswith("</a>"): # loss of information!
            sgun = "yes"
        mnum = row_match.group("mnum")
        if mnum == "<i>- no RM systems -</i>":
            mnum = "no RMs"
        seqs.append((sid, gid, pid, nm, slen, gnum, sgun, mnum))
    return seqs

if __name__ == "__main__":
    parser = ap.ArgumentParser(description="Parse REBASE genomes pages.")
    parser.add_argument(
            "inpath", metavar="INDIR",
            help="input folder or path with {} placeholder"
            )
    parser.add_argument(
            "-o", dest="outab", required=True, type=ap.FileType("w"),
            help="output file"
            )
    args = parser.parse_args()
    inpath = args.inpath
    if "{" not in inpath:
        inpath += "/{}.html"
    cpl_seqs = []
    wgs_seqs = []
    for letter in pages:
        print "Parsing %s page." % letter
        with open(inpath.format(letter)) as inhtml:
            html = inhtml.read().split("</legend>")
        if len(html) == 1:
            print "Note: %s page is empty, skipped" % letter
        elif len(html) == 2:
            tag = html[0].rstrip().rsplit(" ", 1)[-1]
            if tag == "Complete":
                print "Note: %s page has no 'WGS' section." % letter
                cpl_seqs.extend(parse_chunk(html[1]))
            elif tag == "WGS":
                print "Note: %s page has no 'Complete' section." % letter
                wgs_seqs.extend(parse_chunk(html[1]))
            else:
                print "Error: %s page is weird, skipped." % letter
        elif len(html) == 3:
            cpl_seqs.extend(parse_chunk(html[1]))
            wgs_seqs.extend(parse_chunk(html[2]))
        else:
            print "Error: %s page has extra sections, skipped." % letter
    with args.outab as outab:
        outab.write(
                "Genome type\tREBASE sequence ID\tREBASE genome ID\t" +
                "Bioproject ID\tOrganism name\tSequence length (Mb)\t" +
                "Genes number\tShotgun data\tM genes number\n"
                )
        for seq in cpl_seqs:
            outab.write("Complete\t%s\n" % "\t".join(seq))
        for seq in wgs_seqs:
            outab.write("WGS\t%s\n" % "\t".join(seq))

