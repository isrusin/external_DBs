#! /bin/bash

WDIR="REBASE"
SDIR="scripts"
if [ -n "$1" ]; then WDIR=$1; fi

date "+%d/%m/%Y %T"

printf "'Genomes' section\n"

mkdir -p "$WDIR/index"
printf "1_load_index.py ...\n"
time $SDIR/1_load_index.py "$WDIR/index/{}.html"

printf "2_parse_index.py ...\n"
time $SDIR/2_parse_index.py "$WDIR/index/{}.html" \
        -o "$WDIR/genomes.tab"
tail -n+2 "$WDIR/genomes.tab" | cut -f 3 | \
        sort -u > "$WDIR/genomes.gids"
tail -n+2 "$WDIR/genomes.tab" | grep -v "no RMs" | cut -f 3 | \
        sort -u > "$WDIR/withrms.gids"

mkdir "$WDIR/summary" "$WDIR/report"
printf "3_load_summary-reports.py ...\n"
time $SDIR/3_load_summary-reports.py "$WDIR/withrms.gids" \
        -o "$WDIR/{type}/{gid}.html"

printf "4_parse_reports.py ...\n"
time $SDIR/4_parse_reports.py "$WDIR/report/{}.html" \
        -l "$WDIR/withrms.gids" -o "$WDIR/reports.tab"

mkdir "$WDIR/unfinished"
printf "5_parse_summaries.py ...\n"
time $SDIR/5_parse_summaries.py -l "$WDIR/withrms.gids" \
        "$WDIR/summary/{}.html" "$WDIR/unfinished/{}.smr" \
        -s "$WDIR/summaries.tab" -o "$WDIR/organisms.tab"
cat $WDIR/unfinished/*.smr | grep -v "^#" | cut -f 2 | \
        sort -u > "$WDIR/unfinished.nms"

mkdir "$WDIR/seqget"
printf "6_load_seqgets.py ...\n"
time $SDIR/6_load_seqgets.py "$WDIR/unfinished.nms" \
        -o "$WDIR/seqget/{}.html"

ls "$WDIR/unfinished" | grep -Eo "^[^.]+" > "$WDIR/unfinished.gids"
printf "7_solve_summaries.py ...\n"
time $SDIR/7_solve_summaries.py "$WDIR/unfinished/{}.smr" \
        "$WDIR/seqget/{}.html" -l "$WDIR/unfinished.gids" \
        -a "$WDIR/summaries.tab"

mkdir "$WDIR/azlist"
wget -O "$WDIR/azlist/IIM.html" http://rebase.neb.com/cgi-bin/azlist?md2
time $SDIR/8_parse_azlist.py "$WDIR/azlist/IIM.html" > "$WDIR/IIM.nms"
wget -O "$WDIR/azlist/IIG.html" http://rebase.neb.com/cgi-bin/rmlist
time $SDIR/8_parse_azlist.py "$WDIR/azlist/IIG.html" > "$WDIR/IIG.nms"

printf "FTP section ...\n"

mkdir "$WDIR/ftp"
wget -P "$WDIR/ftp/" ftp://ftp.neb.com/pub/rebase/dna_seqs.txt
sed -i "1d; s/<>//; /^$/d" "$WDIR/ftp/dna_seqs.txt"
printf "9_parse_seqs.py ... DNA\n"
time $SDIR/9_parse_seqs.py "$WDIR/ftp/dna_seqs.txt" \
        "$WDIR/dna_seqs.tab" "$WDIR/dna_seqs.fasta"
wget -P "$WDIR/ftp/" ftp://ftp.neb.com/pub/rebase/protein_seqs.txt
sed -i "1d; s/<>//; /^$/d" "$WDIR/ftp/protein_seqs.txt"
printf "9_parse_seqs.py ... proteins\n"
time $SDIR/9_parse_seqs.py "$WDIR/ftp/protein_seqs.txt" \
        "$WDIR/protein_seqs.tab" "$WDIR/protein_seqs.fasta"

wget -P "$WDIR/ftp/" ftp://ftp.neb.com/pub/rebase/allenz.txt
printf "10_parse_allenz.py ...\n"
time $SDIR/10_parse_allenz.py "$WDIR/ftp/allenz.txt" \
        -o "$WDIR/allenz.tab"

wget -P "$WDIR/ftp/" ftp://ftp.neb.com/pub/rebase/bairoch.txt
printf "11_parse_bairoch.py ...\n"
time $SDIR/11_parse_bairoch.py "$WDIR/ftp/bairoch.txt" \
        -o "$WDIR/bairoch.tab"

date "+%d/%m/%Y %T"
