# EXP-WESO-9e2d6d — Coordinator analysis (evidence review)

| field | value |
| --- | --- |
| experiment | EXP-WESO-9e2d6d, specification v1 (sha256 `630a91c9…4e756`), frozen by DEC-20260926-ec2847 |
| hypothesis | H-WESO-516558 (parts H-S sampler, H-1 Heuristic 1 operational form) |
| runs reviewed | RUN-WESO-aa2237 (Stage A), RUN-WESO-f37773 (Stage B), RUN-WESO-e65afd (Stage C); RUN-WESO-0b4b33 (Stage D) not run |
| executor card | TASK-20260926-41c7e7 |
| evidence / decision | EV-WESO-af78c1 / DEC-20260926-c8d4b0 |
| branch state read | `claude/pqc-attack-targets-l7vp2m`, run packages archived through 2ac3071f7 (as reported by the dispatching session; this act ran no git command) |
| author | Coordinator, 2026-09-26 |

**Provenance of numbers.** Every measured value below is copied from the run
packages (`raw-result.json`, `execution_report.yaml`,
`execution_report_addendum.yaml`, `checker_result.json`, manifests). Values
marked **[HC]** are hand arithmetic by the Coordinator in this act from those
recorded values (Wilson intervals, first-order asymptotic terms, ratios). They
are reproducible by any reader from the cited fields. They are not run
artifacts, and no program was executed in this act.

**Binding frame.** Stage C's mechanical outcome is **FC-VOID** under SR-4. The
frozen protocol says FC-VOID means "no H-1 reading of either sign; reported as
an instrument limit". Every Stage-C smoothness number below is therefore an
**observation only**. Nothing in this document reads Heuristic 1 as supported
or weakened. Stage B's sampler-mixing result falls outside the SR-4 stop (it
was gated earlier, by gate_G_B) and is reported as a measured result within
its scope.

---

## 1. Observation

### O-1 Run-set validity (re-verified before any interpretation)

| check | finding |
| --- | --- |
| Expected run count | At most 4 runs, one per stage, with pre-allocated ids (spec `run_ids`, EX-7). Three ran: A, B and C. D was not created. The reason is a protocol stop (SR-4), not a failure (see I-5). No other run id exists. |
| Schema | All three manifests carry id, experiment_id, status, code (commit, dirty, per-file sha256 at start and end), command, environment (gp 2.15.4 and its sha256, python 3.11.15, numpy 2.4.6, sympy 1.14.0, mpmath 1.3.0), inputs, seeds_used, timing, resources, result (validity and certificate kind none), and inference. `RUN_REQUIRED_TOP` is satisfied. Post-archive notes live in the manifest addenda. No committed manifest byte was changed. |
| Code identity | The implementation was untracked at run time (`dirty: true`), so the per-file sha256 values are the binding identity. Stage A ran earlier code (qfminim flag 0). That code is preserved and hash-verified in `runs/RUN-WESO-aa2237/code_snapshot/`. Stage B re-applied I-1 with the frozen code and found 0 mismatches over all 1569 WISDE types. The analysis_freeze (Stage-B manifest) matches Stage C's start and end hashes, so IV-5 is not triggered. |
| Seeds | Stage B used U-1, B-MAIN, B-NULL, PC-2 and START-1. Stage C used CLS, DET-1, and C64-R1/R2/NULL/KS1/PC3/START2, C96-R1/R2/NULL and C128-R1/R2/NULL. The values equal the specification. Per-draw seeds are stored per record. DET-1 found byte-identical deterministic fields (1 worker vs 3). The reproduction spot-check (100 samples per prime, fresh process) passed at all three primes. SEED-2 found 0 duplicate order hashes and δ = 1 in 0 cases at each prime. |
| Raw/summary agreement | **Stage C:** the IV-4 checker (fresh process) recomputed every smooth count, TC-1..TC-3, SEED-2, δ_max and NULL-1 bit-length matching from the stored factorisations. It found 0 mismatches and re-verified every factorisation with sympy (0 failures). **Stage A:** exact identities; `types.jsonl` retained. **Stage B:** NO independent recomputation of the TV tables exists (the checker covers Stages C and D only). Its per-sample file (85 122 367 bytes, sha256 `365dc151…5c83`) sits outside the repository in the session scratchpad, per the spec's size_note. It is present at the time of this review. Regeneration reproduces every field except `wall_s`. |
| Control comparability | NULL-1, NULL-2, replicate halves and arms share the prime, the frozen code and the seed derivation. NULL-2 is drawn as `1 + randbelow(X)`, an unbiased rejection sampler on bit-length(X−1) bits (`implementation/common.py` lines 66-74, `stage_c.py` line 145, read in this act). NULL-2 is therefore uniform on [1, X]. |
| Disclosed deviations | DET-1 used 3 workers, not 4 (host shared); Stage C ran on 3 workers. Per-prime record files replace single files. Stage-C `cpu_seconds_children_*` undercounts (gp children not reaped); wall time (2105.8 s) and peak RSS (2.56 GB) are valid. Development smoke tests ran only at non-frozen primes (implementation.md §11). Float-boundary defect at (p64, u = 3); see C-5. |
| Certificates | None claimed. These are pure measurement runs (`certificate.kind: none`). Factorisations are verified per record. |

