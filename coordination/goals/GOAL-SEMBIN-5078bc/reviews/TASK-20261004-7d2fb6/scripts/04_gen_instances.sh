#!/bin/bash
# The 22 small scratch instances used by the W4/W5/W7 experiments (generator = the repository's boolsys/eq4sys, unmodified; |V| by truth table).
. $(dirname $0)/00_env.sh
mkdir -p $SP/work/inst; cd $SP/work
G="python3 $WS/scripts/gen_small.py $SP/work/inst"
for n in 12 14 16 18; do $G chained $n 2 2 $(( (n+1)/2 )) 0; done
$G chained 20 2 2 10 3; $G chained 18 2 2 11 0; $G chained 9 3 3 4 0; $G chained 10 3 3 4 0
$G null 16 2 2 8 0; $G null 18 2 2 9 0; $G null 12 2 2 9 0; $G null 14 2 2 10 0
$G eq4 8 3 3 4 0; $G eq4 8 3 3 3 0; $G eq4 7 3 3 4 0; $G eq4 9 3 3 4 0; $G eq4 8 3 3 5 0
$G chained 24 2 2 12 1; $G chained 9 3 3 5 0; $G chained 26 2 2 13 1; $G chained 26 2 2 13 2; $G chained 26 2 2 13 3
