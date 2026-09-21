#!/bin/bash
cd "$(dirname "$0")"
s=$(date -u +%s)
out=$(timeout 432 ./cnt aesni 10 0 d6e8b0bc6cb2749dc3e4b1d5359ddf85 502ddf7c0f432fb9a866f39e33cd0965 02030101010203010101020303010102 8 0 4); st=$?
e=$(date -u +%s)
python3 mkrow.py N1 $st $s $e "$out"
echo done $st