**Validity verdict (Coordinator).** Stages A and C are valid and
schema-complete. Their raw/summary agreement is machine-checked (Stage C) or
exact (Stage A). Stage B is valid as reported, but its raw/summary agreement
has not been independently recomputed, and its per-sample file lives in
ephemeral storage. That gap is carried as a confound in EV-WESO-af78c1 and
closed by a next action in DEC-20260926-c8d4b0. No defect makes any run
invalid.

### O-2 Stage A (RUN-WESO-aa2237) — exact ground truth

- **I-1:** 0 mismatches. There were 56, 186, 456 and 871 types at p = 1019, 4099, 10007 and 20011, all on the primary route (WISDE bytes hash-equal to the committed values).
- **A-1:** exact at all four primes (86, 342, 835, 1668).
- **A-2:** max N1 = 6, 11, 15, 20, against bounds 7, 12, 17, 21.
- **A-3** (reported, not a gate): the Eichler mass equals (p−1)/24 exactly at all four primes.
- No two WISDE types shared a Gross-lattice label.

### O-3 Stage B (RUN-WESO-f37773) — sampler mixing, N_B = 10^4 per (p, k)

| p | q99.9 floor δ (type) | TV_δ at k=12 (type) | TV_δ at k=16 (type) | max TV_δ over k ≥ 16 (type) | k* | k*/log2 p |
| --- | --- | --- | --- | --- | --- | --- |
| 1019 | 0.01836 (0.03843) | 0.02468 (0.07312) | 0.00436 (0.03265) | 0.01419 (0.03834 at k=64) | 16 | 1.601 |
| 4099 | 0.02420 (0.06288) | 0.02737 (0.15556) | 0.01716 (0.05833) | 0.01716 (0.05833) | 16 | 1.333 |
| 10007 | 0.02664 | 0.03946 | 0.01652 | 0.01726 | 16 | 1.204 |
| 20011 | 0.02451 | 0.02983 | 0.02059 | 0.02059 | 16 | 1.120 |

- **PC-1** (k ∈ {0, 1, 2}) was detected at all primes.
- **PC-2** (5% contamination by k = 2 draws at k = 64): TV_δ = 0.02236, 0.04210, 0.04770 and 0.04340, above the floor at 4 of 4 primes.
- **START-1** (p = 10007, start order O_0′): k*′ = 16 = reference.
- **U-0** passed at 4 primes. **U-1** passed (χ² p = 0.973, 0.758, 0.530; support equals the independent enumeration). **U-2** found 0 failures in 760 000 orders.
- **gate_G_B: PASS.** c_hat = 1.6011, giving k_C = 308, 462, 615 (and 1201 at 250 bits).

### O-4 Stage C (RUN-WESO-e65afd) — instrument gates and controls

