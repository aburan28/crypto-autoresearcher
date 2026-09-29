#!/bin/bash
# J1(c): the p != 2 sweep.  Cells are (p, n, n') with n' not dividing n.
# Each run enumerates EVERY lambda in F_p[X] of exact degree d in [dmin,dmax].
BIN=./j1_fp_sweep
run(){ p=$1; n=$2; np=$3; dmin=$4; dmax=$5; bl=$6
  printf '### p=%s n=%s np=%s d=%s..%s brute_limit=%s\n' "$p" "$n" "$np" "$dmin" "$dmax" "$bl"
  local t0=$SECONDS
  $BIN $p $n $np $dmin $dmax $bl
  printf 'TIME %s s\n' "$((SECONDS-t0))"
}
