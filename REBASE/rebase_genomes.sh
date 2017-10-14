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

mkdir -p "$WDIR/index"

printf "\n\tLoading index pages ...\n"
wget -nv -NP "$WDIR/index" -B "http://tools.neb.com/genomes/" \
    -i "$SDIR/index.list"

printf "\n\tParsing index pages ...\n"
$SDIR/parse_index.py "$WDIR/index/"* -o "$WDIR/genomes.tsv"

tail -n+2 "$WDIR/genomes.tsv" | cut -f 3 | \
    sort -gu > "$WDIR/all.gid"
ALL=$(cat "$WDIR/all.gid" | wc -l)

tail -n+2 "$WDIR/genomes.tsv" | grep -v "no RMs" | cut -f 3 | \
    sort -gu > "$WDIR/rms.gid"
RMS=$(cat "$WDIR/rms.gid" | wc -l)

printf "\nThere are $ALL genome IDs, $RMS genomes encode R-M systems.\n\n"
date "+%d/%m/%Y %T"
