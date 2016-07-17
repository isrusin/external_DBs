#! /usr/bin/python

import argparse as ap
import re

sum_p = re.compile(
    r"""
      <p>REBASE \s ref \s \# \s (?P<ref>\d+)?</p> \s* # reference (anchor)
      (?P<dnas>.+) # sequences description
      <p>REBASE \s acronym: \s (?P<acro>[^<]+)?</p> \s* # acronym (anchor)
      <p>Org_num: \s (?P<num>\d+)?</p> .+? # REBASE organism ID
      <table \s class="repo_orfs">(?P<rms>.+?)</table> # ORFs description
    """, re.S | re.X
)
multi_p = re.compile(
    r"""
      <tr> \s*
        <td[^>]*> (?P<tag>[^:]+) :</td> \s* # sequence tag
        <td[^>]*> (?P<len>[^<]*) </td> \s* # sequence length
        <td[^>]*> (?P<acc>[^<]+) </td> \s* # accession
      </tr>
    """, re.S | re.X
)
single_p = re.compile(
    r"""
      (<p>(?P<tag>[^:]+): \s # sequence tag
      (?P<len>[1-9][0-9,]* \s bp)</p> \s*)? # sequence length
      <p>[^:]+: \s (?P<acc>[^<]+)</p> # accession
    """, re.S | re.X
)
tr_p = re.compile(r"<tr[^>]*>(?P<tr>.*?)</tr>", re.S)
type_p = re.compile(
    r"""
      <th[^>]*>
        (?P<sys> (?:Type\s[IV]+) | (?:Orphan\sM) | (?:Homing))
      </th>
    """, re.S | re.X
)
tag_p = re.compile(r"<td[^>]*><i>(?P<tag>[^<]+)</i></td>", re.S)
rm_p = re.compile(
    r"""
      <td[^>]*>(?P<locus>(?:\d+)|(?:\?{3})) \s* </td> \s* # locus
      <td[^>]*>(?P<type>RM?|M|S|C|V)</td> \s* # protein type
      <td[^>]*>(?P<sim>[^<]+)</td> \s* # most similar protein
      <td[^>]*>(?P<seq>.+?)</td> \s* # recognition sequence
      <td[^>]*>(?P<name>[-.A-Za-z0-9]+) \s* </td> # REBASE protein name
    """, re.S | re.X
)

def parseEnzRow(tp, rm_m):
    site = rm_m.group("seq").strip()
    if "not in REBASE" in site:
        site = "not in REBASE"
    return "\t".join([tp, rm_m.group("name"), rm_m.group("type"), site,
                      rm_m.group("locus"), rm_m.group("sim").strip()])

def parseSingleSeqEnzTable(rms):
    tp = "-"
    enzs = []
    for tr_m in tr_p.finditer(rms):
        tr = tr_m.group("tr").strip()
        type_m = type_p.match(tr)
        if type_m:
            tp = type_m.group("sys")
            continue
        rm_m = rm_p.match(tr)
        if rm_m:
            enzs.append(parseEnzRow(tp, rm_m))
    return enzs

def parseMultiSeqEnzTable(rms):
    main = [] # ((tags, type_enzs), ...)
    type_enzs = [] # (enzs, ...)
    enzs = []
    tags = []
    tag = "-"
    tp = "-"
    for tr_m in tr_p.finditer(rms):
        tr = tr_m.group("tr").strip()
        type_m = type_p.match(tr)
        if type_m:
            if enzs:
                tags.append(tag)
                type_enzs.append(tuple(enzs))
                main.append((tuple(tags), tuple(type_enzs)))
                enzs = []
                type_enzs = []
                tags = []
            tp = type_m.group("sys")
            continue
        tag_m = tag_p.match(tr)
        if tag_m:
            if enzs:
                type_enzs.append(tuple(enzs))
                tags.append(tag)
                enzs = []
            tag = tag_m.group("tag")
            continue
        rm_m = rm_p.match(tr)
        if rm_m:
            enzs.append(parseEnzRow(tp, rm_m))
    tags.append(tag)
    type_enzs.append(tuple(enzs))
    main.append((tuple(tags), tuple(type_enzs)))
    return tuple(main)

def getAC(ac):
    if "," in ac:
        ac = ac.replace(", ", ",")
    elif "(" in ac:
        ac, ac_ = ac.split(" ")
        if "_" in ac:
            ac = ac_.strip("()")
    if "_" in ac:
        return (ac, "RefSeq AC (%s)" % ac)
    if ac.startswith("NEBC"):
        return (ac, "invalid AC (%s)" % ac)
    return (ac, "")

def _print_enzs(outab, gid, ac, enzs):
    line = gid + "\t" + ac + "\t%s\n"
    for enz in enzs:
        outab.write(line % enz)

