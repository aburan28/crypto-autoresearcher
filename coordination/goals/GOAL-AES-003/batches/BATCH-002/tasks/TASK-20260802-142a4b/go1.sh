#!/bin/bash
cd "$(dirname "$0")"
NOW=$(date -u +%s); TMO=$((1785693426-NOW-140))
exec ./pair.sh M0_r5_j0 $TMO soft 5 0 6fe52e2e9b3ea04085c370f9bc609245 e35f00e7631cdd862e59d126e72b8fc9 00030101010203010101020303010102 8 0 1
