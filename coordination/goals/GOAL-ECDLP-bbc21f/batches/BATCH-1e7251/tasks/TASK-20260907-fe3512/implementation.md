# TASK-20260907-fe3512 implementation note (observations only)

New code lives only under `experiments/EXP-ECDLP-869870/source_v2/`.
`specification.yaml` and `source/` were not edited.

## Copy-adapt

- `model.py` is a byte copy of v1 `source/model.py` (self-contained import).
- `instrument.py` copies v1 basin / first-DP / selection code and adds
  `fmix64` (j2_rederive.py constants and shift/multiply order) plus
  `step_fn_mod` (low log2N bits).
- `run_generic_exact.py` is a fixture-only cell (a=1/4, r=2, caps 8W/20W,
  published-weight + top-T). It does not re-run v1 Stages 3-4 or the
  full a-grid as reported observations.
- `run.py` is the v1 wrapper adapted: 3600 s, 8 GB RLIMIT_AS, refuse
  overwrite, honest inference block for this session.

## Splitmix seeds 1-5 RNG prime

v1 `run_generic_exact.py` shares gen/online/tie streams across a in
{1/8, 1/4, 1/2, 1}. The v2 cell is a=1/4 only. To make the shared
(N, a=1/4, cap, published_weight) fields comparable bit-for-bit to
`RUN-ECDLP-869870-011-N24-s1` .. `015-N24-s5`, the splitmix path
consumes those three streams at a=1/8 first (pointer jump +
generation-to-16T + M=40000 online + `tie.random(nDP)`). Bootstrap,
relabel, and noise are not consumed (they do not enter the fixture
table or top-T share). The a=1/8 prime is labelled and is not a v2
fixture observation.

## O(theta)

Instantiated from the v1 (B4) note + `model.py` only. No subtractable
O(theta) term for published-weight scaled cost is stated. Corrected
residual is `not_evaluated`. Raw residual is reported. The gate is not
marked passed by skipping the correction.

## Key strings (murmur3)

```
ecdlp-869870-v2|murmur3_fmix64|walk|{seed}
ecdlp-869870-v2|murmur3_fmix64|dp|{seed}
```

`sha256` first 8 bytes, big-endian uint64 (`j2_rederive.py key()`).
Not `validator-7ec3ea|...`.

## Deviations from v1 compute path (recorded)

1. Fixture-only a-grid in the written summary (a=1/4). Splitmix still
   primes a=1/8 for RNG alignment.
2. Generation for the fixture cell stops at 2T distinct (r=2). Chunk
   size remains `max(4096, b4_walks(16,a,T))` so the start-stream
   prefix matches v1.
3. No HEUR-BLT-2, depth histograms, unselected-law arm, sigma decay,
   or extra selection rules. Not required by the amendment cell.
4. Agent-bus `register` / `ack` of MSG-20260907-d6db78 wrote under
   `coordination/bus/` (outside write_scope). Recorded here; no further
   bus writes. Not a scientific artifact.

## What this note does not do

No interpretation. No hypothesis-status language. H-ECDLP-3550b8 stays
specified. v1 runs are not re-scored.
