# RUN-SEMBIN-251fd3 — run report (TASK-20260913-495fcc, attempt 2)

Experiment `EXP-SEMBIN-db9bc3` (frozen v1, approved by `DEC-20260913-d02263`),
hypothesis `H-SEMBIN-4a80f3`. Executor observations only. No hypothesis status is
moved, no evidence record, decision or knowledge item is written, and nothing
below is a statement about the security of any curve.

**Scope statement (carried on every deliverable).** Every number here is
log2-domain arithmetic over the declared grid, conditional on Nagao's
Proposition 5 and the first fall degree assumption (both GRANTED, untested).
"Nagao ahead" at a cell means the charged closed form under THIS program's
enumeration of T1–T5 is below van Oorschot–Wiener at the Pareto minimum of its
own curve, at that exact (n, ω, C_0, metric, monomial-count reading, memory
reading). It is not a statement that B-163/233/283/409/571 or any K-curve is
affected, weakened or attacked, in either direction. The two sides' units differ
(F_2 Macaulay operations vs group operations; no conversion applied; a
conversion would move the comparison further toward Nagao by ≈ 2 log2 n bits —
disclosed in `cost-surface.json.unit_conversion_sensitivity`). By the
hypothesis's quantifier order, a table at n ≤ 571 cannot contradict an
asymptotic theorem with unstated n_0; it describes applicability at these n.

Everything in arms C (closed forms), N, K, P, M, I is **modeled**. Only ARM C's
enumeration is **measured** (exhaustive counts at n ≤ 20).

## 0. Attempts

| attempt | window (UTC) | outcome |
|---|---|---|
| 1 | 18:43–19:41 | `failed_infrastructure`: runtime activity timeout; five modules drafted under `code/`, nothing written to the run directory. Not evidence (core rule 5). |
| 2 | 19:45–19:56 | this run; driver executed twice (see §9), zero numeric differences between executions across 42,650 compared values. |

