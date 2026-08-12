# DEV-SOURCE-TAG-JOIN-001

Verified noncanonical development evidence for
`EXP-ECDLP-SOURCE-TAG-JOIN-001`.

This is a one-seed toy sweep. It is not a canonical run, promoted structural
signal, useful compiler result, asymptotic result, or ECDLP break.

## Artifacts

- `prelog.md`: command, source hashes, and pre-run authorization boundary;
- `raw-result.json.gz`: byte-preserving gzip of the 146 MiB generator output;
- `verification.json`: independent deterministic replay certificate;
- `analysis.jq`: reproducible post-run reduction;
- `analysis.json`: generated reduction used by the result note;
- `../../development-result-v1.md`: scoped interpretation and next experiment;
- `../../development-red-team-v1.md`: independent interpretation audit;
- `../../handoff.md`: outer-aware successor contract requirements.

The uncompressed `raw-result.json` is retained locally but ignored by Git because
it exceeds normal GitHub object limits. Its SHA-256 is
`880d466fd5f032ae28b677664f8713950b074a87ecad3d3a079144a24e6d7fa2`.
The checked-in gzip SHA-256 is
`b2b274c2a64258eb0c5af00bd4eedc99319521cd461c7f9fa8e6cec4c95b9f31`.
The verifier receipt SHA-256 is
`d938cad2a704e748e1f59d41cde4736297671979b9e9f786fa9b8dd1e44031b1`,
and the checked-in analysis output SHA-256 is
`159bdc00318f295a702ea9e97998f29eb8347a6d0127fb223360b4428ee9f924`.

## Replay

```bash
gzip -dc \
  experiments/EXP-ECDLP-SOURCE-TAG-JOIN-001/development/DEV-SOURCE-TAG-JOIN-001/raw-result.json.gz \
  > /tmp/DEV-SOURCE-TAG-JOIN-001.raw-result.json

PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src python3 -B \
  experiments/EXP-ECDLP-SOURCE-TAG-JOIN-001/src/verify_source_tag_join.py \
  --input /tmp/DEV-SOURCE-TAG-JOIN-001.raw-result.json \
  --allow-development \
  --output /tmp/DEV-SOURCE-TAG-JOIN-001.verification.json

jq -s -f \
  experiments/EXP-ECDLP-SOURCE-TAG-JOIN-001/development/DEV-SOURCE-TAG-JOIN-001/analysis.jq \
  /tmp/DEV-SOURCE-TAG-JOIN-001.raw-result.json \
  /tmp/DEV-SOURCE-TAG-JOIN-001.verification.json
```