- V-RHO-1..3 PASS. V-RHO-2 reproduced the source's 1/69232 to within 7.9e-7 relative.
- CLS-1 PASS: 10^4 cases, 0 errors, including 2794 cases with B equal to a factor.
- DET-1 PASS. PC-3 PASS (KS D = 1.0, p ≈ 0).
- KS-1 and START-2 NOT_REJECTED at p64 (family of 4; minimum p = 0.124 and 0.280).
- SEED-1: no rejection at any prime (minimum p = 0.077, 0.107, 0.426).
- C-2: 0 violations. δ_max = 2 011 747 / 3 318 526 939 / 5 279 258 401 826, each ≤ X.
- IV-1: 0 unverified factorisations.
- **NULL-2 bounds:** PASS at p64 and p128. **FAIL at p96**, in exactly one admissible cell: u = 4.5, B = 131.3286, X = 3 408 917 801, S_NULL2 = 336 of 100 000, f_NULL2 = 0.00336, ρ(4.5) = 0.00137012, ratio 2.4523, band [0.7, 2.0].
- **Outcome code: FC-VOID (SR-4).** All three primes are otherwise valid.

### O-5 Stage C smoothness measurements (observations only — FC-VOID; no H-1 reading)

These are the cells admissible under the recorded tables, plus (p64, u = 3), which is admissible exactly (C-5). Wilson and T1 intervals are two-sided 99%.

| prime | u | B | f_emp [Wilson 99%] | ρ(u) | R_max | T1 [99%] | f_NULL2/ρ |
| --- | --- | --- | --- | --- | --- | --- | --- |
| p64 | 1.5 | 16384 | 0.62059 [0.6166, 0.6245] | 0.59453 | 1.044 | 0.981 [0.967, 0.995] | 1.056 |
| p64 | 2 | 1448.2 | 0.33596 [0.3321, 0.3398] | 0.30685 | 1.095 | 0.966 [0.947, 0.985] | 1.112 |
| p64 | 2.5 | 337.8 | 0.15485 [0.1519, 0.1578] | 0.13032 | 1.188 | 0.948 [0.921, 0.976] | 1.233 |
| p64 | 3 | 128.0 | 0.06673 [0.0647, 0.0688] | 0.04861 | 1.373 | 0.922 [0.883, 0.964] | 1.477 |
| p96 | 1.5 | 2.27e6 | 0.61438 [0.6104, 0.6183] | 0.59453 | 1.033 | 0.991 [0.976, 1.006] | 1.035 |
| p96 | 2 | 58386 | 0.32814 [0.3243, 0.3320] | 0.30685 | 1.069 | 0.987 [0.967, 1.007] | 1.070 |
| p96 | 2.5 | 6502.0 | 0.14405 [0.1412, 0.1469] | 0.13032 | 1.105 | 0.975 [0.946, 1.004] | 1.126 |
| p96 | 3 | 1505.0 | 0.05668 [0.0548, 0.0586] | 0.04861 | 1.166 | 0.960 [0.915, 1.007] | 1.224 |
| p96 | 3.5 | 529.2 | 0.02061 [0.0195, 0.0218] | 0.01623 | 1.270 | 0.939 [0.867, 1.017] | 1.370 |
| p96 | 4 | 241.6 | 0.00699 [0.0063, 0.0077] | 0.00491 | 1.423 | 0.890 [0.778, 1.019] | 1.761 |
| p96 | 4.5 | 131.3 | 0.00228 [0.0019, 0.0027] | 0.00137 | 1.664 | 0.884 [0.696, 1.121] | **2.452** |
| p128 | 1.5 | 3.13e8 | 0.60754 [0.6036, 0.6115] | 0.59453 | 1.022 | 0.986 [0.971, 1.000] | 1.020 |
| p128 | 2 | 2.35e6 | 0.32028 [0.3165, 0.3241] | 0.30685 | 1.044 | 0.981 [0.961, 1.001] | 1.037 |
| p128 | 2.5 | 125153 | 0.13904 [0.1362, 0.1419] | 0.13032 | 1.067 | 0.970 [0.940, 1.000] | 1.071 |
| p128 | 3 | 17696 | 0.05307 [0.0513, 0.0549] | 0.04861 | 1.092 | 0.953 [0.907, 1.001] | 1.116 |
| p128 | 3.5 | 4375.5 | 0.01840 [0.0173, 0.0195] | 0.01623 | 1.134 | 0.952 [0.875, 1.036] | 1.152 |
| p128 | 4 | 1534.3 | 0.00636 [0.0057, 0.0070] | 0.00491 | 1.295 | 0.983 [0.850, 1.137] | 1.212 |
| p128 | 4.5 | 679.1 | 0.00205 [0.0017, 0.0025] | 0.00137 | 1.496 | 1.035 [0.797, 1.345] | 1.431 |
| p128 | 5 | 353.8 | 0.00067 [0.00049, 0.00092] | 0.000355 | 1.889 | 1.098 [0.686, 1.765] | 1.917 |