if __name__ == "__main__":
    parser = ap.ArgumentParser(description="Parse REBASE summary pages.")
    parser.add_argument(
            "inpath", metavar="SUMMARY_PATH",
            help="REBASE summary pages path, use {} placeholder for gid"
            )
    parser.add_argument(
            "oupath", metavar="UNFINISHED_PATH",
            help="unfinished summaries path, use {} placeholder for gid"
            )
    parser.add_argument(
            "-l", metavar="IN_GIDS", dest="ingids", type=ap.FileType("r"),
            required=True, help="input list with genome IDs"
            )
    parser.add_argument(
            "-s", metavar="OUT_SUMS", dest="outab", type=ap.FileType("w"),
            required=True, help="output tabular file with summaries"
            )
    parser.add_argument(
            "-o", metavar="OUT_ORGS", dest="ortab", type=ap.FileType("w"),
            required=True, help="output tabular file with organisms"
            )
    args = parser.parse_args()
    with args.ingids as ingids:
        gids = sorted(ingids.read().strip().split("\n"))
    with args.outab as outab, args.ortab as ortab:
        outab.write(
                "REBASE genome ID\tSequence AC\tR-M system type\t" +
                "REBASE name\tGene type\tRecognition site\t" +
                "ORF number\tSimilar enzyme\n"
                )
        ortab.write(
                "REBASE genome ID\tOrganism acronym\tOrganims ID\t" +
                "Refference\tSequence AC\tSequence tag\tSequence length\n"
                )
        for gid in gids:
            with open(args.inpath.format(gid)) as inhtml:
                html = inhtml.read()
            sum_m = sum_p.search(html)
            acro = sum_m.group("acro") or "-"
            num = sum_m.group("num") or "-"
            ref = sum_m.group("ref") or "-"
            rms = sum_m.group("rms").strip()
            if not rms:
                print "Note: %s is empty." % gid
                continue
            dnas = sum_m.group("dnas").strip()
            if dnas.startswith("<table"):
                acs = dict()
                seqs = []
                solvable = True
                for multi_m in multi_p.finditer(dnas):
                    ac = multi_m.group("acc").strip()
                    ac, ac_tag = getAC(ac)
                    if ac_tag:
                        print "Note: %s has %s." % (gid, ac_tag)
                    tag = multi_m.group("tag")
                    length = multi_m.group("len").strip().replace(",", "")
                    ortab.write("\t".join([gid, acro, num ,ref, ac,
                                           tag, length]) + "\n")
                    if tag in acs:
                        solvable = False
                        acs[tag].append(ac)
                    else:
                        acs[tag] = [ac]
                    seqs.append((ac, tag))
                enzs = parseMultiSeqEnzTable(rms)
                if solvable:
                    for tags, tp_enzs in enzs:
                        for tag, tag_enzs in zip(tags, tp_enzs):
                            ac = acs[tag][0]
                            _print_enzs(outab, gid, acs[tag][0], tag_enzs)
                else:
                    tosmr = ""
                    for tags, tp_enzs in enzs:
                        if len(tags) == len(seqs):
                            for (ac, tag), tag_enzs in zip(seqs, tp_enzs):
                                _print_enzs(outab, gid, ac, tag_enzs)
                        else:
                            tags_dict = dict()
                            for tag, tag_enzs in zip(tags, tp_enzs):
                                if tag in tags_dict:
                                    tags_dict[tag].append(tag_enzs)
                                else:
                                    tags_dict[tag] = [tag_enzs]
                            for tag, val in tags_dict.items():
                                if len(val) == len(acs[tag]):
                                    for ac, enzs in zip(acs[tag], val):
                                        _print_enzs(outab, gid, ac, enzs)
                                else:
                                    for enzs in val:
                                        block = "\n".join(enzs)
                                        tosmr += "#%s\n%s\n" % (tag, block)
                    if tosmr:
                        with open(args.oupath.format(gid), "w") as ousmr:
                            for seq in seqs:
                                if len(acs[seq[1]]) == 1:
                                    continue
                                ousmr.write(
                                        "#Sequence:\t%s\t%s\n" % seq
                                        )
                            ousmr.write(tosmr)
            else:
                single_m = single_p.match(dnas)
                ac = single_m.group("acc")
                ac, ac_tag = getAC(ac)
                if ac_tag:
                    print "Note: %s has %s." % (gid, ac_tag)
                tag = single_m.group("tag") or "-"
                length = single_m.group("len") or "-"
                length = length.replace(",", "")
                ortab.write("\t" .join([gid, acro, num, ref, ac, tag,
                                        length]) + "\n")
                _print_enzs(outab, gid, ac, parseSingleSeqEnzTable(rms))

