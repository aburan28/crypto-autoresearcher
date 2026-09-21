# DEV-OUTER-TRANSLATOR-001

Verified noncanonical development evidence for
`EXP-ECDLP-OUTER-TRANSLATOR-001`.

This is a generated-toy 8/10/12-bit sweep. It is not a canonical run,
coordinate-continuation signal, exponent result, ECDLP break, or deployed-key
claim.

## Artifacts

- `prelog.json`: clean commit, exact configuration, child commands, host, and
  22 source hashes recorded before launch;
- `raw-result.json.gz`: deterministic byte-preserving gzip of the 258 MiB raw
  generator artifact;
- `run-manifest.json`: child exits/resources, source-stability recheck, and
  hashes of the original run artifacts;
- `verification-receipt.json`: independent replay and affine/root/witness
  verification receipt;
- `analysis.jq`: reproducible post-run reduction;
- `analysis.json`: generated reduction used by the result note;
- `../../development-result-v1.md`: scoped interpretation and next question;
- `../../development-red-team-v1.md`: independent post-run interpretation
  audit.

The uncompressed `raw-result.json` is retained locally but ignored by Git. Its
authoritative SHA-256 is
`8556a9e430a25ffe97b06b5508a76186784804b417ca175e05736c2332fa67f0`.
The checked-in gzip SHA-256 is
`63929f64b70927dff9ca31b7c39242064fc05a50be2d8c0e363cea263aec4400`;
decompression reproduces the authoritative raw hash exactly.

Other checked-in hashes:

- run manifest: `09511cbd5d78fdb01ea6a6cc52f66bed8fa4a7a5d0974551bbd68b4f6f6fe851`;
- verifier receipt: `53871d36b169c1fea2954acf1a394a557512105edfe1640448c3e80cdf1f7211`;
- analysis program: `04716c133644b393991e7e00cc3b88311e536d9a9019d22dc334d1f9a3787b42`;
- analysis output: `7c0c747aee61ab2ad1261442ac8e56cbe99d45c8c23096a3bc4ea46e74b83455`.

## Replay

```bash
gzip -dc \
  experiments/EXP-ECDLP-OUTER-TRANSLATOR-001/development/DEV-OUTER-TRANSLATOR-001/raw-result.json.gz \
  > /tmp/DEV-OUTER-TRANSLATOR-001.raw-result.json

PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src python3 -B \
  experiments/EXP-ECDLP-OUTER-TRANSLATOR-001/src/verify_outer_translator.py \
  --input /tmp/DEV-OUTER-TRANSLATOR-001.raw-result.json \
  --output /tmp/DEV-OUTER-TRANSLATOR-001.verification.json \
  --allow-development

jq -s -f \
  experiments/EXP-ECDLP-OUTER-TRANSLATOR-001/development/DEV-OUTER-TRANSLATOR-001/analysis.jq \
  /tmp/DEV-OUTER-TRANSLATOR-001.raw-result.json \
  /tmp/DEV-OUTER-TRANSLATOR-001.verification.json \
  experiments/EXP-ECDLP-OUTER-TRANSLATOR-001/development/DEV-OUTER-TRANSLATOR-001/run-manifest.json
```