Further observations, recorded as data and not interpreted:

- In every one of the 33 recorded cells, the Wilson upper bound of f_emp is ≥ ρ(u).
- The recorded T1 upper bound is < 1 at p64 u ∈ {1.5, 2, 2.5}, at p64 u = 3 (C-5), and at p128 u = 2.5 (0.99999).
- The OLS slope of ln T1 on u over the admissible cells at p96 is −0.0419 per unit u, 99% CI [−0.0646, −0.0192], n = 7. At p64 (n = 3) and p128 (n = 8) the CI contains 0.
- TC-3 (δ prime vs NULL-1 prime) differs by +0.01437, +0.00953 and +0.00727 at p64, p96 and p128. The 99% Wald intervals are [0.0112, 0.0175], [0.0070, 0.0121] and [0.0050, 0.0095].
- TC-1 is inadmissible at every prime (M = 2, 19, 71 < 128).
- TC-2 is admissible only at p128. The observed counts 16, 46 and 147 lie against the thresholds m = 5, 20 and 100, so no deficit is flagged.
- Per-sample wall time: mean 0.0140, 0.0163 and 0.0205 s.
- Size-matched ρ-prediction ratio S_δ/Σρ(ln δ_i/ln B) at admissible cells ranges from 0.81 to 0.96.

### O-6 Stage D

Not run. RUN-WESO-0b4b33 has no directory. The FG-D pilot was not executed, so no feasibility datum exists.

---

## 2. Comparison

### C-1 Stage B against its frozen gate

Every gate_G_B condition holds on the recorded values:

- (1) PC-1 and PC-2 were detected.
- (2) k* exists at every prime, and k* ≤ 128.
- (3) k*(20011)/log2 20011 = 1.120 ≤ 2 × min = 2.240.
- (4) START-1 passed.
- (5) U-0..U-2 passed.

The mixing threshold sits in the grid gap (12, 16] at every prime. At k = 12 the δ-level TV exceeds the floor everywhere; at k = 16 it is below the floor everywhere.

Two margins are tight:

- The type-level TV at p = 1019, k = 64 is 0.03834 against a floor of 0.03843, a margin of 0.00009.
- At p = 4099 the type-level TVs for k ≥ 16 lie in [0.0486, 0.0583], which is 77-93% of the floor 0.0629.

### C-2 The failing NULL-2 cell against sampling noise [HC]

S_NULL2 = 336 of N = 10^5, so p̂ = 0.00336. The two-sided 99% Wilson interval is [0.0029205, 0.0038654]. Dividing by ρ(4.5) = 0.00137012 gives a ratio interval of **[2.13, 2.82]**. The lower bound exceeds the band limit 2.0, so the failure is not a sampling fluctuation. By contrast, the passing cell p128 u = 5 (S = 68) has a ratio interval of [1.40, 2.62], which straddles 2.0: its pass is statistically unresolved against the same band.

### C-3 NULL-2 (cumulative smooth fraction) against the first-order de Bruijn term [HC]

NULL-2 estimates Ψ(X, B)/X for integers uniform on [1, X], with u = ln X / ln B. The first-order asymptotic is

  Ψ(X, B) = X ρ(u) + (1 − γ) X ρ(u − 1) / ln X + (higher order),

