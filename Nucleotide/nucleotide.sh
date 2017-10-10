#! /bin/bash

WDIR=$(dirname $0)
GDIR="$WDIR/../NCBI_Genome"
if [ -n "$1" ]; then GDIR=$1; fi

printf "ACv source: $GDIR\n"

date "+%d-%m-%Y %T"

printf "Downloading plasmids ...\n"
time $WDIR/load_missed.py "$GDIR/plasmids.acv" -s "$WDIR"

printf "Downloading chromosomes ...\n"
time $WDIR/load_missed.py "$GDIR/chromosomes.acv" -s "$WDIR"

printf "Getting lengths ...\n"
time $WDIR/get_lengths.py "$WDIR/gbk/{}.gbk.gz" -l "$WDIR/.acv"
    -o "$WDIR/acv2len.dct"

date "+%d-%m-%Y %T"
