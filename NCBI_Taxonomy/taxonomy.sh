#! /bin/bash

WDIR=$(dirname "$0")

date "+%D %T"

wget -nv -NP "$WDIR" ftp://ftp.ncbi.nih.gov/pub/taxonomy/taxdump.tar.gz

printf "\nParsing NCBI taxdump archive ...\n"
time $WDIR/parse_taxdump.py "$WDIR/taxdump.tar.gz" -o "$WDIR/taxonomy.tab"

printf "\nExtracting prokaryotic subtree ...\n"
time $WDIR/extract_subtree.py 2 2157 \
    -i "$WDIR/taxonomy.tab" -o "$WDIR/taxonomy_prokaryotes.tab"

printf "\nExtracting viral subtree ...\n"
time $WDIR/extract_subtree.py 10239 12884 \
    -i "$WDIR/taxonomy.tab" -o "$WDIR/taxonomy_viruses.tab"

date "+%D %T"