so R1 := 1 + (1 − γ) ρ(u−1) / (ρ(u) ln X), with γ = 0.5772157.

The general form is recalled from de Bruijn (1951) and Tenenbaum's monograph, ch. III.5 (provenance **recalled**, not verified in this program). It is **re-derived here for 1 < u < 2**, where it is elementary:

- Ψ(X, B) = ⌊X⌋ − Σ_{B<p≤X} ⌊X/p⌋.
- Σ_{B<p≤X} 1/p = ln u + (exponentially small), by Mertens and the prime number theorem.
- Σ_{B<p≤X} {X/p} ≈ (X/ln X) ∫_1^∞ {v}/v² dv = (1 − γ) X / ln X.
- Hence Ψ/X = 1 − ln u + (1 − γ)/ln X + o(1/ln X), which is ρ(u) + (1−γ)ρ(u−1)/ln X, since ρ(u−1) = 1 on this range.

Here ln X = 14.5561 (p64), 21.9497 (p96) and 29.3432 (p128).

| prime | u | ln B | observed f_NULL2/ρ | first-order R1 | observed / R1 |
| --- | --- | --- | --- | --- | --- |
| p128 | 1.5 | 19.56 | 1.020 | 1.024 | 0.996 |
| p128 | 2 | 14.67 | 1.037 | 1.047 | 0.990 |
| p96 | 1.5 | 14.63 | 1.035 | 1.032 | 1.002 |
| p128 | 2.5 | 11.74 | 1.071 | 1.066 | 1.005 |
| p96 | 2 | 10.98 | 1.070 | 1.063 | 1.006 |
| p128 | 3 | 9.78 | 1.116 | 1.091 | 1.023 |
| p64 | 1.5 | 9.70 | 1.056 | 1.049 | 1.007 |
| p96 | 2.5 | 8.78 | 1.126 | 1.088 | 1.035 |
| p128 | 3.5 | 8.38 | 1.152 | 1.116 | 1.033 |
| p96 | 3 | 7.32 | 1.224 | 1.122 | 1.091 |
| p128 | 4 | 7.34 | 1.212 | 1.143 | 1.060 |
| p64 | 2 | 7.28 | 1.112 | 1.095 | 1.016 |
| p128 | 4.5 | 6.52 | 1.431 | 1.171 | 1.222 |
| p96 | 3.5 | 6.27 | 1.370 | 1.155 | 1.187 |
| p128 | 5 | 5.87 | 1.917 | 1.199 | 1.598 |
| p64 | 2.5 | 5.82 | 1.233 | 1.133 | 1.089 |
| p96 | 4 | 5.49 | 1.761 | 1.191 | 1.479 |
| p96 | 4.5 | 4.88 | **2.452** | 1.228 | **1.997** |
| p64 | 3 | 4.85 | 1.477 | 1.183 | 1.248 |
| p96 | 5 (inadm.) | 4.39 | 3.496 | 1.267 | 2.760 |
| p64 | 3.5 (inadm.) | 4.16 | 1.966 | 1.233 | 1.594 |
| p64 | 4 (inadm.) | 3.64 | 2.946 | 1.287 | 2.289 |

The pattern is systematic:

- The observed ratio exceeds 1 in every cell, which is the classical direction.
- For ln B ≳ 9 it agrees with R1 to within 1-2%. The largest discrepancy there is about 2.2 binomial SD, at p128 u = 2.
- At each prime, the excess over R1 grows monotonically as B falls: p64 goes 1.007 → 2.29, p96 goes 1.002 → 2.76, p128 goes 0.996 → 1.60.
- At fixed B ≈ 130 the excess grows with u: 1.25 (p64, u = 3), 2.00 (p96, u = 4.5), and 3.23 at p128, u = 6 (4.07/1.260; S = 8, noisy, inadmissible).

### C-4 NULL-1 (point smoothness probability) against the first-order point-density term [HC]

Differentiating the C-3 expansion in X shows that the smooth-number density near a given size t is

  ρ(u_t) − γ ρ(u_t − 1)/ln t, with u_t = ln t / ln B.

