#! /bin/bash

WDIR="REBASE"
SDIR="scripts"
if [ -n "$1" ]; then WDIR=$1; fi

date "+%d/%m/%Y %T"

mkdir -p "$WDIR/ftp"

printf "\n\tLoading DNA sequences ...\n"
wget -nv -NP "$WDIR/ftp/" ftp://ftp.neb.com/pub/rebase/dna_seqs.txt
sed -i "1d; s/<>//; /^$/d" "$WDIR/ftp/dna_seqs.txt"

printf "\n\tParsing DNA sequences ...\n"
$SDIR/parse_seqs.py "$WDIR/ftp/dna_seqs.txt" "$WDIR/genes.tsv" \
    "$WDIR/genes.fasta"

printf "\n\tLoading protein sequences ...\n"
wget -nv -NP "$WDIR/ftp/" ftp://ftp.neb.com/pub/rebase/protein_seqs.txt
sed -i "1d; s/<>//; /^$/d" "$WDIR/ftp/protein_seqs.txt"

printf "\n\tParsing protein sequences ...\n"
$SDIR/parse_seqs.py "$WDIR/ftp/protein_seqs.txt" "$WDIR/proteins.tsv" \
    "$WDIR/proteins.fasta"

printf "\n\tLoading bairoch ...\n"
wget -nv -NP "$WDIR/ftp/" ftp://ftp.neb.com/pub/rebase/bairoch.txt

printf "\n\tParsing bairoch ...\n"
$SDIR/parse_bairoch.py "$WDIR/ftp/bairoch.txt" -o "$WDIR/bairoch.tsv"

printf "\n\tLoading allenz ...\n"
wget -nv -NP "$WDIR/ftp/" ftp://ftp.neb.com/pub/rebase/allenz.txt

printf "\n\tParsing allenz ...\n"
$SDIR/parse_allenz.py "$WDIR/ftp/allenz.txt" -o "$WDIR/allenz.tsv"

date "+%d/%m/%Y %T"
