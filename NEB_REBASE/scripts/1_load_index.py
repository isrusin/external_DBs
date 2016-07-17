#! /usr/bin/python

from argparse import ArgumentParser
from httplib import HTTPConnection

pages = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"

if __name__ == "__main__":
    parser = ArgumentParser(description="Load REBASE genomes pages.")
    parser.add_argument(
            "oupath", metavar="DIR",
            help="output folder or path with {} placeholder"
            )
    args = parser.parse_args()
    oupath = args.oupath
    if "{" not in oupath:
        oupath += "/{}.html"
    conn = HTTPConnection("tools.neb.com")
    address = "/genomes/index.php?page=%s"
    for letter in pages:
        conn.request("GET", address % letter)
        resp = conn.getresponse()
        with open(oupath.format(letter), "w") as ouhtml:
            ouhtml.write(resp.read())
        print "%s page was loaded." % letter
    conn.close()