This lies BELOW ρ(u_t). For 1 < u_t < 2 there is an independent elementary check. An integer n ≈ t is non-smooth iff n = m·q with q a prime in (B, n], so the probability is Σ_{m<t/B} 1/(m ln(t/m)). The gap between this integer sum and its integral over m is γ/ln t, giving density 1 − ln u_t − γ/ln t.

The ratio S_NULL1 / Σ_i ρ(ln δ_i/ln B) compares a size-matched uniform-integer count with the spec's PRED-2 ρ-sum (same sizes up to bit-level matching; approximate check):

| prime | u | observed S_NULL1/Σρ | first-order 1 − γ ρ(u−1)/(ρ(u) ln X) |
| --- | --- | --- | --- |
| p64 | 1.5 | 0.9337 | 0.9333 |
| p64 | 2 | 0.8917 | 0.8708 |
| p96 | 1.5 | 0.9563 | 0.9558 |
| p96 | 2 | 0.9218 | 0.9143 |
| p96 | 2.5 | 0.8906 | 0.8800 |
| p128 | 1.5 | 0.9715 | 0.9669 |
| p128 | 2 | 0.9420 | 0.9359 |

Agreement is within 0.1-2.5% where B is large. The ratio then departs upward as B falls, for example 0.864, 0.867, 0.909 and 0.941 at p96 u = 3, 3.5, 4 and 4.5.

### C-5 (p64, u = 3) admissibility, exact

With u = 3, B = exp(ln(p/2)/9) = (p/2)^{1/9}. So B ≥ 128 = 2^7 ⟺ p/2 ≥ 2^63 ⟺ p ≥ 2^64. The prime is p64 = 18 446 744 073 709 551 667 = 2^64 + 51, so **B ≥ 128 holds exactly**. N·ρ(3) = 4860.8 ≥ 30. The cell is **admissible**, and the recorded table (float B = 127.99999999999997) is wrong.

For the other primes, the cell with B = 128 would need u = log2(p/2)/21 = 95/21 (p96) or 127/21 (p128). Neither is on the grid, so no other cell is at the boundary; this confirms the Executor's check. Smooth counts are unaffected, because the primes below either value of B are the same set {primes ≤ 127}. The (p64, u = 3) NULL-2 ratio is 1.477, inside the band. **FC-VOID is unchanged** either way: its sole cause is p96 u = 4.5.

---

## 3. Inference

### I-1 Stage B is a measured sampler result within its toy scope

Scoped statement:

> At the four primes p ∈ {1019, 4099, 10007, 20011} (all ≡ 3 mod 4), with 10^4 draws per (p, k), the right order of a uniformly random cyclic left O_0-ideal of norm 2^k (the endpoint of a uniform non-backtracking norm-2 walk) was indistinguishable from the exhaustive Eichler-mass-weighted δ law at every grid k ≥ 16, and distinguishable at every grid k ≤ 12. At 1019 and 4099 the same held for the Gross-lattice type law. Indistinguishability is at the resolution of the 99.9% multinomial null floor: 0.018-0.027 TV at the δ level and 0.038-0.063 at the type level. Known-biased samplers (k ≤ 2, and 5% k = 2 contamination) were detected at all four primes. So k*(p) = 16 at every tested prime, k*/log2 p ∈ [1.12, 1.60], and c_hat = 1.60.

Limits on that statement:

- c_hat is **grid-limited**: the true threshold lies in (12, 16] at each prime.
- The data do not show k* growing with log p over log2 p ∈ [10.0, 14.3]. They are consistent with, but do not establish, linear scaling.
- A residual type-level bias below the floor is not excluded (C-1 margins).
- The statement does not cover HEUR-WESO-516558-2's transfer to 64-250 bits.

At scale, KS-1 and START-2 at p64 did not reject at N = 2·10^4, and PC-3 was detected. That is a sampler-transfer check with limited power. Its u = 3 family member is still pending recomputation (C-5), and it is not an H-1 reading.

