# EXP-STR-001 analysis — Displacement-rank relation matrices from AP supports (candidate A3)

- Hypothesis: STR-H-001 (research_directions_20260717.md, "## Candidate: A3")
- Run: RUN-STR-001-a (`sage experiments/EXP-STR-001/str1_ap_matrix.sage`), 2026-07-18, wall 29.1 s, 36/36 instances, not truncated
- Provenance: git 09ccb38b838ea17b562add2a439d85a60dc05ced, dirty tree, SageMath 10.9, Python 3.14.3, macOS arm64
- **validity_status: valid** (both mandatory controls pass; deviations below)

## Protocol recap (frozen in specification.yaml)

Ordinary prime-field curves, prime order n (anomalous excluded), seeded per (p, seed).
FB = x-interval, B = ceil(sqrt(n)), canonical y. p ∈ {211, 1009, 4099}; D = {1..64};
m ∈ {3,4}; seeds 20260717..20260722. Per instance: exact enumeration of all AP support
tuples {x, x+d, …, x+(m−1)d} ⊆ FB; full baseline enumeration of C(B,m) supports (sampled
at the 120 000 cap where larger); exact sum multisets over F_p; 16 seeded targets with
EXACT hit counts from the multisets; displacement rank over F_n with two operators;
greedy full-rank B×B AP subsystem + own Wiedemann solve (verified Mx=b) + dense reference;
gate arithmetic in F_p-mul-equivalent units (affine EC add charged 4 mul + 1 inv = 19 muls).

## Controls

- **Positive control (standard harvesting reproduced at D = {0}): PASS 36/36.**
  Frozen interpretation: d = 0 APs are degenerate multisets, so D = {0} is realized as the
  AP filter disabled (unconstrained random-support harvesting). Enumeration integrity held
  (multiset counts == tuple counts everywhere); 8 seeded tuple sums per instance recomputed
  with Sage's own EC arithmetic matched the script's pure-Python arithmetic exactly
  (0 failures); measured random hit rate within [0.5, 2]× the 1/n expectation everywhere.
- **Negative control (no AP enrichment in random x-sets): PASS 6/6.**
  Direct enumeration of AP m-subsets of F_p equals the closed form Σ_d max(0, p−(m−1)d)
  on all 6 legs. Sampling legs within 4 binomial σ of expectation for p ∈ {211, 1009, 4099}
  m = 3 and p = 211 m = 4; two legs (m = 4 at p = 1009, 4099) are low-power even at the
  3 000 000-sample cap (expected hits 4.1 and 0.07; observed 7 and 0) and are carried by
  the exact direct-enumeration leg — recorded as low_power, not silently dropped.

## Measured results (medians across 6 seeds per cell)

### Relation harvesting: AP vs random-support baseline

| p | m | B | n (med) | AP supply | supply/B | per-tuple penalty | yield penalty C(B,m)/supply | coverage AP | coverage base |
|---|---|---|---------|-----------|----------|-------------------|------------------------------|-------------|----------------|
| 211 | 3 | 15 | 197 | 28 | 1.77 | 0.990 | 17.5 | 0.132 | 0.929 |
| 211 | 4 | 15 | 197 | 8 | 0.48 | 0.680 | 214.9 | 0.033 | 1.000 |
| 1009 | 3 | 32 | 1002 | 124 | 3.83 | 0.891 | 41.9 | 0.118 | 0.993 |
| 1009 | 4 | 32 | 1002 | 40 | 1.23 | 0.139 | 924.5 | 0.039 | 1.000 |
| 4099 | 3 | 64.5 | 4080 | 477 | 7.41 | 0.700 | 87.8 | 0.111 | 1.000 |
| 4099 | 4 | 64.5 | 4080 | 154 | 2.41 | 0.315 | 4128.6 | 0.038 | 1.000 |

