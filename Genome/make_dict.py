#! /usr/bin/env python

"""Make sequence ID to assembly AC dictionary."""

import argparse
import re
import sys


def message(msg, *args, **kwargs):
    level = kwargs.pop("level", "info")
    stream = kwargs.pop("stream", sys.stderr)
    stream.write(
        "%s: %s\n" % (level.capitalize(), msg.format(*args, **kwargs))
    )


def split_acvs(acv_str, no_versions):
    acvs = set()
    if acv_str:
        acvs = set(re.split(",|/", acv_str))
        if no_versions:
            acvs = set(acv.rsplit(".", 1)[0] for acv in acvs)
    return acvs


def print_mapping(oufile, mapping, **kwargs):
    metadata = kwargs.pop("metadata", None)
    compress = kwargs.pop("compress", False)
    inner_sep = kwargs.pop("inner_sep", ",")
    if kwargs:
        raise TypeError("unknown kwarg '%s'" % kwargs.popitem()[0])
    if metadata:
        oufile.write(metadata)
    if compress:
        temp_dict = dict()
        for key, value in mapping:
            temp_dict.setdefault(key, set()).add(value)
        mapping = (
            (k, inner_sep.join(v)) for k, v in temp_dict.iteritems()
        )
    for key, value in sorted(mapping):
        oufile.write("%s\t%s\n" % (key, value))
    oufile.write("##\n")


def main(argv=None):
    parser = argparse.ArgumentParser(
        description="Make sequence ID to assembly AC dictionary."
    )
    parser.add_argument(
        "intsv", metavar="GENOMES", type=argparse.FileType("r"),
        help="input TSV file with a list of genomes"
    )
    parser.add_argument(
        "-o", dest="oudct", metavar="FILE", type=argparse.FileType("w"),
        default=sys.stdout, help="output file, default STDOUT"
    )
    parser.add_argument(
        "--keep-versions", dest="no_versions", action="store_false",
        help="do not remove AC versions"
    )
    args = parser.parse_args(argv)
    no_versions = args.no_versions
    map_ac = set()
    map_wgs = set()
    with args.intsv as intsv:
        c_index = dict()
        asac_index = None
        chrs_index = None
        plms_index = None
        etc_index = None
        wgs_index = None
        for line in intsv:
            if line.startswith("#"):
                if line.startswith("#:"):
                    title = line.strip("\n#:").split("\t")
                    for i, column in enumerate(title):
                        c_index[column] = i
                    try:
                        asac_index = c_index["Assembly AC"]
                        chrs_index = c_index["Chromosomes"]
                        plms_index = c_index["Plasmids"]
                        etc_index = c_index["Other"]
                        wgs_index = c_index["WGS"]
                    except KeyError:
                        message("bad file format", level="error")
                        return 1
                continue
            if not c_index:
                message("data lines before title (#:)", level="error")
                return 1
            vals = line.strip().split("\t")
            asac = vals[asac_index]
            acs = split_acvs(vals[chrs_index], no_versions)
            acs |= split_acvs(vals[plms_index], no_versions)
            acs |= split_acvs(vals[etc_index], no_versions)
            for ac in acs:
                map_ac.add((ac, asac))
            wgs = vals[wgs_index]
            if wgs:
                if no_versions:
                    wgs = wgs.rstrip("0123456789.")
                map_wgs.add((wgs, asac))

    with args.oudct as oudct:
        ac_section_header = (
            "##Sequence AC{0} - assembly ACv subdict\n"
            "#:AC{0}\tAsACv\n"
        ).format("" if no_versions else "v")
        print_mapping(
            oudct, map_ac, compress=True, metadata=ac_section_header
        )
        wgs_section_header = (
            "##WGS AC{0} - assembly ACv subdict\n"
            "#:WGS{0}\tAsACv\n"
        ).format("" if no_versions else "v")
        print_mapping(
            oudct, map_wgs, compress=True, metadata=wgs_section_header
        )

if __name__ == "__main__":
    sys.exit(main())