This is **one run, not independently recomputed** (O-1), so its strength is **preliminary**.

### I-2 Heuristic 1: no reading

The frozen protocol's FC-VOID fired, so no statement of either sign is drawn about Heuristic 1 or H-1 from O-5. This holds even though:

- the T1 comparisons use the model-free NULL-1; and
- the computed-but-unevaluated criterion inputs exist in raw-result.json.

SR-4 says STOP before any criterion is evaluated, and this analysis honours that.

### I-3 Diagnosis of the NULL-2 failure: a comparator-calibration defect in the frozen protocol, not a code defect (provisional pending exact Ψ)

1. **Code.** CLS-1, the IV-4 sympy re-verification and the reading of the generator (O-1) leave no identified path by which the NULL-2 count could be wrong. The counts are an unbiased estimate of Ψ(X, B)/X.
2. **Theory.** Where classical first-order theory is expected to be accurate (ln B ≳ 9), both NULL populations reproduce the first-order terms to within about 1-2.5%:
   - NULL-2 matches the cumulative term (C-3).
   - NULL-1 matches the point-density term (C-4).

   A broken RNG or classifier would not reproduce these; they are two different first-order terms with opposite signs.
3. **Small B.** The departures grow monotonically as B falls. At fixed B they grow with u, in the classical direction. At B ≈ 131 and u = 4.5 the expansion parameter is not small (ln B = 4.88), so the first-order term is not expected to be accurate there.
4. **Design.** The band [0.7, 2.0] and the admissibility floor B ≥ 128 were set without a finite-size model. The spec's own rationale ("B >= 128 avoids the tiny-B regime where rho is a poor finite-size model") is contradicted by the measurement: at B ≈ 131, u = 4.5, X ≈ 3.4·10^9, ρ underestimates Ψ(X, B)/X by a factor of 2.45 (99% interval [2.13, 2.82]).

So FC-VOID is attributed to a **protocol design defect in the NULL-2 comparator**. The protocol also conflates two different quantities under "ρ(u)":

- the **cumulative** fraction Ψ(X, B)/X, which lies above ρ;
- the **point** probability for an integer of a given size, which lies below ρ at first order.

This affects three things: the NULL-2 band, the `expected_direction` rationale for R_max, and PRED-2's size-matched ρ-sum, which overstates point probabilities by the C-4 factor. The model-free NULL-1 is the size-consistent comparator.

**Status: provisional.** The decisive check, an exact count of Ψ(3 408 917 801, 131.33) (the 131-smooth integers ≤ X) compared with S_NULL2 = 336, has **not** been computed. This act has no code-execution tool. The check is scheduled in DEC-20260926-c8d4b0. If the exact count disagrees with the NULL-2 count beyond binomial error, this inference is withdrawn and the run returns to the Executor as a code defect.

### I-4 Consequences for any re-analysis of the retained Stage-C samples

Replacing the ρ-relative NULL-2 band with an exact-Ψ binomial check would make the instrument gate evaluable on data already collected. But the Coordinator has now seen every criterion input (O-5). A re-analysis of the retained samples under an amended check is therefore **post hoc**: its outcome is effectively known before it is run. It can be labelled exploratory at most, can support at most `preliminary` strength, and cannot move H-1 toward `supported` or satisfy promotion gate 2 for any conditional claim.

A confirmatory reading requires **fresh, newly named seeds** under an amendment frozen before those samples exist. Any comparator chosen in that amendment is chosen after seeing v1 data, and must say so.

### I-5 Stage D ruling review: SR-4 governs (ruling upheld)

The specification says both "STAGE-D gated_by: gate_G_B and Stage C completed valid (any verdict)" and "SR-4 … NULL-2 bounds fail → STOP before any criterion is evaluated (FC-VOID)". The Coordinator upholds the dispatching session's ruling that SR-4's STOP governs, for five reasons:

