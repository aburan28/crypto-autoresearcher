# EXP-INC-001 analysis — output-sensitive F_p incidence reporting vs exact enumeration (candidate A2, m=3)

**Canonical run:** `RUN-INC-001-c` (valid). Superseded runs: `RUN-INC-001-a` (invalid — witness
bug), `RUN-INC-001-b` (invalid — serializer defect); both preserved with manifests.
Curves (deterministic scan, prime order ⇒ ordinary): p=211 E=[20,143] n=223; p=1009 E=[5,38]
n=1021; p=4099 E=[25,178] n=4079. Seeds 20260717..20260722, 6 per instance.
B grid exclusions per protocol (B<8): p=211 n^(1/4)→4, n^(1/3)→6; p=1009 n^(1/4)→6.
36 instances total (6 surviving (p,B) rows × 6 seeds).

## Measured per-size table (seed means; op unit = candidate pair test = 1 EC add + 1 x-lookup)

| p | n | B row | B | pair tests (ALL methods) | avoided | I mean | I pred | enum total | r1 total | r2 total |
|---|---|-------|---|------|---------|--------|--------|-----------|----------|----------|
| 211  | 223  | n^2/5 | 9  | 36  | 0 | 0.333 | 0.377 | 48.3  | 62.3  | 101.3 |
| 1009 | 1021 | n^1/3 | 10 | 45  | 0 | 0.167 | 0.118 | 56.8  | 75.8  | 110.8 |
| 1009 | 1021 | n^2/5 | 16 | 120 | 0 | 0.667 | 0.548 | 140.5 | 165.5 | 200.5 |
| 4099 | 4079 | n^1/4 | 8  | 28  | 0 | 0.167 | 0.014 | 37.5  | 50.5  | 89.5  |
| 4099 | 4079 | n^1/3 | 16 | 120 | 0 | 0.167 | 0.137 | 137.7 | 162.7 | 197.7 |
| 4099 | 4079 | n^2/5 | 28 | 378 | 0 | 0.667 | 0.803 | 411.5 | 459.5 | 483.5 |

Candidate tests are **exactly C(B,2) for enum, r1, and r2 on every instance** — the reporters
avoid zero candidate pairs (grid bucketing and algebraic partitioning have no filtering power
over F_p representatives; no correctness-preserving skip rule exists without order structure).
r1/r2 totals exceed enum only by their setup/visit overheads. Wall-clock totals over all 36
instances: enum 39.0 ms, r1 37.6 ms, r2 39.1 ms — no constant-factor win (Python-overhead
dominated at toy sizes; op counts are the predefined primary metric).

## Controls

- **Positive control: PASS.** Reporter triple multisets identical to enumerator on 36/36
  instances; all 13 reported witnesses verified by exact EC addition (P_i+P_j+P_k = O).
- **Negative control: PASS.** Random non-EC point sets were not reported more cheaply:
  avoided pairs 0 (random) ≤ 0 (EC). Richness itself: I_EC = 13, I_rand = 12, random-model
  prediction Σ C(B,3)/n = 11.98 — EC chord richness is indistinguishable from random sets and
  from the prediction at these sizes (no anomalous richness; relevant context for D3).

## Gate arithmetic (measured numbers, not a verdict)

- **Pair/tuple-output exponent (candidate-test scaling): 2.078 for ALL three methods**
  (log2 tests vs log2 B, 6 pooled rows). All methods are exactly Θ(B²) in the query phase.
- Fitted total-op exponents α₂: enum 1.900, r1 1.743, r2 1.332. The r2 value reads below the
  3/2 gate threshold **only as a finite-size artifact**: r2's fixed overhead (45 structure-pair
  visits + 2B bucket inserts) exceeds its useful work at small B (at B=8: 89.5 total vs 28
  tests), which flattens the fitted slope. Its candidate tests are exactly C(B,2) with exponent
  2.078 and zero pairs avoided; the fit converges to 2 as B grows. The naive α₂<3/2 reading is
  therefore not evidence of output sensitivity.
- **Setup o(B²): confirmed numerically** for r1 (setup+visits)/B² = 0.344, 0.300, 0.296,
  0.164, 0.164, 0.098 across the six rows (≈ Θ(1/B), subquadratic). Setup being cheap does not
  help: the crux is the query phase, which stays fully quadratic — exactly the candidate's own
  "likely fatal obstruction" #1.
- **Marginal per-incidence cost (seed-aggregated): Σ non-setup ops / Σ I = 4436/13 = 341.2 ops
  per reported incidence, IDENTICAL for enum/r1/r2** — marginal cost is candidate-proportional
  (Ω(B²) per constant-size output), not output-proportional.
- **Complete-cost trend (log2 total vs log2 n):** n^(2/5) row, 3 sizes: enum 0.736, r1 0.687;
  n^(1/3) row, 2 sizes: enum 0.639, r1 0.551; n^(1/4) row has only one surviving size (no trend).
  No row trends below 0.49. Charged ratio total/(0.886·√n) along n^(2/5): 4.71 → 5.85 → 8.12
  (r1), growing with n; the n^(1/4) row sits at 0.89 < 1 at its single size but delivers
  I ≈ 0.014 relations/seed — essentially zero relation supply (m=3 arithmetic, as the candidate
  itself states).
- Output vs B fit (richness growth): 0.95 (tiny counts; informational only).

## Unexpected observations (rule 8)

1. **RUN-INC-001-a (invalid, preserved):** implementation v1 recorded triples on x-coordinate
   match alone. The FB point with x = x(−(P_i+P_j)) is −R with probability ~1/2, and −R is not
   on the chord line — 18/36 instances failed exact EC witness verification, with apparent
   richness inflated ~4× (48 vs predicted ~12). Multiset equality across methods still held
   (shared pair body), and the negative control passed. Fixed in v2 by exact point-equality
   (P_k = R) at record time; after the fix EC richness matches random sets and the random model
   (13 ≈ 12 ≈ 11.98). Lesson recorded: x-only matching is not a valid witness; the sign check
   is mandatory.
2. **RUN-INC-001-b (invalid, preserved):** JSON serializer tried int() before float();
   sage-preparsed decimal literals (1.5, 0.49, 2/3, 0.886) became RealNumber/Rational and were
   int-truncated in the gate_arithmetic block. Algorithm unchanged; serializer fixed in v2.1.
   Primary rows verified byte-identical in value to run-c.
3. The naive total-op α₂ fit for r2 (1.33) superficially passes the 3/2 threshold while the
   method does zero filtering — a warning against reading fitted exponents without the op
   decomposition at toy sizes.

## Scope

Toy prime fields (p ≤ 2^12), m=3 chord relations only, B ∈ {8..28}, one reporter family
(grid bucketing + algebraic partition, correctness-preserving). Per negative-result semantics:
no improvement meeting the predefined thresholds was observed over the tested instances,
parameters, implementation, and budget; this closes only the tested scope. It does not address
m=4/5 regimes, crypto-scale fields, or the existence of a subquadratic finite-field reporting
primitive (the candidate's proof/disproof tracks and D3 barrier remain open).
