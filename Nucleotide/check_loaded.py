#! /usr/bin/env python3


"""Check loaded NCBI Nucleotide entries and return invalid entries.

* Check if gbk files end with // line.
* Check if ACV in gbk and fasta files match the file names.
* Check if length of sequence in fasta match the value in the gbk.
* Compare list of gbk and fasta files with the list from the .acv file.
"""


import argparse
import gzip
import re
import sys

from collections import Counter
from os import listdir
from os.path import isdir


GBK_FOLDER_STUB = "{wdir}/gbk"
GBK_FILE_STUB = "{wdir}/gbk/{acv}.gbk.gz"
FASTA_FOLDER_STUB = "{wdir}/fasta"
FASTA_FILE_STUB = "{wdir}/fasta/{acv}.fasta.gz"
ACV_FILE_STUB = "{wdir}/.acv"

MESSAGE_TAGS = ["Error", "Warning", "Note"]
ERROR, WARNING, NOTE = 0, 1, 2


def message(level, text, *format_args, **format_kwargs):
    if format_args or format_kwargs:
        text = text.format(*format_args, **format_kwargs)
    print(
        MESSAGE_TAGS[level], text,
        sep=": ", file=sys.stderr
    )
    sys.stderr.flush()


def check_wdir(wdir):
    answer = True # wdir is OK
    for dir_stub in [GBK_FOLDER_STUB, FASTA_FOLDER_STUB]:
        dir_path = dir_stub.format(wdir=wdir)
        answer &= isdir(dir_path)
    if not answer:
        return False
    acv_path = ACV_FILE_STUB.format(wdir=wdir)
    with open(acv_path, "a"):
        pass
    return True


def load_acv_list(inacvs):
    if not hasattr(inacvs, "read"):
        inacvs = open(inacvs)
    with inacvs:
        acvs = set(inacvs.read().split())
    return acvs


def update_loaded_list(wdir, acvs, append=True):
    acv_path = ACV_FILE_STUB.format(wdir=wdir)
    if append:
        loaded = load_acv_list(acv_path)
        acvs = loaded.union(acvs)
    with open(acv_path, "w") as ouacvs:
        ouacvs.write("\n".join(sorted(acvs)) + "\n")
    message(NOTE, "{} records in the database", len(acvs))


def parse_ids_from_names(file_paths, path_regexp=None):
    if path_regexp is None:
        path_regexp=re.compile(
            "(?:[^/]*/)*(?P<ID>.+)(?:\.[^.]+)?"
        )
    ids = set()
    for file_path in file_paths:
        path_match = path_regexp.fullmatch(file_path)
        if path_match:
            ids.add(path_match.group(1))
        else:
            message(WARNING, "{} does not match the pattern", file_path)
    return ids


def extract_loaded_entries(wdir):
    ids_gbk = parse_ids_from_names(
        listdir(GBK_FOLDER_STUB.format(wdir=wdir)),
        path_regexp=re.compile(
            "(?:[^/]*/)*(?P<ID>.+)\.gbk\.gz"
        )
    )
    ids_fasta = parse_ids_from_names(
        listdir(FASTA_FOLDER_STUB.format(wdir=wdir)),
        path_regexp=re.compile(
            "(?:[^/]*/)*(?P<ID>.+)\.fasta\.gz"
        )
    )
    acvs = ids_gbk & ids_fasta
    incomplete = (ids_gbk | ids_fasta) - acvs
    if incomplete:
        message(
            WARNING,
            "there are {} entries without gbk or fasta part:\n\t{}",
            len(incomplete), "\n\t".join(sorted(incomplete))
        )
    return acvs


def group_symbol_counts(counts):
    grouped_smbls = {
        "ACGT": "acgt", "N": "n", "IUPAC": "bdhvukmryws",
        "SPACE": " \t\r", "BREAK": "\n", "GAP": "-.", "BAD": ""
    }
    smbl_groups = {
        smbl: grp for grp in grouped_smbls for smbl in grouped_smbls[grp]
    }
    group_counts = dict.fromkeys(grouped_smbls, 0)
    for smbl, count in counts.items():
        grp = smbl_groups.get(smbl, "BAD")
        group_counts[grp] += count
    length = sum(group_counts[grp] for grp in ("ACGT", "N", "IUPAC"))
    group_counts["NUCLS"] = length
    return group_counts


