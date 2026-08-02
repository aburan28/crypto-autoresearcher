#!/bin/bash
cd "$(dirname "$0")"
run(){ tag="$1"; shift; echo "{\"tag\":\"$tag\",\"utc\":\"$(date -u +%FT%TZ)\",\"argv\":\"$*\"}" >> val_cmds.jsonl
       out=$(./val_count "$@"); echo "$tag $out" >> val_results.txt; echo "$tag $out"; }
# fresh validator keys, chosen by me, unrelated to producer KDF
K1=0f1e2d3c4b5a69788796a5b4c3d2e1f0
K2=a3f19c4e77b2d05186ec3410fa5b72d9
K3=5c0d8e2b41967af3082dc5e7b19640af
K4=deadbeefcafebabe0123456789abcdef
B1=00112233445566778899aabbccddeeff
B2=7f3e1d5a09c6b2843fe0517a6b9c2d48
B3=112233445566778899aabbccddeeff00
run r4_bijection      4 3 key $K1 $B1 id
run r5_A              5 0 key $K1 $B1 id
run PRP_aes10_A      10 2 key $K2 $B2 id
run BALLS_null_A  5 0 balls 0123456789abcdef $B1 id
run r5_B              5 2 key $K2 $B2 id
run r6_A              6 2 key $K1 $B1 id
run r5_C              5 3 key $K3 $B3 id
run SIBLING_fd_r5     5 1 key $K1 $B1 fd
run PRP_aes10_B      10 0 key $K3 $B3 id
run BALLS_null_B  5 0 balls fedcba9876543210 $B1 id
run r5_D              5 1 key $K4 $B2 id
run r4_bijection_B    4 1 key $K2 $B2 id
run r2j1_exact        2 1 key $K1 $B1 id w64
run r3_exact          3 3 key $K1 $B1 id w64
run r6_B              6 0 key $K3 $B3 id
echo "DONE $(date -u +%FT%TZ)"
