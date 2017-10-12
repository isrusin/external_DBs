#! /bin/bash

SDIR=$(dirname "$0")

TAXDIR="."
if [ -d "$1" ]
    then TAXDIR="$1"
    else printf "Usage: <script> TAXDIR [WDIR]\n"; exit
fi

WDIR="."
if [ -n "$2" ]
    then if [ -d "$2" ] || mkdir "$2"
        then WDIR="$2"
        else printf "Bad working folder name!\n"; exit 1
    fi
fi

date "+%d-%m-%Y %T"
printf "Working folder: $WDIR\nTaxonomy source: $TAXDIR\n"

wget -nv -NP "$WDIR" \
    ftp://ftp.ncbi.nlm.nih.gov/genomes/GENOME_REPORTS/prokaryotes.txt

printf "\nSearching for repeated IDs ...\n"
"$SDIR/report_repeats.py" -n 5 "$WDIR/prokaryotes.txt"

printf "\nAppending taxonomy ...\n"
"$SDIR/add_taxonomy.py" -o "$WDIR/assemblies.tsv" \
    "$WDIR/prokaryotes.txt" "$TAXDIR/taxonomy_prokaryotes.tsv"

printf "\nFiltering the list of genomes ...\n"
"$SDIR/filter_genomes.py" --with-chromosomes --min-size=0.1 \
    -o "$WDIR/genomes.tsv" "$WDIR/assemblies.tsv" "Genome"

tail -n+2 "$WDIR/genomes.tsv" | cut -f 3 | \
    grep -Eo "[^,]+" | sort -u > "$WDIR/chromosomes.acv"

tail -n+2 "$WDIR/genomes.tsv" | cut -f 4 | \
    grep -Eo "[^,]+" | sort -u > "$WDIR/plasmids.acv"

tail -n+2 "$WDIR/genomes.tsv" | cut -f 5 | \
    grep -Eo "[^,]+" | sort -u > "$WDIR/other.acv"

date "+%d-%m-%Y %T"
