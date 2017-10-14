#! /usr/bin/env python

"""Parse REBASE Genomes index pages, return TSV file."""

from __future__ import print_function
import argparse
import re
import sys


ROW_PATTERN = re.compile(
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
    </tr>""",
    re.S | re.X
)


def parse_chunk(page_chunk):
    seqs = []
    for row_match in ROW_PATTERN.finditer(page_chunk):
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


def main(argv=None):
    parser = argparse.ArgumentParser(
        description="Parse index pages of REBASE Genomes."
    )
    parser.add_argument(
        "infile", metavar="INDEX", type=argparse.FileType("r"), nargs="+",
        help="REBASE Genomes index page"
    )
    parser.add_argument(
        "-o", dest="outab", metavar="FILE", type=argparse.FileType("w"),
        default=sys.stdout, help="output file, default STDOUT"
    )
    args = parser.parse_args(argv)
    files = args.infile
    cpl_seqs = []
    wgs_seqs = []
    for inhtml in files:
        with inhtml:
            html = inhtml.read().split("</legend>")
        name = inhtml.name
        if len(html) == 1:
            print(
                "Info: '%s' page is empty, skipped" % name,
                file=sys.stderr
            )
        elif len(html) == 2:
            tag = html[0].rstrip().rsplit(" ", 1)[-1]
            if tag == "Complete":
                print(
                    "Info: '%s' page has no 'WGS' section." % name,
                    file=sys.stderr
                )
                cpl_seqs.extend(parse_chunk(html[1]))
            elif tag == "WGS":
                print(
                    "Info: '%s' page has no 'Complete' section." % name,
                    file=sys.stderr
                )
                wgs_seqs.extend(parse_chunk(html[1]))
            else:
                print(
                    "Error: '%s' page is weird, skipped." % name,
                    file=sys.stderr
                )
        elif len(html) == 3:
            cpl_seqs.extend(parse_chunk(html[1]))
            wgs_seqs.extend(parse_chunk(html[2]))
        else:
            print(
                "Error: '%s' page has extra sections, skipped." % name,
                file=sys.stderr
            )
    with args.outab as outab:
        outab.write(
            "#:Genome type\tREBASE sequence ID\tREBASE genome ID\t" +
            "Bioproject ID\tOrganism name\tSequence length (Mb)\t" +
            "Genes number\tShotgun data\tM genes number\n"
        )
        for seq in cpl_seqs:
            outab.write("Complete\t%s\n" % "\t".join(seq))
        for seq in wgs_seqs:
            outab.write("WGS\t%s\n" % "\t".join(seq))


if __name__ == "__main__":
    sys.exit(main())

