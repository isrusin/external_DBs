#! /bin/bash

WDIR=$(dirname "$0")

date "+%D %T"

wget -nv -NP "$WDIR" ftp://ftp.ncbi.nih.gov/pub/taxonomy/taxdump.tar.gz

printf "1_get_taxon_ranks.py ...\n"
time $WDIR/1_get_taxon_ranks.py -o "$WDIR/taxonomy.tab" \
        "$WDIR/taxdump.tar.gz"

printf "2_extract_by_root_taxid.py ...\n"
time $WDIR/2_extract_by_root_taxid.py 2 2157 \
        -i "$WDIR/taxonomy.tab" -o "$WDIR/taxonomy_prokaryotes.tab"

date "+%D %T"
