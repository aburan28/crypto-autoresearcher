#!/bin/bash
cd "$(dirname "$0")"
K=0f1e2d3c4b5a69788796a5b4c3d2e1f0
B=00112233445566778899aabbccddeeff
{ echo "# UTC $(date -u +%FT%TZ) r2 j0=1 exact positive control (predict C(2^32,2)=9223372034707292160)"
  ./val_count 2 1 key $K $B id w64
  echo "# UTC $(date -u +%FT%TZ) r2 j0=0 (predict 0)"
  ./val_count 2 0 key $K $B id w64
  echo "# UTC $(date -u +%FT%TZ) r3 j0=3 exact positive control (predict 36028794871480320)"
  ./val_count 3 3 key $K $B id w64
} >> val_controls.jsonl 2>&1