Per-tuple penalty = random hit rate / AP hit rate over 16 targets (exact counts);
14/36 instances (small supply × few targets) have zero AP hits → rate 0, recorded as such.
**The penalty is in the supply, not the per-tuple probability**: AP tuples hit at a
comparable per-tuple rate (penalty 0.14–0.99), but only supply ≪ C(B,m) tuples exist
(yield penalty 17.5×–4128.6×), and AP tuple sums cover only 3.3–13.2 % of the group.
Yield penalty grows with p and superlinearly in m (m=3: ~×2 per size doubling; m=4: ~×4.4).

### Displacement rank α over F_n (exact)

| p | m | α_xspace AP | α_xspace rand | α_classic AP | α_classic rand | min(R,B) |
|---|---|--------------|----------------|---------------|-----------------|-----------|
| 211 | 3 | 9.5 | 7.5 | 15 | 15 | 15 |
| 211 | 4 | 6 | 6 | 9 | 9 | 9 |
| 1009 | 3 | 25 | 17.5 | 32 | 32 | 32 |
| 1009 | 4 | 18 | 16.5 | 32 | 32 | 32 |
| 4099 | 3 | 49 | 31.5 | 64.5 | 64.5 | 64.5 |
| 4099 | 4 | 38 | 31 | 64.5 | 64.5 | 64.5 |

- α_classic = standard (Z, Zᵀ) displacement rank, AP rows in (d, x_start) harvest order.
  It equals the generic maximum min(R,B) in 32/35 measurable instances; the 3 exceptions
  (toy ranks) have AP α slightly BELOW random (12<14, 10<15, 25<27). A genuine
  Toeplitz/Hankel-like operator would give α ≈ 2–4. Measured: α ≈ B.
- α_xspace = rank of (Z_r M − M Z_c) under the mechanism's own x-translation symmetry.
  AP α is comparable to, and at the two larger sizes LARGER than, the same-shape random
  baseline; α/B ≈ 0.56–0.77 at p ≥ 1009 (roughly constant ⇒ α grows ≈ linearly in B);
  α/√B itself grows 2.42 → 4.39 → 6.10 (m=3), i.e. α grows faster than √B.
