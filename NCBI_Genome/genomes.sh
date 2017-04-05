#! /bin/bash

WDIR=$(dirname $0)
TAXDIR="$WDIR/../NCBI_Taxonomy"
if [ -n "$1" ]; then TAXDIR=$1; fi

printf "Taxonomy source: $TAXDIR\n"

date "+%D %T"

wget -nv -NP "$WDIR" \
    ftp://ftp.ncbi.nlm.nih.gov/genomes/GENOME_REPORTS/prokaryotes.txt

printf "\nFiltering the list of genomes ...\n"
time $WDIR/filter_genomes.py --with-chromosomes --min-size=0.1 \
    -o "$WDIR/complete_genomes.tab" "$WDIR/prokaryotes.txt" \
    "Complete" "Complete Genome" "Chromosome"

printf "\nSearching for repeated IDs ...\n"
time $WDIR/report_repeats.py "$WDIR/complete_genomes.tab"

printf "\nEnumerating genomes ...\n"
time $WDIR/enumerate_genomes.py -o "$WDIR/enumerated_genomes.tab" \
    "$WDIR/complete_genomes.tab" "$TAXDIR/taxonomy_prokaryotes.tab"

tail -n+2 "$WDIR/enumerated_genomes.tab" | cut -f 4 | \
    grep -Eo "[^,]+" | sort -u > chromosomes.acv

tail -n+2 "$WDIR/enumerated_genomes.tab" | cut -f 5 | \
    grep -Eo "[^,]+" | sort -u > plasmids.acv

tail -n+2 "$WDIR/enumerated_genomes.tab" | cut -f 6 | \
    grep -Eo "[^,]+" | sort -u > other.acv

date "+%D %T"
