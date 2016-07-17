#! /bin/bash

WDIR=$(dirname $0)
TAXDIR="$WDIR/../NCBI_Taxonomy"
if [ -n "$1" ]; then TAXDIR=$1; fi

printf "Taxonomy source: $TAXDIR\n"

date "+%D %T"

wget -NP "$WDIR" \
        ftp://ftp.ncbi.nlm.nih.gov/genomes/GENOME_REPORTS/prokaryotes.txt

printf "1_filter_genomes.py ...\n"
time $WDIR/1_filter_genomes.py --no-wgs --with-chromosomes --min-size=0.1 \
        -i "$WDIR/prokaryotes.txt" -o "$WDIR/complete_genomes.tab" \
        "Complete" "Complete Genome" "Gapless Chromosome" "Chromosome" \
        "Chromosome with gaps"

printf "2_find_repeates.py ...\n"
time $WDIR/2_find_repeates.py "$WDIR/complete_genomes.tab"

printf "3_enumerate_genomes.py ...\n"
time $WDIR/3_enumerate_genomes.py -t "$TAXDIR/taxonomy_prokaryotes.tab" \
        -i "$WDIR/complete_genomes.tab" -o "$WDIR/enumerated_genomes.tab"

tail -n+2 "$WDIR/enumerated_genomes.tab" | cut -f 4 | grep -Eo "[^,]+" | \
        sort -u > chromosomes.acvs
tail -n+2 "$WDIR/enumerated_genomes.tab" | cut -f 5 | grep -Eo "[^,]+" | \
        sort -u > plasmids.acvs

date "+%D %T"
