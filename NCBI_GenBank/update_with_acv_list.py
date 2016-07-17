#! /usr/bin/python

import argparse as ap
import urllib2
import urllib

import parse_multiple_record_gbk

def load_acvs(inacvs):
    with inacvs:
        return set(inacvs.read().strip().split("\n"))

def update(inacvs, wdir):
    acvs = load_acvs(inacvs) - load_acvs(open(wdir + "/.acvs", "r"))
    acvs = list(acvs)
    acvs.sort()
    print "%d ACVs are missed." % len(acvs)
    params = urllib.urlencode({"db": "nuccore", "rettype": "gbwithparts",
                               "retmode": "text", "id": ",".join(acvs)})
    req = urllib2.Request(
            "http://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi",
            params, {"User-agent": "Mozilla"}
            )
    resp = urllib2.urlopen(req)
    parse_multiple_record_gbk.parse(resp, wdir)
    resp.close()

if __name__ == "__main__":
    parser = ap.ArgumentParser(
            description="Upload missed gbk/fasta files by INSDC ACv list."
            )
    parser.add_argument(
            "inacvs", metavar="input.acvs", type=ap.FileType("r"),
            help="input list of INSDC ACVs"
            )
    parser.add_argument(
            "-s", "--source", dest="wdir", default=".",
            help="working folder"
            )
    args = parser.parse_args()
    update(args.inacvs, args.wdir)

