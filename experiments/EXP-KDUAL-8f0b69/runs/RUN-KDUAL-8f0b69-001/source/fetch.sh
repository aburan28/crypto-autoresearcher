#!/bin/sh
# Re-fetch the exact bytes read by RUN-KDUAL-8f0b69-001.
C=3e48ef421ec256afddb3e7d2249a77eab6e9ba12
for f in __init__ lwe lwe_dual lwe_primal lwe_guess lwe_bkw reduction cost nd; do
  curl -sS -o "le_$f.py" \
    "https://raw.githubusercontent.com/malb/lattice-estimator/$C/estimator/$f.py"
done