- Cause is visible in the data: the FB x-interval has ~50 % gaps (non-residue x's), so
  x-translation by 1 does not preserve FB membership; the claimed translation symmetry of
  supports does not survive lifting — the candidate's own "likely fatal obstruction" #2.

### Structured solve vs Wiedemann at equal matrix

Equal matrix = greedy full-rank B×B subsystem of the AP relation matrix over F_n.
Feasibility: full-rank square obtained in 4/6 seeds (211,m3), 0/6 (211,m4 — supply < B),
6/6 (1009,m3), 3/6 (1009,m4), 6/6 (4099,m3), 6/6 (4099,m4).

| p | m | Wiedemann (measured) | dense ref (measured) | structured model ops | model ratio str/wie |
|---|---|----------------------|----------------------|----------------------|---------------------|
| 211 | 3 | 0.43 ms | 0.2 ms | 2 940–8 640 | 4.9× |
| 1009 | 3 | 2.38 ms | 0.6 ms | 84 640–155 232 | 17.6× |
| 1009 | 4 | 1.90 ms | 0.3 ms | 46 240–77 440 | 7.4× |
| 4099 | 3 | 6.45 ms | 0.9 ms | 921 375–1 048 320 | 39.1× |
| 4099 | 4 | 6.32 ms | 0.8 ms | 443 904–710 016 | 18.6× |

- All 25 Wiedemann solves verified (Mx=b, 1 attempt each); minpoly degree < B in some
  instances (random projection) — correctness gated on verification, all pass.
- Structured-solve time is MODEL-ONLY (frozen scope note; no superfast solver at toy
  scale): ops = α²·B·⌈log2 B⌉ with the measured x-space α (the smaller of the two
  measured α's — favorable to the candidate). Wiedemann model ops = 2·B²·m.
- At the measured α, the "structured" solve costs 4.9–39× MORE field ops than generic
  Wiedemann, and the ratio grows with size. With α_classic = B it is worse still.

### Promotion-gate arithmetic (fully charged, F_p-mul-equivalent units)

| p | m | LA share (Wiedemann) | LA share (structured model) | relation penalty vs baseline | gate threshold |
|---|---|----------------------|-----------------------------|------------------------------|----------------|
| 211 | 3 | 0.016 | 0.075 | 17.5× | LA < 0.10 AND penalty < 1.5× |
| 211 | 4 | 0.015 | 0.018 | 214.9× | same |
| 1009 | 3 | 0.005 | 0.090 | 41.9× | same |
| 1009 | 4 | 0.030 | 0.165 | 924.5× | same |
| 4099 | 3 | 0.004 | 0.129 | 87.8× | same |
| 4099 | 4 | 0.007 | 0.133 | 4128.6× | same |

- LA share < 10 % holds with generic Wiedemann at all sizes (0.4–3.0 %) — at toy sizes the
  relation stage dominates total cost so heavily that this clause is structurally easy.
- With the structured model it exceeds 10 % in 4/6 cells.
- The relation-stage penalty vs the standard-harvest baseline is 17.5×–4128.6× — 1–3
  orders of magnitude above the 1.5× threshold — and GROWS with size at both m.
- Disproof-track arithmetic: α grows like B (α/√B rising 2.4→6.1), and the AP penalty
  exceeds n/B at the two larger sizes (41.9 > 31.2, 87.8 > 63.3, 924.5 ≫ 31.2,
  4128.6 ≫ 63.3). Measured values do not cross the promotion gate at any size; both
  disproof criteria are met by the measurements. (Status decision belongs to the
  Coordinator.)

## Unexpected observations (rule 8)

1. Per-tuple AP hit probability is NOT collapsed (penalty 0.14–0.99); the failure is
   entirely supply-side (tuple count) and coverage-side (3.3–13.2 % group coverage,
   max multiplicity ≤ 3 — AP sums are spread thin, not clustered).
2. α_xspace(AP) ≥ α_xspace(random) in 5/6 cells — AP matrices are slightly MORE
   displaced than random under x-translation (interval boundary effects).
3. AP relation matrices have excellent ordinary rank (rank = B extractable whenever
   supply ≳ 1.2·B): the obstruction is structural (no displacement structure), not rank.
4. Sage dense solve_right shows ~0.1 s first-call overhead then sub-ms; toy timings are
   constant-dominated and are not interpreted as scaling evidence.
5. m=4 at p=211: AP supply as low as 3 tuples (one instance below the m-threshold for the
   displacement computation → recorded as null, not interpolated).

## Deviations from protocol (all recorded here and in the EV record)

1. p=4099/m=4: C(64,4) = 635 376 > 120 000 cap → seeded uniform sample of 120 000 baseline
   tuples (per stopping rules); exact combinatorial totals used for yield arithmetic.
2. D = {0} positive control realized as AP-filter-disabled (frozen interpretation in
   specification.yaml; d = 0 APs are degenerate multisets).
3. Two negative-control sampling legs low-power at the 3 M-sample cap; exact
   direct-enumeration leg carries the control.
4. Structured-solve time is model-projected from measured α (no superfast solver
   implemented at toy scale) — frozen scope note in specification.yaml.
5. Run history: 4 sage invocations; attempts 1–3 were infrastructure failures of the
   script (sage preparser Integer leaks into random.seed / JSON — fixed; one Rational
   truncation bug in the JSON coercer — fixed and rerun). Attempt 4 is the run of record.
   No timeout kill was needed (29 s < 600 s). Runs used: 4 ≤ budget 8.

## Limitations / claim boundary

Toy prime fields (p ≤ 4099, n ≤ 4139), x-interval FB at B = ⌈√n⌉ only, 6 seeds, 16
targets per instance for hit-rate estimates (distribution stats are exact). Hit-rate
penalties at small supply have wide uncertainty (14/36 zero-hit instances recorded
honestly). Structured-solve comparison is a cost-model evaluation driven by measured α,
not a measured superfast solve. Per docs/evidence-and-reproducibility.md, these
observations establish behavior only on the tested toy distribution; they close only the
tested scope: AP-constrained relation supports at these sizes, FB rule, and D = {1..64}.
