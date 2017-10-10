#! /bin/bash

SDIR=$(dirname "$0")

WDIR="."
if [ -n "$1" ]
    then if [ -d "$1" ] || mkdir "$1"
        then WDIR=$1
        else printf "Bad working folder name!\n"; exit 1
    fi
fi

date "+%d-%m-%Y %T"
printf "Working folder: $WDIR\n"

wget -nv -NP "$WDIR" ftp://ftp.ncbi.nih.gov/pub/taxonomy/taxdump.tar.gz

printf "\nParsing NCBI taxdump archive ...\n"
$SDIR/parse_taxdump.py "$WDIR/taxdump.tar.gz" -o "$WDIR/taxonomy.tsv"

printf "\nExtracting prokaryotic subtree ...\n"
$SDIR/extract_subtree.py 2 2157 \
    -i "$WDIR/taxonomy.tsv" -o "$WDIR/taxonomy_prokaryotes.tsv"

printf "\nExtracting viral subtree ...\n"
$SDIR/extract_subtree.py 10239 12884 \
    -i "$WDIR/taxonomy.tsv" -o "$WDIR/taxonomy_viruses.tsv"

date "+%d-%m-%Y %T"
