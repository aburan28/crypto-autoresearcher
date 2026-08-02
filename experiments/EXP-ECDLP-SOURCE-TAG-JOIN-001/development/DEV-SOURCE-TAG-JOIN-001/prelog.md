# Development run prelog

- Run ID: `DEV-SOURCE-TAG-JOIN-001`
- Status at prelog: `AUTHORIZED_NONCANONICAL`
- Timestamp UTC: `2026-07-18T04:27:13Z`
- Branch: `codex/source-tag-join-001`
- Base commit: `3e8fd8d8a93d6306a7f854c53b92902ec0b2e55b`
- Generator SHA-256: `9b7137ffc2fffbca05e639c9ea2e44870baa686adfc2713a80834af2a0cc59e8`
- Verifier SHA-256: `552bcb1c9669b9eaf7aae38942e0ca4b6305b1a73da00d768afa43b8bcf21faf`
- Contract SHA-256: `85669460c5cf7e04f9cc230d1b8215581807786191174843cf050e47be2c518f`
- Final pre-run review SHA-256: `3ab64c6898ce73e7ca5ad4b981a370e8c2a9e7b150607fd4ba3b82896250e490`
- Focused tests: `23/23 PASS`
- Repository tests: `123/123 PASS`
- Independent decisions: theory `GO`, benchmark `GO`, red team `GO`
- Canonical execution: `NOT AUTHORIZED`

## Command

```bash
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src python3 -B \
  experiments/EXP-ECDLP-SOURCE-TAG-JOIN-001/src/source_tag_join.py \
  --bit-sizes 10 12 14 \
  --seeds 3317584535 \
  --families x_interval square_map rational_union random_x random_scalar \
  --witness-policies symmetry_lex symmetry_hash \
  --source-tags ordinal_sum source_x_sum parameter_mix \
  --tag-counts 4 8 16 \
  --output-routers x_interval \
  --null-seeds 7301 7307 7321 7331 \
  --query-samples 4 \
  --descent-challenges 1 \
  --descent-attempt-limit 8 \
  --rho-trials 1 \
  --output experiments/EXP-ECDLP-SOURCE-TAG-JOIN-001/development/DEV-SOURCE-TAG-JOIN-001/raw-result.json
```

## Required follow-up

Replay `raw-result.json` with the independent verifier and
`--allow-development`. Preserve raw output even if the hypothesis is negative or
the implementation requires revision.
