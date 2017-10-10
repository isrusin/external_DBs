#! /bin/bash

WDIR=$(dirname $0)
GDIR="$WDIR/../NCBI_Genome"
if [ -n "$1" ]; then GDIR=$1; fi

printf "ACvs source: $GDIR\n"

date "+%D %T"

printf "Downloading plasmids ...\n"
time $WDIR/load_missed.py "$GDIR/plasmids.acvs" -s "$WDIR"

printf "Downloading chromosomes ...\n"
time $WDIR/load_missed.py "$GDIR/chromosomes.acvs" -s "$WDIR"

printf "Getting lengths ...\n"
time $WDIR/get_lengths.py "$WDIR/gbk/{}.gbk.gz" -l "$WDIR/.acvs"
    -o "$WDIR/acv2len.dct"

date "+%D %T"
