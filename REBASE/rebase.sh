#! /bin/bash

SDIR=$(dirname "$0") # source dir

WDIR="REBASE" # working dir
if [ -n "$1" ]
    then if [ -d "$1" ] || mkdir "$1"
        then WDIR="$1"
        else printf "Bad working folder name!\n"; exit 1
    fi
fi

date "+%d/%m/%Y %T"
printf "Working folder: $WDIR\n"

mkdir -p "$WDIR/ftp"

printf "\n\tLoading VERSION ...\n"
wget -nv -NP "$WDIR/ftp/" ftp://ftp.neb.com/pub/rebase/VERSION

printf "\n\tLoading DNA sequences ...\n"
wget -nv -NP "$WDIR/ftp/" ftp://ftp.neb.com/pub/rebase/dna_seqs.txt
#sed -i "1d; s/<>//; /^$/d" "$WDIR/ftp/dna_seqs.txt"

printf "\n\tParsing DNA sequences ...\n"
$SDIR/parse_seqs.py "$WDIR/ftp/dna_seqs.txt" "$WDIR/genes.tsv" \
    "$WDIR/genes.fasta"

printf "\n\tLoading protein sequences ...\n"
wget -nv -NP "$WDIR/ftp/" ftp://ftp.neb.com/pub/rebase/protein_seqs.txt
#sed -i "1d; s/<>//; /^$/d" "$WDIR/ftp/protein_seqs.txt"

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

printf "\n\tLoading linkoutenz ...\n"
wget -nv -NP "$WDIR/ftp/" ftp://ftp.neb.com/pub/rebase/linkoutenz*.xml

date "+%d/%m/%Y %T"