- (a) Stopping rules are the specification's control flow. "Any verdict" most naturally ranges over the decision outcomes (success, FC-H1, inconclusive), which presuppose IG. FC-VOID is an instrument void, not a verdict about H-1.
- (b) The handoff binds the same way: EX-4 says "Gate failures stop as SR-1..SR-9 say".
- (c) Approval condition AC-2 says "a gate stop ends the card's execution at that stage".
- (d) Under genuine ambiguity, the reading that spends no compute and loses no evidence is the conservative one.
- (e) Stage D would have run the same NULL-2 comparator. Even where its B values would all be ≥ ~3750, a Stage-D result would carry the same unresolved comparator question.

Not running Stage D is a protocol stop. It is never evidence about Heuristic 1 or the sampler (AGENTS.md core rules 5 and 9). The conflicting wording is to be resolved in the amendment, by gating Stage D explicitly on IG.

### I-6 Delgado (KN-LIT-6fb205) and priority

KN-LIT-6fb205 (read in full, **unverified**) claims the p^{1/3+o(1)} exponent without Heuristic 1. Nothing in this analysis depends on it.

**If it holds:**

- Heuristic 1 stops carrying the exponent.
- The measurement keeps value for three things:
  - (i) the heuristic as literally stated, which GOAL-SSIQ-001 SC-1 still cites;
  - (ii) concrete cost at SQIsign parameters: Delgado disclaims concrete costs and carries constants of order 2^80 n^4, so Wesolowski's heuristic algorithm, whose per-attempt success is the smoothness probability of δ, remains the concretely relevant one;
  - (iii) the sampler result (I-1).
- The C-3/C-4 finding bears directly on (ii). A ρ-based concrete-cost model misstates smoothness probabilities in a direction that depends on whether the quantity is cumulative or pointwise.

**Either way:** verification of Delgado is an exponent-level question and outranks the H-1 confirmatory replication. The cheap exact-Ψ diagnostic (zero new sampling) does not wait on it.

---

## 4. Limitation

- **L-1 Exact Ψ not computed.** I-3 rests on first-order asymptotics, on the monotone pattern across 33 cells, and on code checks. It does not rest on an exact count. The recalled sources (de Bruijn 1951; Tenenbaum III.5; Hildebrand 1986; Hildebrand-Tenenbaum 1986 saddle point) are pointers, not support. Only the 1 < u < 2 derivations in C-3/C-4 are self-contained.
- **L-2 Stage B not independently recomputed.** The TV tables were computed by the producer's code only. The per-sample file is in ephemeral session storage. It is regenerable from seeds except `wall_s`.
- **L-3 No independent review yet.** AC-6 requires a review_plan, a validator (run-set validity and blind recomputation) and a red team (sampler and null-model joints). None has run. This analysis and DEC-20260926-c8d4b0 precede that review. They make no directional claim, and no claim may change until it completes. A review_plan prior written now is post-data and must be labelled so.
- **L-4 Grid resolution.** c_hat = 1.60 is set by the k-grid gap (12, 16] at the smallest prime. The true constant at these primes lies between 12/log2 p and 16/log2 p.
- **L-5 Mixing transfer.** k_C at 64-128 bits (308-615) is 19-38 times k* = 16. The margin is large, but transfer is an extrapolation (TA-1). KS-1 and START-2 at N = 2·10^4 have limited tail power, and their u = 3 family members at p64 are pending.
- **L-6 One prime per size (TA-2)**, one run per stage, and no replication at Stage C.
- **L-7 Measurement defects.** Stage-C CPU seconds undercount; DET-1 compared 3 workers, not 4; the implementation was untracked at run time (hash identity only); Stage A ran pre-freeze code (I-1 re-applied: 0 mismatches).
- **L-8 Scope.** Stage-C observations concern the three frozen-rule primes 2^64 + 51, the smallest p ≡ 3 mod 4 above 2^96, and the smallest above 2^128, with N = 10^5 each. The NULL-2 measurement concerns integers ≤ 5.5·10^12. Nothing here speaks to p = 5·2^248 − 1 or to the o(1) of Heuristic 1.
- **L-9 Post-data exposure.** The Coordinator has read all Stage-C metrics. Every subsequent choice of comparator or criterion is informed by them and must be disclosed as such (I-4).