def check_fasta(wdir, acv, length):
    answer = True # file is good
    fasta_path = FASTA_FILE_STUB.format(wdir=wdir, acv=acv)
    smbl_counts = Counter()
    try:
        with gzip.open(fasta_path, "rt") as infasta:
            line = infasta.readline()
            if line.startswith(">"):
                acv_from_fasta, *_desc = line[1:].split()
                if acv_from_fasta != acv:
                    answer = False
                    message(
                        WARNING, "{} does not match fasta sequence ID {}",
                        acv, acv_from_fasta
                    )
            else:
                message(WARNING, "{} has bad fasta format", acv)
                return False

            while line:
                line = infasta.readline()
                smbl_counts.update(line.lower())
    except (EOFError, OSError) as error:
        message(
            WARNING, "{} has IO problem with the fasta file:\n{}",
            acv, error
        )
        return False

    group_counts = group_symbol_counts(smbl_counts)
    if group_counts["NUCLS"] != length:
        answer = False
        message(
            WARNING,
            "{} sequence length {} does not match the expected value {}",
            acv, group_counts["NUCLS"], length
        )

    if group_counts["BAD"]:
        answer = False
        message(
            WARNING, "{} contains {} bad symbols",
            acv, group_counts["BAD"]
        )
    for grp_name in ("N", "IUPAC", "space", "gap"):
        grp = grp_name.upper()
        if group_counts[grp]:
            count = group_counts[grp]
            message(
                NOTE, "{acv} contains {count} {group} symbols",
                acv=acv, count=count, group=grp_name
            )
    return answer


def check_entry(wdir, acv):
    answer = True # entry is good
    gbk_path = GBK_FILE_STUB.format(wdir=wdir, acv=acv)
    length = None
    try:
        with gzip.open(gbk_path, "rt") as ingbk:
            line = ingbk.readline()
            if line.startswith("LOCUS"):
                try:
                    length = int(line.split()[2])
                except (IndexError, ValueError):
                    answer = False
                    message(WARNING, "{} LOCUS line has bad format", acv)
            else:
                message(WARNING, "{} has bad gbk format", acv)
                return False

            while not line.startswith("VERSION"):
                line = ingbk.readline()
            _field, acv_from_gbk, *_etc = line.strip().split()
            if acv_from_gbk != acv:
                answer = False
                message(
                    WARNING, "{} does not match gbk entry VERSION {}",
                    acv, acv_from_gbk
                )

            while line:
                if line.startswith("//"):
                    break
                line = ingbk.readline()
            else:
                message(WARNING, "{} gbk file is truncated", acv)
                return False

            if ingbk.readline().strip():
                answer = False
                message(
                    WARNING,
                    "{} has non-empty lines after entry end", acv
                )
    except (EOFError, OSError) as error:
        message(
            WARNING, "{} has IO problem with the gbk file:\n{}",
            acv, error
        )
        return False
    return answer and check_fasta(wdir, acv, length)


def main(argv=None):
    parser = argparse.ArgumentParser(
        description="Check loaded NCBI Nucleotide entries."
    )
    parser.add_argument(
        "-s", "--source", dest="wdir", metavar="DIR", default=".",
        help="working folder"
    )
    parser.add_argument(
        "--update-list", action="store_true", help="update .acv file"
    )
    args = parser.parse_args(argv)
    wdir = args.wdir
    if not check_wdir(wdir):
        parser.error("bad working folder (-s option)")
    acv_list = load_acv_list(ACV_FILE_STUB.format(wdir=wdir))
    loaded = extract_loaded_entries(wdir)
    checked = set(acv for acv in sorted(loaded) if check_entry(wdir, acv))
    message(NOTE, "{} entries are correct", len(checked))
    missed = acv_list - checked
    if missed:
        message(
            WARNING, "{} entries are missed or corrupted:\n\t{}",
            len(missed), "\n\t".join(sorted(missed))
        )
    unmarked = checked - acv_list
    if unmarked:
        message(
            WARNING, "{} entries are not marked as loaded:\n\t{}",
            len(unmarked), "\n\t".join(sorted(unmarked))
        )
    if args.update_list:
        message(NOTE, "updating the list of loaded entires")
        update_loaded_list(wdir, checked, append=False)


if __name__ == "__main__":
    sys.exit(main())

