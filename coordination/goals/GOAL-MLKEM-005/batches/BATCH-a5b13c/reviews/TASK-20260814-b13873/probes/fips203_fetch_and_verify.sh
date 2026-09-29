#!/usr/bin/env bash
# Validator probe (TASK-20260814-b13873, target #6 / red-team-primary-target
# cross-check): independently fetch the primary FIPS 203 source and confirm,
# WITHOUT reading the producer's own quoted extract first, that (a) the
# committed inputs/MLKEM-DUAL-SOURCES-20260802 corpus really does lack the
# Compress/Decompress and rounding-operator passages (confirming the
# producer's stated protocol deviation is genuine, not a fabricated excuse),
# and (b) the primary source's actual text for section 2.3 (rounding
# operator) and section 4.2.1 (Compress/Decompress) matches what the
# producer's writeup quotes.
set -euo pipefail
cd /home/user/crypto-autoresearcher

echo "=== (a) committed corpus lacks the needed passage ==="
grep -in "compress\|round" inputs/MLKEM-DUAL-SOURCES-20260802/fips203_selected_text.txt \
  inputs/MLKEM-DUAL-SOURCES-20260802/extracts/fips203/front_matter.txt \
  && echo "FOUND (unexpected)" || echo "NOT FOUND in committed corpus (confirms producer's stated gap)"

echo
echo "=== (b) independent fetch of the primary source ==="
OUT=/tmp/claude-0/-home-user-crypto-autoresearcher/a714f03f-c705-50ff-824f-f404113138fd/scratchpad/fips203.pdf
curl -sS -o "$OUT" -w "HTTP %{http_code}, size %{size_download}\n" \
  https://nvlpubs.nist.gov/nistpubs/FIPS/NIST.FIPS.203.pdf --max-time 60
sha256sum "$OUT"

echo
echo "=== extraction (pdftotext -layout, matching the producer's own choice of tool -- pypdf/pdfminer.six independently confirmed unusable in this sandbox too, see below) ==="
TXT=/tmp/claude-0/-home-user-crypto-autoresearcher/a714f03f-c705-50ff-824f-f404113138fd/scratchpad/fips203.txt
pdftotext -layout "$OUT" "$TXT"
wc -l "$TXT"

echo
echo "=== pypdf import check (independent reproduction of the producer's claimed sandbox defect) ==="
python3 -c "import pypdf" 2>&1 | tail -3 || true

echo
echo "=== section 2.3 rounding-operator definition, as independently extracted ==="
grep -n -A2 "rounding of" "$TXT"

echo
echo "=== section 4.2.1 Compress/Decompress definition, as independently extracted ==="
sed -n '/Compression and decompression/,/Floating-point computations shall not be used/p' "$TXT"
