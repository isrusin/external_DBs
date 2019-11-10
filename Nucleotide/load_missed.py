#! /usr/bin/env python3


"""Load missed NCBI Nucleotide entries through efetch request.

* Get list of missed ACs.
* Send a request to the Entrez Fetch util.
* Split the uploaded GenBank Flatfile by entries, save sequences in
separate Fasta files; gzip everything.
"""


import argparse
import gzip
import os
import re
import socket
import sys
import time

from urllib.request import Request, urlopen
from urllib.parse import urlencode
from urllib.error import URLError


GBK_FOLDER_STUB = "{wdir}/gbk"
GBK_FILE_STUB = "{wdir}/gbk/{acv}.gbk.gz"
FASTA_FOLDER_STUB = "{wdir}/fasta"
FASTA_FILE_STUB = "{wdir}/fasta/{acv}.fasta.gz"
ACV_FILE_STUB = "{wdir}/.acv"

MESSAGE_TAGS = ["Error", "Warning", ""]
ERROR, WARNING, NOTE = 0, 1, 2

TOOL_ID = "load-missed"
EMAIL = "@".join((os.getlogin(), socket.gethostname()))


def message(level, text, *format_args, **format_kwargs):
    if format_args or format_kwargs:
        text = text.format(*format_args, **format_kwargs)
    print(
        MESSAGE_TAGS[level], text,
        sep=": ", file=sys.stderr
    )


def prepare_wdir(wdir):
    for dir_stub in [GBK_FOLDER_STUB, FASTA_FOLDER_STUB]:
        dir_path = dir_stub.format(wdir=wdir)
        try:
            os.makedirs(dir_path, exist_ok=True)
        except OSError as mkdir_error:
            message(ERROR, mkdir_error)
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


def cut_versions(acvs):
    return set(acv.split(".")[0] for acv in acvs)


def exclude_loaded(wdir, acvs):
    loaded = load_acv_list(ACV_FILE_STUB.format(wdir=wdir))
    if not hasattr(acvs, "difference"):
        acvs = set(acvs)
    toload = acvs.difference(loaded, cut_versions(loaded))
    message(NOTE, "{} AC(v)s are missed", len(toload))
    return toload


def extract_gbk_definition(byte_lines):
    desc = ""
    in_def_block = False
    for byte_line in byte_lines:
        if byte_line.startswith(b"DEFINITION"):
            in_def_block = True
        elif not byte_line.startswith(b"          "):
            in_def_block = False
        if in_def_block:
            desc += byte_line.decode()[11:-1]
    return desc


def read_gbk_header(ingbk):
    byte_line = ingbk.readline()
    unexpected_lines = []
    while byte_line and not byte_line.startswith(b"LOCUS"):
        if byte_line.strip():
            unexpected_lines.append(byte_line)
        byte_line = ingbk.readline()
    if unexpected_lines:
        message(
            WARNING, "skip {} unexpected line(s)", len(unexpected_lines)
        )
    acv = None
    desc = ""
    header = []
    while byte_line:
        header.append(byte_line)
        if byte_line.startswith(b"VERSION"):
            acv = byte_line.decode().split()[1]
            break
        byte_line = ingbk.readline()
    desc = extract_gbk_definition(header)
    return header, acv, desc


def save_gbk_sequence(wdir, ingbk, acv, desc):
    fasta_path = FASTA_FILE_STUB.format(wdir=wdir, acv=acv)
    complete = False
    with gzip.open(fasta_path, "wb", compresslevel=5) as oufasta:
        oufasta.write(
            ">{acv}{desc}\n".format(acv=acv, desc=desc).encode()
        )
        byte_line = ingbk.readline()
        while byte_line:
            if byte_line.startswith(b"//"):
                complete = True
                break
            oufasta.write(
                byte_line.lstrip(b" 0123456789").replace(b" ", b"")
            )
            byte_line = ingbk.readline()
    return complete


def save_gbk_entry(wdir, ingbk):
    header, acv, desc = read_gbk_header(ingbk)
    if acv is None:
        return None
    gbk_path = GBK_FILE_STUB.format(wdir=wdir, acv=acv)
    with gzip.open(gbk_path, "wb", compresslevel=5) as ougbk:
        ougbk.writelines(header)
        byte_line = ingbk.readline()
        while byte_line:
            ougbk.write(byte_line)
            if byte_line.startswith(b"//"):
                message(WARNING, "{} entry has no sequence", acv)
                return acv
            if byte_line.startswith(b"ORIGIN"):
                ougbk.write(b"//\n")
                break
            byte_line = ingbk.readline()
    complete = save_gbk_sequence(wdir, ingbk, acv, desc)
    if not complete:
        message(ERROR, "{} sequence is not complete!", acv)
        return None
    return acv


