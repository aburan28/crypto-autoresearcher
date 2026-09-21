# EXP-ECDLP-869870 source_v2

Executor-owned implementation of protocol amendment
`PA-ECDLP-869870-v1-to-v2` (TASK-20260907-fe3512).

v1 `specification.yaml` and `source/` are read-only and are never edited.

## What this namespace runs

16 enumerated cells, one directory each:

- `RUN-ECDLP-869870-V2-splitmix-s{1..8}`
- `RUN-ECDLP-869870-V2-murmur3-s{1..8}`

Each cell: N = 2^24, T = 256, a = 1/4, caps 8W and 20W, published-weight
table at r = 2, plus global-oracle top-T share.

## Mixers

| arm | mixer | walk projection | keys |
| --- | --- | --- | --- |
| splitmix | v1 `mix64` / `mix64_int` | TOP log2N bits (`walk_projection: top_bits`) | v1 `walk_keys` GOLDEN schedule |
| murmur3 | `fmix64` from TASK-20260906-7ec3ea `j2_rederive.py` | `mix(x XOR K) mod N` / LOW log2N bits (`walk_projection: mod_N`) | `sha256` first 8 bytes, strings `ecdlp-869870-v2\|{mixer}\|walk\|{seed}` and `...\|dp\|{seed}` |

Murmur3 does not reuse `validator-7ec3ea|...` key strings. The validator's
sealed 1.6814 / -0.109 figures are a prior, not this cell's result.

## Splitmix seeds 1-5

Seeds 1-5 use the v1 GOLDEN walk-key schedule. The compute path also
consumes the v1 a = 1/8 gen/online/tie streams first so the a = 1/4
published-weight and top-T fields can be compared bit-for-bit against
already-committed `RUN-ECDLP-869870-011-N24-s1` .. `015-N24-s5`.
Disagreement is IV-determinism, not a v1 re-score. Seeds 6-8 are new
under the same walk_keys schedule.

## Wrapper

```
python3 run.py --run-id RUN-... --script run_generic_exact.py --kind fixture -- -- --mixer splitmix64 --seed 1
```

Enforces 3600 s wall and 8 GB `RLIMIT_AS`. Refuses to overwrite an
existing run directory. Writes `command.txt`, `environment.json`,
`stdout.log`, `stderr.log`, `manifest.yaml`, `raw-result.json`,
`summary.json`, plus `receipt.yaml` / `results.json`.

## O(theta)

The v1 (B4) note and `model.py` do not state a subtractable O(theta)
form for published-weight scaled cost. Corrected residual is
`not_evaluated`. Raw residual is always reported. The gate is not
marked passed by skipping the correction.

## Inference

`requested_policy: executor-implementation`. The model that answered
this session is recorded in every manifest (not a copied v1
claude-sonnet block).
