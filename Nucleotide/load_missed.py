#! /usr/bin/env python

"""Load missed NCBI Nucleotide entries through efetch request.

* Get list of missed ACs.
* Send a request to Entrez Fetch util.
* Split the uploaded GenBank Flatfile by entries, save sequences in
separate Fasta files; gzip everything.
"""

from __future__ import print_function
import argparse
import gzip
import os
import socket
import sys
import urllib2
import urllib


def check_wdir(wdir):
    gbk_dir = "%s/gbk" % wdir
    if not os.path.exists(gbk_dir):
        os.makedirs(gbk_dir)
    fasta_dir = "%s/fasta" % wdir
    if not os.path.exists(fasta_dir):
        os.makedirs(fasta_dir)
    return os.path.isdir(gbk_dir) and os.path.isdir(fasta_dir)


def get_missed(inacvs, wdir, verbose=True):
    acvs = set()
    with inacvs:
        acvs.update(inacvs.read().split())
    try:
        with open("%s/.acv" % wdir) as dump:
            loaded = set(dump.read().split())
            loaded_acs = set()
            for acv in loaded:
                ac = acv.split(".")[0]
                loaded_acs.add(ac)
            loaded.update(loaded_acs)
            acvs.difference_update(loaded)
    except IOError:
        pass
    if verbose:
        print("%d AC(v)s are missed." % len(acvs), file=sys.stderr)
    return sorted(acvs)


def request_efetch(acvs):
    socket.setdefaulttimeout(300)
    email = "%s@%s" % (os.getlogin(), socket.gethostname())
    post_args = urllib.urlencode({
        "db": "nuccore", "rettype": "gbwithparts", "retmode": "text",
        "email": email, "id": ",".join(acvs)
    })
    req = urllib2.Request(
        "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi",
        post_args, {"Content-Type": "application/x-www-form-urlencoded",
                    "User-Agent": "Firefox"}
    )
    return urllib2.urlopen(req)


def parse_gbk(ingbk, wdir, verbose=True):
    gbk_path = "%s/gbk/%s.gbk.gz"
    fasta_path = "%s/fasta/%s.fasta.gz"
    count = 0
    while True:
        count += 1
        header = ""
        acv = ""
        de = ""
        for line in ingbk:
            header += line
            if line.startswith("DEFINITION") or line.startswith(" "):
                de += line[11:-1] # + leading " ", - trailing "\n"
            elif line.startswith("VERSION"):
                acv = line.split()[1]
                break
        else:
            break # EOF
        with gzip.open(gbk_path % (wdir, acv), "w", 5) as ougbk:
            ougbk.write(header)
            for line in ingbk:
                ougbk.write(line)
                if line.startswith("ORIGIN"):
                    ougbk.write("//\n")
                    break
                if line.startswith("//"):
                    if verbose:
                        print(
                            "%s record has no sequence!\n" % acv,
                            file=sys.stderr
                        )
                    break
        with gzip.open(fasta_path % (wdir, acv), "w", 5) as oufasta:
            oufasta.write(">%s%s\n" % (acv, de))
            for line in ingbk:
                if line.startswith("//"):
                    continue
                if line == "\n":
                    break
                oufasta.write(line[10:].replace(" ", ""))
        if verbose:
            print(
                "%d\t%s was loaded." % (count, acv),
                file=sys.stderr
            )


def update_dump(wdir, verbose=True):
    gacvs = set()
    for name in os.listdir(wdir + "/gbk/"):
        gacvs.add(name.split(".gbk")[0])
    facvs = set()
    for name in os.listdir(wdir + "/fasta/"):
        facvs.add(name.split(".fasta")[0])
    acvs = list(gacvs.intersection(facvs))
    acvs.sort()
    with open(wdir + "/.acv", "w") as ouacvs:
        ouacvs.write("\n".join(acvs) + "\n")
    if verbose:
        print(
            "%d records in the database." % len(acvs),
            file=sys.stderr
        )


def main(argv=None):
    parser = argparse.ArgumentParser(
        description="""Load missed NCBI Nucleotide entries."""
    )
    parser.add_argument(
        "inacvs", metavar="LIST", type=argparse.FileType("r"),
        help="input file with whitespace-separated list of ACs"
    )
    parser.add_argument(
        "-s", "--source", dest="wdir", metavar="DIR", default=".",
        help="working folder"
    )
    args = parser.parse_args(argv)
    wdir = args.wdir
    if not check_wdir(wdir):
        parser.error("bad working folder (-s option)")
    acvs = get_missed(args.inacvs, wdir)
    resp = request_efetch(acvs)
    parse_gbk(resp, wdir)
    resp.close()
    update_dump(wdir)


if __name__ == "__main__":
    sys.exit(main())