Attempt-1 modules: **kept unchanged** `arm_c_coset.py`, `arm_i_independent_memory.py`,
`binary_field.py`, `nagao_cost.py`; **kept with one docstring correction**
`semaev_repro.py` (the `degenerate_slice` docstring claimed the ceiled rows differ
by the ceiling slack; the implementation compares like-with-like and returns 0 at
both readings, which is the correct identity; docstring fixed, self-test pins it).
**Added in attempt 2**: `selftest.py` (56 hand-checked assertions, all pass) and
`run_experiment.py` (driver; writes each arm's artifact the moment it completes).
Every reused formula passed the self-test against a hand-worked literal; ARM R
passed before any Nagao cell was computed.

## 1. ARM C — the C_0 lower bound (ran first; `c0-lower-bound.json`)

Closed forms (HEUR-1, δ = 1/2, m = ⌈n/C_0⌉), two conditions separated:

- **Bound A** (no empty coset, ε = 0.05): Pr[all m nonempty] = (1 − 2^{−2^{C_0}})^m.
  Order of growth **Θ(log log n)**. Value: **C_0 ≥ 4 at all five labels**
  (163, 233, 283, 409, 571); first reaches 5 at n = 16384.
- **Bound B** (∏#Fb_i within 1 bit of 2^n, the condition Nagao's yield argument
  uses): total Jensen deficit Δ = m·[log2 E#Fb_i − E log2 #Fb_i] ≤ 1 bit.
  Order of growth **Θ(log n)**. Values: **C_0 ≥ 5 / 6 / 6 / 6 / 7** at
  n = 163 / 233 / 283 / 409 / 571; reaches 12 at n = 65536.
- Consequence stated in the closed-form block: under bound B, p^{C_0} = Θ(n/log n)
  so #Fb = Θ(n²/log² n), and the decompose exponent moves from 8ω+1 to 8ω+2 up
  to logarithmic factors. **It remains polynomial.** This run does not propose
  that Theorem 1 is non-polynomial; escalation trigger (b) is NOT fired.
- **Second reading recorded, not adjudicated**: if the m translates are *chosen*
  after testing ("we choose suitable constant C_0"; Algorithm 2's "Put v_1..v_m"),
  there are 2^{n−C_0} cosets to pick from, only m are needed, and the selection
  cost is the same order as writing the factor base down. Under that reading
  neither bound constrains C_0. Both readings are in the JSON.
- Declared C_0 range vs bounds: {2, 3} violate bound A at every n; {2, 3, 4}
  violate bound B at every n, {6} additionally at n = 571 (and {5} is not in the
  declared range). Violating cells are computed and flagged, never dropped.
- H-SEMBIN-4a80f3 P1's "C_0 ≥ ~9.2 at n = 571" is the crude reading 2^{C_0} ≥ n
  (= log2 571 = 9.157). The derived bound B is 7 at n = 571 (1-bit tolerance);
  the crude reading is reported beside it.

**Exact enumeration (measured)**: 28 cells, p = 2, n ∈ {8,…,20}, k ∈ {1,…,4},
one seeded random ordinary curve y²+xy = x³+Ax²+B per cell, structured
V = span{1,x,…,x^{k−1}} plus 4 random k-dim V, null = 8 random subsets of the
same size under both V families. Peak RSS 120 MB against the 2 GB cap;
**0 cells unreached**. Curve-vs-null pooled z-scores: mean 0.037 SD, max |z|
1.24 SD, no cell beyond 2 SD. Structured-V single-draw z: max |z| 2.09 at
(n = 20, k = 2), the only cell beyond 2 SD (≈1.3 such cells expected by chance
in 28). Observed empty-coset counts track the binomial prediction cell for cell
(e.g. n = 20, k = 3: structured 496, random-V mean 540.75, predicted 514.6,
null 519 ± 19). No verdict on HEUR-1 is given here; the comparison is reported.

**Prior check.** The Coordinator's prior expected ARM C to force C_0 = Ω(log n)
and thereby make Theorem 1 non-polynomial. The arithmetic gives Ω(log n) for
bound B (and only Ω(log log n) for the correctness condition A), with numerical
values 4–7 across the labels — but the consequence is exponent 8ω+2 (up to
logs), not non-polynomiality. So the prior's *growth order* held for bound B and
its *conclusion* (non-polynomial) did not follow. ARM C did not turn out to be
"the whole experiment": constant-looking C_0 values (7 at n = 571) satisfy its
bound and the surface at those C_0 is where the results below live.

## 2. ARM R — reproduction gate (`reproduction.json`) — **PASSED**

107 gate cells (COST-SEMBIN-8d123b five-label table, its crossovers, ceiling
discrepancy and degree-sensitivity block; CORR-20260913-53739b correction_1's
corrected eq. (11) figures, argmins and crossovers 281/295/337/393 and its
controls; EV-SEMBIN-71e5cd O-6's exactly-29.0-bit overcharge at n = 283/310/409/571
and O-7's 520/460 and 518/460 crossovers and −37.79/−17.48/+40.49 margins).
**0 failures. Worst error at a 1e-3-tolerance cell: 0.00086 bits**
(`bits_added_if_bound_is_5[n=310]`, 18.24514 vs printed 18.246). Worst error at
a 1-decimal target cell: 0.048 bits (tolerance 5e-2 declared before the arm ran).
Every integer cell (optimal m, argmin (m,k), crossover n) matched exactly.

Control: the m!-only (uncorrected) figures 186.7/187.2 and 186.4/186.5/197.1 and
303/307/347/400 are reproduced BY NAME under the m!-only charge, and the eq. (11)
pipeline does **not** reproduce any uncorrected figure where it differs from the
corrected one. Degenerate slice (C_0 = k, m = n/k, m! yield restored): difference
exactly 0 at both un-ceiled and ceiled readings at all five labels. Note: this
identity is an identity of the relation-count × yield accounting under a shared
per-solve cost; it does not assert Nagao's Lemma-2 per-solve (N^{d_F ω},
N = n(m−1)) equals Semaev's block-reduced n^{4ω}. ARM N charges Nagao's own.

## 3. ARM N — cost surface (`cost-surface.json`, `concrete-cost.yaml`)

320 cells (5 n × {2.376, 2.807, 3.0, and Nagao's own 2.7 reported separately} ×
8 C_0 × 2 readings), each with T1–T5 as separate columns, memory beside time,
margins under 4 metrics × 2 memory readings, and both ARM C flags. 512 crossover
cells. Sign: margin = Nagao − vOW, positive = Nagao worse. vOW at its Pareto
minimum: product metrics at 6nW (invariant along w = M), equal-rate at √(6nW),
time-only at total work W (declared convention, documented in code).

Representative rows, binomial reading, n = 571 (T1..T5 in bits; margins TO =
time-only, TM = time×memory frozen width C(N+4,4), TMd = time×memory dense
width², ER = equal-rate):

| ω | C_0 | bound B | m | T1 | T2 | T3 | T4 | T5 | time | TO | TM | TMd | ER |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 2.376 | 8 | ok | 72 | 56.6 | 77.9 | 14.2 | 0.00 | 56.6 | 148.8 | −136.6 | −91.7 | −35.0 | +0.2 |
| 2.807 | 8 | ok | 72 | 56.6 | 102.4 | 14.2 | 0.00 | 56.6 | 173.2 | −112.2 | −67.3 | −10.6 | +24.6 |
| 3.0 | 8 | ok | 72 | 56.6 | 113.3 | 14.2 | 0.00 | 56.6 | 184.1 | −101.2 | −56.3 | +0.3 | +35.6 |
| 3.0 | 3 | violates | 191 | 62.3 | 124.6 | 10.6 | 17.01 | 62.3 | 214.6 | −70.8 | −20.2 | +42.1 | +66.0 |

The full per-label table for all 240 committed-ω cells is in `concrete-cost.yaml`.

**Crossover surface** (committed ω only; each entry is the range over the 24
(ω, C_0) cells; the JSON has every cell):

| metric | reading | memory reading | crossover n, all declared C_0 | restricted to C_0 satisfying bound B at the crossover |
|---|---|---|---|---|
| time_only | binomial | — | 244–399 | 244–338 |
| time_only | loose N^d | — | 271–435 | 271–373 |
| time×memory / AT | binomial | frozen width | 332–529 | 332–446 |
| time×memory / AT | binomial | dense width² | 457–697 | 457–572 |
| time×memory / AT | loose | frozen width | 360–565 | 360–481 |
| time×memory / AT | loose | dense width² | 486–731 | 486–606 |
| equal_rate_max | binomial | either | 561–961 | 561–753 |
| equal_rate_max | loose | either | 614–1039 | 614–820 |

No cell returned a null crossover in [16, 2000]. At C_0 ∈ {2, 3, 4} the
crossover is frequently **not monotone** (Nagao falls behind again within 200 of
n) because T4 grows linearly in m at fixed small C_0 (17.0 bits at n = 571,
C_0 = 3) — the ARM C premise showing up in the cost arithmetic.

**Spreads at n = 571** (bits): C_0 spread over the declared range 36.9 (time-only)
/ 49.0 (T×M frozen) / 61.1 (T×M dense); over the bound-B-satisfying range only
5.2 / 9.3 / 13.4. ω spread 40.4 (binomial) / 43.2 (loose) at every C_0; the
theorem form n^{8ω+1} alone spans 45.7 bits.

**Escalation flags (contract trigger (a))**: 242 cells show Nagao below vOW's
Pareto minimum under a memory-charging metric at a FIPS label; 180 with ω in the
committed set; **120 with ω committed AND C_0 satisfying ARM C's bound B**. Those
120 are at n = 409 (15 T×M + 15 AT, frozen width only, C_0 ≥ 8 at ω = 2.807,
C_0 ≥ 6 at ω = 2.376, C_0 = 16 at ω = 3.0 by 0.1 bits) and n = 571 (42 T×M +
42 AT under both memory readings for ω ≤ 2.807 and under frozen width at ω = 3.0;
6 equal-rate at ω = 2.376, C_0 ≥ 10). Under the dense-width² reading at
ω = 3.0, n = 571, the sign is within 0.3 bits of zero at C_0 = 8 and negative
from C_0 = 10. **Recorded plainly and flagged for review-breakthrough at max
effort (non-degradable, core rule 12) as the contract declares. Not characterised
as a result.** The reviewer should weigh: (i) the memory reading (column count
vs dense square differs by 57–65 bits at n = 571 and decides the n = 409 rows),
(ii) the unit disclosure (favours Nagao further if applied), (iii) the granted
Proposition 5 and first-fall-degree assumption, and (iv) that Nagao's Lemma-2
per-solve N^{4ω} with N = n(m−1) ≈ n²/C_0 has no measured constant.

## 4. ARM K — known-false object d_F = 5 (`known-false-dF5.json`)

240 cells. Cost rose at every cell. Observed time rise minus the degree-ratio
prediction (ω log2 N loose; ω log2((N+5)/5) binomial): max |residual|
5.7e-14 bits. Memory rise likewise. Observed time rise range across cells is
reported in the JSON. Degree sensitivity is present and of the predicted
magnitude; invalidation rule 2 did not fire.

## 5. ARM P — nearby object, odd characteristic (`nearby-object-oddchar.json`)

From the shared code path, p = 3 gives d_F = 10 and exponent 20ω+1
(48.52 / 57.14 / 61.0 at ω = 2.376 / 2.807 / 3.0); p = 5 gives d_F = 16 and
32ω+1. All exponents match (6p+2)ω+1 and all degrees match 3p+1; p = 2 gives
8ω+1 from the same function. Call-sequence traces at p = 2, 3, 5 are identical
after masking p and the p-derived d_F (masking p alone leaves d_F differing,
which is the expected and only difference). p enters only through `d_F_bound`
(the source's own Prop. 2 / Prop. 5 branch) and log2 p. Invalidation rule 3 did
not fire. **Anomaly recorded**: H-SEMBIN-4a80f3 P6 quotes "54.5 at p = 3,
ω = 2.807" but its own formula (6p+2)ω+1 = 20·2.807+1 = **57.14**; the code
returns the formula's value. The hypothesis is not edited.

## 6. ARM M — matched nulls (`matched-nulls.json`)

240 cells × 8 metric/memory combinations. Free-yield share of the margin equals
T4 exactly: 0 bits at cells with slack m·C_0 − n ≥ 2, up to **17.0 bits at
n = 571, C_0 = 3** (Δ = 19.0 bits of Jensen deficit across 191 cosets of
expected size 8). Zero-memory share equals the charged memory column exactly:
44–65 bits (frozen) / 89–129 bits (dense) across the grid. Both nulls beside the
real margin at every cell.

## 7. ARM I — blind memory term (`independent-memory-term.json`)

Written from "C(N+4,4) at N = n(m−1), m = n/C_0" alone, before ARM N existed
(module docstring records the ordering). Three ambiguities found in the
statement and reported rather than resolved: A1 rounding of m (C_0 ∤ n at 22 of
40 cells), A2 clamp m ≥ 2, A3 unit. Under the ceil reading the largest
disagreement with ARM N's T5 frozen-width column is **exactly 0.0 bits** at all
40 (n, C_0) cells. Under the floor reading the largest disagreement is
−0.607 bits (the A1 ambiguity, e.g. n = 571, C_0 = 16 floor m = 35 vs ceil 36).
The quantity was derivable from its statement up to those three declared
ambiguities.

## 8. Predictions P1–P6 and the prior — observations

- **P1** (C_0 = Ω(log log n) for no-empty-coset, Ω(log n / log p) for the yield
  condition; ≈ 9.2 at n = 571): **growth orders held** (A: Θ(log log n),
  B: Θ(log n)). The numerical value at n = 571 under the derived bound B is 7
  (1-bit tolerance), and 9.157 is the crude 2^{C_0} ≥ n reading. Under the
  searched-coset reading neither bound constrains C_0; that reading is recorded.
- **P2** (time-only crossover exists below 571 at ω = 2.807, range [250, 450]):
  **held** at every C_0 under both readings — at ω = 2.807 the binomial-reading
  crossovers are 293–369 (C_0 = 16 … 2), inside [250, 450]. The Coordinator's
  contrary prior (no time-only crossover below 571) **was overturned**: at
  n = 571 the time-only margin is −70 to −139 bits across committed ω and C_0.
- **P3** (no crossover below 571 under T×M or AT for any committed ω): **failed
  at most cells**. Under frozen-width memory the T×M/AT crossover is 332–529
  across the declared grid and ≤ 446 at bound-B-satisfying C_0; under dense
  width² it is 457–697, with n = 571 straddled at ω = 3.0 (crossover 572 at
  C_0 = 8, 539–561 at C_0 ≥ 10). Recorded and flagged for escalation; not
  characterised.
- **P4** (C_0 spread at 571 > 46-bit ω spread): **mixed, reading-dependent**.
  Over the declared C_0 range: 36.9 (time-only) < ω spread 40.4–43.2; 49.0 (T×M
  frozen) and 61.1 (T×M dense) > ω spread. Over bound-B-satisfying C_0 only:
  5.2–13.4, well below the ω spread under every metric. The measured ω spread of
  the charged cost is 40.4–43.2 bits, not 46 (that is the theorem form's).
- **P5** (reproduction gate passes at 1e-3): **held**; worst 0.00086 bits.
- **P6** (odd branch returns (6p+2)ω+1 from the shared path): **held** as a
  formula; the quoted numeral 54.5 is inconsistent with the formula (57.14).
- **Coordinator prior**: ARM C growth order held but the non-polynomiality
  inference did not; "no time-only crossover below 571" overturned; "Nagao loses
  under memory charging at every label" overturned at n = 409 and 571 under the
  frozen-width reading and at n = 571 under dense width² for ω ≤ 2.807.
  Escalation trigger (a) fires; trigger (b) does not.
- **Framing-failure check**: the charged cost depends on the memory reading
  (57–65 bits at n = 571) by more than on any varied variable except ω; the
  memory reading was carried as a second axis in every deliverable, so it is
  reported as a surface dimension rather than as an unmet deliverable. It should
  be treated as a declared variable by any successor contract.

## 9. Protocol deviations

1. Driver executed twice within attempt 2 (label fixes only; exec-1 artifacts
   retained as `*.driver-exec-1.*`; zero numeric differences). Classified
   `implementation_error` in reporting labels, fixed, not evidence.
2. `manifest.yaml.artifacts` was re-hashed once after `task-report.md` and
   `implementation.md` were written, so the manifest lists every file in the run
   directory; no other manifest field was changed by that step.
3. Git HEAD moved twice during the run (Coordinator commits on the shared branch:
   783decc8 → 0fbc6de0 → 0ac05e30); the manifest records HEAD at manifest-write
   time and `dirty: true` (this run's own uncommitted artifacts).
4. Tolerance policy: 1-decimal and 2-decimal targets were checked at their
   printed precision (5e-2 / 5e-3) and reported at full precision beside, because
   a 1e-3 check against a 1-decimal number is not a test; declared in code before
   the arm ran.
