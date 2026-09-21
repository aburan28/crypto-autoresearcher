# EXP-NCP-001 analysis — noncommutative path-algebra (correspondence quiver) search vs commutative subset-sum baseline

**Run:** `RUN-NCP-001-a` (validity_status: **valid**). Handoff `TASK-20260717-C3`, candidate C3,
frozen protocol `experiments/EXP-NCP-001/specification.yaml`.
Command: `sage experiments/EXP-NCP-001/ncp1_quiver_gb.sage`; git `9cbe0049` (dirty tree);
SageMath 10.9, Python 3.14.3, macOS 15.6 arm64; wall 5.36 s, peak RSS 767.8 MB (Sage runtime baseline).
12/12 instances completed (p ∈ {101, 431} × B ∈ {4, 8} × seeds 20260717..20260719), no timeouts.
Raw data: `runs/RUN-NCP-001-a/raw.json`.

## Per-instance measured numbers (from raw.json)

| p | B | seed | n | ops_nc | R_nc | cost_nc/rel | R_comm_d6 | cost_d6/rel | R_comm_eq (ops = ops_nc, r) | cost_eq/rel |
|---|---|------|-----|--------|------|-------------|-----------|-------------|------------------------------|-------------|
| 101 | 4 | 20260717 | 53 | 19531 | 380 | 51.40 | 43 | 59.95 | 344 (r=11) | 56.78 |
| 101 | 4 | 20260718 | 17 | 19531 | 1161 | 16.82 | 158 | 16.32 | 1160 (r=11) | 16.84 |
| 101 | 4 | 20260719 | 13 | 19531 | 1562 | 12.50 | 198 | 13.02 | 1494 (r=11) | 13.07 |
| 101 | 8 | 20260717 | 53 | 597871 | 11680 | 51.19 | 1534 | 52.26 | 11257 (r=9) | 53.11 |
| 101 | 8 | 20260718 | 17 | 597871 | 34955 | 17.10 | 4708 | 17.03 | 35191 (r=9) | 16.99 |
| 101 | 8 | 20260719 | 13 | 597871 | 46017 | 12.99 | 6162 | 13.01 | 46010 (r=9) | 12.99 |
| 431 | 4 | 20260717 | 13 | 19531 | 1742 | 11.21 | 200 | 12.89 | 1506 (r=11) | 12.97 |
| 431 | 4 | 20260718 | 439 | 19531 | 10 | 1953.10 | 3 | 859.33 | 49 (r=11) | 398.61 |
| 431 | 4 | 20260719 | 41 | 19531 | 497 | 39.30 | 64 | 40.28 | 480 (r=11) | 40.69 |
| 431 | 8 | 20260717 | 13 | 597871 | 46056 | 12.98 | 6181 | 12.97 | 45964 (r=9) | 13.01 |
| 431 | 8 | 20260718 | 439 | 597871 | 2081 | 287.30 | 193 | 415.35 | 1342 (r=9) | 445.51 |
| 431 | 8 | 20260719 | 41 | 597871 | 15359 | 38.93 | 1973 | 40.63 | 14492 (r=9) | 41.26 |

`ops` = evaluations charged (1 per NC word; 1 per (vector, ε) commutative evaluation).
`R_*` = Q-reaching relations found (eval(w, P) = Q ⇔ v(w) ≡ k mod n, verified by point arithmetic).
Equal-op-budget baseline stops at vector granularity (final shell partial), ops_eq = ops_nc ± 1.

Hit rates track the uniform-draw expectation ops/n for **both** classes in every instance with
n ≪ ops (ratio R/(ops/n) ∈ [0.88, 1.16] except the small-count n=439 instances: 0.225 and 1.528
— see unexpected observations).

## Controls (frozen specification)

**Positive control (engine verified on known k) — PASS.**
- 200 seeded random words per instance (2400 total): point-arithmetic eval == affine scalar eval, 0 mismatches.
- First ≤200 stored Q-reaching words per instance (2210 total) re-verified by point arithmetic:
  eval(w, P) == Q and v(w) ≡ k mod n, 0 mismatches.
- k recovered from the first Q-reaching word equals k mod n in 12/12 instances.

**Negative control (commutative quotient reproduces all NC relations) — PASS.**
- Value-set inclusion S_nc ⊆ S_comm on full value histograms: 0 violations in all 12 instances.
- Shadow replay: 94,472 Q-reaching words (3 instances capped at 20,000 stored words each,
  flagged `shadow_sample_capped`); every word's signed count vector has ℓ1 norm ≤ 6, lies in the
  degree-≤6 commutative vector set, and satisfies ε + Σ a_i s_i ≡ k mod n: 0 violations.
- Enumeration self-check: ops_nc == Σ_{d=0}^6 (B+1)^d exactly, all instances.

The candidate's named scoped-negative condition — "if the commutative quotient reproduces all
found relations, C3 is bookkeeping" — is therefore met over the tested scope.