def send_epost(acvs, webenv=None):
    args_dict = {
        "db": "nuccore", "id": ",".join(sorted(acvs)),
        "tool": TOOL_ID, "email": EMAIL
    }
    if webenv is not None:
        args_dict["WebEnv"] = webenv
    post_args = urlencode(args_dict).encode()
    req = Request(
        "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/epost.fcgi",
        post_args, {"Content-Type": "application/x-www-form-urlencoded"}
    )
    with urlopen(req) as response:
        res_xml = response.read().decode()
    webenv, query_key = None, None
    res_regexp = re.compile(
        """
        <QueryKey>(?P<QueryKey>[^<]+)</QueryKey>.*
        <WebEnv>\s*(?P<WebEnv>[^<\s]+)\s*</WebEnv>
        """,
        flags=(re.ASCII | re.DOTALL | re.VERBOSE)
    )
    res_match = res_regexp.search(res_xml)
    if res_match:
        webenv = res_match.group("WebEnv")
        query_key = res_match.group("QueryKey")
    else:
        message(ERROR, "bad epost response!")
    return webenv, query_key


def efetch_from_history(webenv, query_key, retstart=0,
                        retmax=500, retry_num=5):
    args_dict = {
        "db": "nuccore", "rettype": "gbwithparts", "retmode": "text",
        "retstart": retstart, "retmax": retmax,
        "WebEnv": webenv, "query_key": query_key,
        "tool": TOOL_ID, "email": EMAIL
    }
    post_args = urlencode(args_dict).encode()
    message(NOTE, "request efetch\n{}", post_args)
    req = Request(
        "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi",
        post_args, {"Content-Type": "application/x-www-form-urlencoded"}
    )
    response = None
    for try_num in range(retry_num):
        try:
            response = urlopen(req)
        except URLError as urlerror:
            message(
                WARNING,
                "efetch request failed, try #{} of {}\n{}",
                try_num, retry_num, urlerror
            )
            continue
    if response is None:
        message(ERROR, "giving up to request efetch!")
    return response


def parse_efetch_response(wdir, response):
    loaded = set()
    with response:
        try:
            acv = save_gbk_entry(wdir, response)
            while acv:
                message(NOTE, "{} entry was loaded", acv)
                loaded.add(acv)
                acv = save_gbk_entry(wdir, response)
        except URLError as url_error:
            message(ERROR, url_error)
    update_loaded_list(wdir, loaded)
    return loaded


def epost_efetch_pipeline(wdir, acvs, fetch_num=500):
    webenv, query_key = send_epost(acvs)
    loaded = set()
    for fetch_start in range(0, len(acvs), fetch_num):
        response = efetch_from_history(
            webenv=webenv, query_key=query_key,
            retstart=fetch_start, retmax=fetch_num
        )
        loaded.update(parse_efetch_response(wdir, response))
        time.sleep(0.5)
    if not hasattr(acvs, "difference"):
        acvs = set(acvs)
    missed = acvs.difference(loaded)
    return missed


def main(argv=None):
    parser = argparse.ArgumentParser(
        description="Load missed NCBI Nucleotide entries."
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
    if not prepare_wdir(wdir):
        parser.error("bad working folder (-s option)")
    fetch_num = 500
    retry_num = 5
    acvs = load_acv_list(args.inacvs)
    for try_num in range(retry_num):
        message(NOTE, "Try #{}".format(try_num + 1))
        toload = exclude_loaded(wdir, acvs)
        missed = epost_efetch_pipeline(
            wdir, toload, fetch_num=fetch_num,
        )
        if missed:
            message(WARNING, "{} entries were not loaded", len(missed))
            time.sleep(0.5)
        else:
            break


if __name__ == "__main__":
    sys.exit(main())


def __parse_ids_from_names(file_paths, path_regexp=None):
    if path_regexp is None:
        path_regexp=re.compile(
            "(?:[^/]*/)*(?P<ID>.+)(?:\.[^.]+)?"
        )
    ids = set()
    for file_path in file_paths:
        path_match = path_regexp.fullmatch(file_path)
        if path_match:
            ids.add(path_match.group(1))
    return ids


def __recover_loaded_list(wdir):
    ids_gbk = __parse_ids_from_names(
        GBK_FOLDER_STUB.format(wdir=wdir),
        path_regexp=re.compile(
            "(?:[^/]*/)*(?P<ID>.+)\.gbk\.gz"
        )
    )
    ids_fasta = __parse_ids_from_names(
        FASTA_FOLDER_STUB.format(wdir=wdir),
        path_regexp=re.compile(
            "(?:[^/]*/)*(?P<ID>.+)\.fasta\.gz"
        )
    )
    acvs = ids_gbk & ids_fasta
    update_loaded_list(wdir, acvs, append=False)

