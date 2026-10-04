#!/bin/sh
# Regenerate binary-curve-params.txt from the local OpenSSL build.
# Every curve below is a named, standardized binary-field curve carried by
# OpenSSL 3.0.13; the file is a DERIVED artifact and is regenerated, not edited.
set -e
for c in sect163k1 sect233k1 sect283k1 sect409k1 sect571k1 \
         sect163r2 sect233r1 sect283r1 sect409r1 sect571r1 \
         sect193r1 sect193r2 sect239k1 sect131r1 sect131r2 \
         c2pnb163v1 c2pnb163v2 c2pnb163v3 c2pnb176v1 \
         c2tnb191v1 c2tnb191v2 c2tnb191v3 c2pnb208w1 \
         c2tnb239v1 c2tnb239v2 c2tnb239v3 c2pnb272w1 \
         c2pnb304w1 c2tnb359v1 c2pnb368w1 c2tnb431r1; do
  echo "===== $c ====="
  openssl ecparam -name "$c" -param_enc explicit -text -noout
done