## Promotion-gate arithmetic (numbers only; no verdict on the hypothesis)

Gate: *an NC relation class with NC-GB cost per relation < commutative harvest cost at equal
size, with charged exponent trend < 0.49.*

**Clause 1 — cost ratio NC / commutative at equal size (seed-mean):**

| B | p=101 vs eq-budget | p=431 vs eq-budget | p=101 vs degree-6 | p=431 vs degree-6 |
|---|---|---|---|---|
| 4 | 0.931 | 4.430 | 0.904 | 2.196 |
| 8 | 0.978 | 0.679 | 0.988 | 0.723 |

Mixed around 1; no consistent NC advantage (worst 4.43× NC penalty at B=4, p=431; best 0.68×).

**Clause 2 — charged exponent trend** (frozen two-point formula on seed-means, n̄_101 = 27.67,
n̄_431 = 164.33):

| class | B=4 | B=8 |
|---|---|---|
| NC | 1.803 | 0.802 |
| comm equal-budget | 0.927 | 1.007 |
| comm degree-6 | 1.305 | 0.977 |

Secondary log-log OLS over all 12 instances (n spans 13…439): NC slope **1.155** (R² = 0.925),
comm equal-budget **0.990** (R² = 0.999), comm degree-6 **1.088** (R² = 0.986).

Every measured exponent ≥ 0.80, i.e. all are above the 0.49 threshold; per-relation cost grows
≈ linearly in n (uniform-search behavior), not sub-birthday.

## Unexpected observations (AGENTS rule 8)

1. **Strict inclusion at (p=431, B=4, seed 20260718, n=439):** NC words reach only 350/439
   distinct values (histogram max/mean = 216/55.8) while the degree-6 commutative shadows reach
   437/439 with 7.6× fewer ops. Word-order constraints only *prune* the commutative shadow set,
   never extend it — direct quantitative evidence of bookkeeping overhead. This also explains the
   low R_nc = 10 there (k fell in a sparse region of a nonuniform value distribution).
2. **Instance-generation variance:** the frozen floor n ≥ 13 admits near-trivial subgroups:
   seeded curve selection gave n ∈ {13, 17, 41, 53, 439} (p=431 seed 20260717: N = 468 = 2²·3²·13
   → n = 13; seed 20260718: N = 439 prime → n = 439). The two-point exponent trend is
   correspondingly noisy; the 12-point scatter fit is the more robust reading (both reported).
3. **k ∈ {s_i} in 4 instances** (length-1 trivial relations exist) and k ≤ 4 in 3 instances
   (all k, s_i recorded in raw.json); controls unaffected.
4. At equal op budget the commutative baseline reaches ℓ1 radius 9–11 vs NC word degree 6:
   ~8–14 NC words per commutative shadow at these parameters.

## Deviations and infrastructure log

- **Two failed infrastructure attempts** (same day, same protocol): output stage crashed on JSON
  serialization of sage `Integer`/`RealNumber` literals (script bug, fixed by coercing constants
  to native Python types; equal-budget loop also hardened to stop at vector granularity).
  No raw result was ever written by the failed attempts; logs preserved as
  `runs/RUN-NCP-001-a/failed-attempt-{1,2}.{stdout,stderr}.txt`. Per AGENTS rule 5 these are
  infrastructure failures, not evidence. Runs used: 1 valid of maximum 8; wall ≈ 25 s of 2400 s.
- **Implementation choice (stated in frozen specification):** exhaustive truncated word
  enumeration with affine normal-form reduction realizes the degree-≤6 truncated NC-GB search
  (identical relation set; no separate Bergman overlap basis constructed).
- **Reproduction paths:** per handoff ID mapping, artifacts live under `experiments/EXP-NCP-001/`
  rather than the candidate-text path `experiments/ecdlp_ncpath/`; script name `ncp1_quiver_gb.sage`
  preserved. Audit (positive/negative controls) is built into the main script rather than a
  separate `ncp1_verify.sage`.
- **Executor-chosen parameters** (candidate fixed only p ∈ {101, 431} and degree 6): B ∈ {4, 8},
  seeds {20260717, 20260718, 20260719}, subgroup floor n ≥ 13 — frozen in specification.yaml.
- **Shadow-replay cap:** 3 instances with R_nc > 20,000 replayed on the first 20,000 stored words
  (flagged); value-level inclusion was still checked on complete histograms.

## Boundaries (AGENTS rules 6, 7)

Toy primes {101, 431}; subgroup orders 13–439; quiver {T_{P_i}} ∪ {neg} only (no isogeny arrows);
word degree ≤ 6; B ∈ {4, 8}; 3 seeds; single run. No improvement meeting the predefined threshold
was observed over the tested instances, parameters, implementation, and resource budget. This
closes only the tested scope: it says nothing about degree > 6, larger B, isogeny-arrow quivers,
non-prime fields, or crypto-scale curves.
