# EXP-QSP-33b442 Stage 5 — the report

**Executor of `TASK-20260917-892420`. Observations only.** Nothing here decides
whether `H-QSP-5540d7` is supported, refuted, or anything else; that is a
Coordinator decision on a later review round, and by `claim_tier_note` of the
frozen contract a supported outcome routes to an independent
`review-breakthrough` round at `max` effort.

Every number in the **MEASURED** sections below was produced by the runs
`RUN-QSP-33b442-S1`, `-S1B`, `-S2B`, `-S3`, `-S4` of this experiment and is
extracted mechanically from their `raw-result.json` files into
`runs/RUN-QSP-33b442-S5/metrics.json` by `implementation/make_report.py`.
**No number in this report was taken from `analysis/qsp-ecc2k130/explore/`**
(`explore.json`, `explore_fast.json`, `shape_census_131.json`, or the README
tables). Code was adapted from that directory with provenance stated in the
headers of `implementation/qspcore.py` and `implementation/gf2rc.c`; no data
was.

Amendment in force: `AMD-20260917-001` (the Stage 2 / C3 `deg D` feasibility cap).

---

## 0. Run inventory

| run | stage | status | wall (s) | CPU (s) | peak RSS | workers |
|---|---|---|---|---|---|---|
| `RUN-QSP-33b442-S0` | 0 — derivation note | `completed_valid` | zero compute | zero compute | n/a | n/a |
| `RUN-QSP-33b442-S1` | 1 + gate + C1–C4 + C6 | `completed_valid` | 2.857 | 2.555 | 58118144 B | 1 |
| `RUN-QSP-33b442-S1B` | 1b (= C5) | `completed_valid` | 24.865 | 24.966 | 53993472 B | 1 |
| `RUN-QSP-33b442-S2` | 2 | **`aborted_implementation_error`** | 1481 (before abort) | not captured | not captured | 1 |
| `RUN-QSP-33b442-S2B` | 2 | `completed_valid` | 1099.091 | 1099.171 | 73916416 B | 1 |
| `RUN-QSP-33b442-S3` | 3 | `completed_valid` | 143.841 | 143.911 | 52527104 B | 1 |
| `RUN-QSP-33b442-S4` | 4 | `completed_valid` | 5.845 | 5.927 | 51417088 B | 1 |

`RUN-QSP-33b442-S2` is **retained and invalid**, superseded by `-S2B` under a
new run id. No number from it is reported anywhere. Its defect (an
unconditional construction of `D` for the recorded `deg_D` column, infeasible
at `q = 15`) is written out in its own manifest. That is `implementation_error`
in the `agents/executor.md` taxonomy — not `F6`, and not evidence of any kind.

Peak memory across every run: **73916416 B ≈ 70.5 MiB**, against the 4 GB cap.

**Determinism cross-check, free of charge.** The 54 per-cell checkpoint files
that `-S2` wrote before it was stopped and the corresponding cells of `-S2B`
cover **23176 of the same candidates**, computed by two independent invocations.
They return the **same `N` on all 23176, with 0 mismatches**. This is a
determinism check on the I2 code path only; it is not a result, and no `N` is
reported from `-S2`. No seventh stage invocation was spent on a full
replication run, because `budget.maximum_runs = 6` is a hard limit and six
invocations were used; Stages 0, 1, 2, 3 and every control are exhaustive and
seed-free and so reproduce bit for bit by construction, and a fresh replication
remains available to the Validator.

---

## 1. MEASURED — the metrics as the contract names them

### M1 — max `N / max(d^{q+1}, 2^{n'-r})` per cell

Stage 1 (exhaustive `F_2`, 252 candidates per cell, 0 degenerate anywhere):

| cell | q | r | M1 | attaining lambda | max N | bound there |
|---|---|---|---|---|---|---|
| (11, 6) | 1 | 5 | **0.52** | `X^5 + X^3 + X` | 13 | 25 |
| (13, 7) | 1 | 6 | **0.56** | `X^5 + X + 1` | 15 | 25 |
| (7, 3) | 2 | 1 | **1.00** | `X^2 + X` | 8 | 8 |
| (11, 4) | 2 | 3 | **0.25** | `X^2` | 13 | 8 |
| (13, 5) | 2 | 3 | **0.25** | `X^2` | 26 | 8 |

Stage 1b (`K`-coefficient, 200 draws per cell, 0 degenerate):

| cell | bound | M1 | max N |
|---|---|---|---|
| n=11, n'=6, d=3 | 9 | 0.6667 | 6 |
| n=11, n'=6, d=5 | 25 | 0.2000 | 5 |
| n=11, n'=6, d=7 | 49 | 0.1224 | 6 |
| n=13, n'=7, d=3 | 9 | 0.5556 | 5 |
| n=13, n'=7, d=5 | 25 | 0.2000 | 5 |
| n=13, n'=7, d=7 | 49 | 0.0816 | 4 |

Stage 3 (`n = 131`): M1 = **0.054977** at `n' = 33` (`X^7 + X^2`, N = 132,
bound 2401); **0.074074** at `n' = 44` (`X^3`, N = 2, bound 27);
**0.222222** at `n' = 66` (`X^3`, N = 2, bound 9).

**M1 <= 1 at every cell of Stages 1, 1b, 2 and 3. The largest ratio observed
anywhere is exactly 1, at (7, 3).** Candidates above the bound, by stage:
Stage 1 **0**, Stage 1b **0**, Stage 2 **0**, Stage 3 **0**.

### M2 — the three-instrument agreement matrix

Stage 1, all 1260 candidates, all three instruments on every one:

|  | I1 | I2 | I3 |
|---|---|---|---|
| **I1** | 0 | **0** | **0** |
| **I2** | **0** | 0 | **0** |
| **I3** | **0** | **0** | 0 |

Candidates compared 1260; candidates on which all three returned the same `N`:
**1260**. **Disagreeing candidates: none — the list is empty.**

Stage 1b subset (more than one instrument on every draw; I1 additionally on
120 of the 1200): `I1_vs_I2 = 0`, `I1_vs_I3 = 0`, `I2_vs_I3 = 0`.

Stage 2: I1 ran on **10444** candidates (every candidate at `n <= 13`) with
**0** disagreements against I2; I3 ran on **342** of the 356 near-complete
candidates with **0** disagreements against I2.

### M3 — the complete-splitter and near-complete tables

Sweep totals: **95 cells, 42244 candidates, 356 near-complete
(`N >= 2^{n'-1}`), 65 complete splitters (`N = 2^{n'}`)**.

Complete splittings occur at exactly four cells:

| cell | complete splitters | d values | exact corollary `n/(n+n'-r)` | conservative `n(n'-1)/(n'(n+n'-r))` | beta range | min(beta − exact) | min(beta − conservative) |
|---|---|---|---|---|---|---|---|
| (7, 3) | 36 | 2×d2, 4×d4, 4×d5, 8×d6, 18×d7 | 0.777778 | 0.518519 | 0.7778 … 2.1835 | **0.000000** | 0.259259 |
| (7, 4) | 3 | d4, d6, d8 | 0.875000 | 0.656250 | 0.8750 … 1.3125 | **0.000000** | 0.218750 |
| (31, 5) | 24 | 4×d4, 4×d6, 6×d7, 10×d8 | 0.885714 | 0.708571 | 2.4800 … 3.7200 | 1.594286 | 1.771429 |
| (31, 6) | 2 | d4, d8 | 0.861111 | 0.717593 | 1.7222 … 2.5833 | 0.861111 | 1.004630 |

**Complete splitters with beta below the exact corollary: 0. Below the
conservative corollary: 0.** Minimum of `beta − exact` over all 65 splitters:
**0.000000** (equality, at (7, 3) `X^2 + X` and at (7, 4) `X^4 + X^2 + X`).
Minimum of `beta − conservative`: **0.21875**.

The full 356-row near-complete table with the same columns is
`metrics.json -> M3_near_complete_rows`, and the full 65-row complete table is
`metrics.json -> M3.complete_splitters`.

### M4 — the `n = 131` census

`K = F_2[z]/(z^131 + z^13 + z^2 + z + 1)`. 244 non-linearized lambda of exact
degree 3..7 per cell, 732 in total. Instrument I3 only.

| n' | q | r | max N | attaining lambda | bound there | M1 | histogram of N | N>0 | certificates | orbit-carrying | slack max |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 33 | 3 | 32 | **132** | `X^7 + X^2` | 2401 | 0.054977 | `{0: 62, 1: 118, 2: 60, 132: 4}` | 182 | 182 | **4** | 2 |
| 44 | 2 | 43 | **2** | `X^3` | 27 | 0.074074 | `{0: 62, 1: 122, 2: 60}` | 182 | 182 | **0** | 0 |
| 66 | 1 | 65 | **2** | `X^3` | 9 | 0.222222 | `{0: 62, 1: 122, 2: 60}` | 182 | 182 | **0** | 2 |

The four orbit-carrying candidates at `n' = 33`, each with orbit sizes
`[1, 131]` (one `F_2` root plus one full Frobenius orbit), `N = 132`, slack 0:

    X^7 + X^2
    X^7 + X^5 + 1
    X^7 + X^6 + X^3 + X^2
    X^7 + X^6 + X^5 + X^4 + X^3 + X + 1

**546 certificates written (182 per cell), and all 546 independently
re-verified by the wrapper: 0 failures.** Each certificate lists every root as
a coefficient vector over `F_2[z]/(z^131 + z^13 + z^2 + z + 1)`, grouped into
Frobenius orbits, plus the slack and the re-verification result; the wrapper
evaluates `x^{2^{n'}} - lambda(x)` in `K` directly and asserts zero, and
asserts pairwise distinctness. Paths:
`runs/RUN-QSP-33b442-S3/certificates/np{33,44,66}_lam0x*.json`; the per-cell
row tables with the certificate path per candidate are
`runs/RUN-QSP-33b442-S3/cells/n131_np{33,44,66}.json`.

### M5 — Stage 4, rational lambda

200 draws per cell, seed streams `20260917:stage4:n11-np6` and
`20260917:stage4:n23-np12`. Conjectured bound at `d <= 3`, `q = 1`:
`d^{q+1} + 2^{n'-r} + q d^q = 9 + 2 + 3 = 14`.

| cell | max N | histogram | draws above the conjectured bound |
|---|---|---|---|
| (11, 6) | **2** | `{0: 91, 1: 87, 2: 22}` | **0** |
| (23, 12) | **2** | `{0: 92, 1: 89, 2: 19}` | **0** |

At `n = 11` every draw was additionally counted by brute enumeration of all
2048 elements of `K`: **0 disagreements** with the gcd count. At `n = 23`
enumeration of `2^23` elements was not run.

### M6 — the forced fixtures, measured versus forced

| control | cell | lambda | forced | measured | instruments that ran | bound | attains |
|---|---|---|---|---|---|---|---|
| C1 | (12, 6) | `X` | **64** | **64, 64, 64** | I1, I2, I3 (+C6) | 64 | yes (vacuous, r = 0) |
| C2 | (7, 3) | `X^2 + X` | **8** | **8, 8, 8** | I1, I2, I3 (+C6) | 8 | yes |
| C3 | (31, 15) | `X^128 + X^8 + X^2 + X` | **32768** | **32768** | I2 (+C6) | 2097152 | no (ratio 0.0156, admitted with room) |
| C4 | (3, 2) | `X^2 + X` | **4** | **4, 4, 4** | I1, I2, I3 (+C6) | 4 | yes |

**M6 = (64, 8, 32768, 4) exactly.** C3 carries one measuring instrument (I2)
plus the independent C6 decision procedure: I1 is not affordable at `2^31`
elements and I3 is above the `AMD-20260917-001` cap (`deg D = 2097152`). Both
exclusions are declared in the amendment, which was authored before the run.

### M8 — slack (D-roots discarded by the closing test)

Stage 1, per cell: (11,6) max 22, mean 1.0238; (13,7) max 26, mean 0.7063;
(7,3) max **63**, mean 0.8333; (11,4) max 33, mean 0.2619; (13,5) max **0**,
mean **0.0**. Stage 1b: cell maxima 6, 6, 6, 8, 4, 8; means 0.89–1.22.
Stage 3: `n' = 33` max 2, `n' = 44` max **0**, `n' = 66` max 2.

The (13, 5) cell is the calibration extreme in one direction: `D` has no
`K`-root that is not a root of `L` anywhere in that cell, so the injection is
exact there on all 252 candidates. The (7, 3) maximum of 63 is the opposite
extreme: `deg D = 343` at `d = 7` and up to 63 of its `K`-roots fail the
closing test.

### M9 — null-object statistics

Stage 3 orbit tail (Poisson mean `244/131 = 1.8626` under H2):

| cell | orbit-carrying candidates | upper-tail P(X >= observed) | refutes H2 at 0.01? |
|---|---|---|---|
| n' = 33 | 4 | **0.1190** | no |
| n' = 44 | 0 | 1.0000 | no |
| n' = 66 | 0 | 1.0000 | no |

Stage 1b (C5): **0** draws with `N >= n` in any of the six cells; the largest
`N` per cell is 6, 5, 6, 5, 5, 4 against bounds 9, 25, 49, 9, 25, 49.
*Caveat recorded in the run:* with `K` coefficients the root set of `L` is not
Frobenius-stable and does not decompose into orbits, so this row counts draws
whose distinct-root count reaches `n`, as the closest available analogue. The
genuine orbit statistic of this experiment is the Stage 3 census.

### M10 — resources

In the run inventory table above. Census cost for the next census: the Stage 3
`n = 131` census of 732 candidates with 546 re-verified certificates cost
**143.8 s wall / 143.9 s CPU / 52.5 MiB peak** on one worker. The dominant
cost of this contract was **Stage 2 at 1099 s**, not Stage 3 — the contract's
design-time estimate had these the other way round (see §4).

---

## 2. ARITHMETIC, NOT MEASURED — M7

**Every row in this section is a closed-form evaluation of the corollary (B)
and of Proposition 8 of `KN-LIT-4fe9d2`. Nothing here was measured by this
experiment and nothing here is evidence about (A) or (B).**

Definitions used: `beta >= n/(n + n' - r)` with `n = 131`, `r = 131 mod n'`
(the exact corollary); `alpha_beta = 1/(2 kappa beta)` and, for `m >> 1`, the
exponent `1 - alpha_beta/2` (Proposition 8); `kappa = 4.876` (Rojas, as used in
Remark 1 of `KN-LIT-4fe9d2`); rho on ECC2K-130 at `2^60.9` (`KN-LIT-096`).

- **Smallest beta admitted over `n' in 2..130`:** `0.5038462` at `n' = 130`
  (`r = 1`). `alpha_beta = 0.2035206`, exponent `0.8982397`, i.e. `2^117.67`.
- **Smallest Proposition 8 exponent over `n' in 2..130`:** the same row,
  `0.8982397` -> `117.67` bits, **56.77 bits above** rho's `60.9`.
- **The ten `n'` with `131 = -1 mod n'`** (`n' in {2, 3, 4, 6, 11, 12, 22, 33,
  44, 66}`, `r = n' - 1`): all give `beta >= 0.9924242`,
  `alpha_beta = 0.1033259`, exponent `0.9483371` -> `124.23` bits.

*Caveat carried from `KN-LIT-4fe9d2` "Limits of applicability": Proposition 8's
asymptotics assume `m >> 1` with `m` fixed, a regime that does not exist at a
concrete `n` where `m` is an integer near `n/n'`. The full 129-row table is
`metrics.json -> M7_arithmetic_not_measured.all_rows`.*

H1 — the cost model under which the closure reading (E) is stated — is **not
tested by this contract and cannot be**; its scheduled validation route
`IDEA-20260916-b84e2d` carries a recorded engine impediment. Nothing here
validates it.

---

## 3. Gate record

| gate | outcome | evidence |
|---|---|---|
| Stage 0 hand re-derivation, identities (i)–(vii) | **written and archived before Stage 1 ran** | `runs/RUN-QSP-33b442-S0/derivation-note.md` |
| Stage 0 numeric gate, (4, 3), `X^2+X+1` | **PASS** — hand N = 1, slack 0; I1 = I2 = I3 = 1, slack 0 | `RUN-QSP-33b442-S1` `raw-result.json -> stage_0_numeric_gate` |
| Stage 0 numeric gate, (4, 3), `X^3+1` | **PASS** — hand N = 0, slack 2; I1 = I2 = I3 = 0, D has 2 K-roots, both discarded, slack 2 | same |
| C1 forced 64 | **PASS** (64, 64, 64) | `RUN-QSP-33b442-S1` `forced_fixtures_C1_C4` |
| C2 forced 8 | **PASS** (8, 8, 8) | same |
| C3 forced 32768 | **PASS** (32768, by I2; C6 independently predicts 32768) | same |
| C4 forced 4 | **PASS** (4, 4, 4) | same |
| C5 null object (Stage 1b) | **PASS** — 1200 draws through the same instruments, 0 above the bound, histograms and orbit statistics reported | `RUN-QSP-33b442-S1B` `C5_null_object` |
| C6 linearized cross-check vs Proposition 2 | **PASS** — 30 linearized candidates in Stage 1 and 1170 in Stage 2, **0 disagreements** with `N = 2^{deg gcd(f, T^n - 1)}` | `RUN-QSP-33b442-S1`/`-S2B` `C6_linearized_cross_check` |
| Three-instrument agreement on all 1260 Stage 1 candidates | **PASS** — M2 = 0 | `RUN-QSP-33b442-S1` `M2_agreement_matrix` |
| Stage 3 certificate re-verification | **PASS** — 546/546 re-verified, 0 failures | `RUN-QSP-33b442-S3` `certificate_reverification_failures: []` |
| Bound-attaining Stage 1 candidates carry a re-verified root list | **PASS** — 2 candidates (`X^2+X`, `X^2+X+1` at (7,3)), both verified | `RUN-QSP-33b442-S1` cell `n7_np3` |
| `gf2rc.c` parser-fix self-test (a)–(d) | **PASS** — 131073 hex digits echoed intact; oversize lambda rejected with `-1`; 32769 hex digits accepted; 84 candidates vs the independent Python I2, **0 mismatches** | `RUN-QSP-33b442-S2B` `helper_self_test` |

**No gate failed, so no gate has archived failure evidence.**

Tail checks:

- **Attainment tail.** Attained (ratio exactly 1) at (7, 3) by **both**
  `X^2 + X` and `X^2 + X + 1`, each with `N = 8 = 2^3`, as pre-registered; and
  at (7, 4) by `X^4 + X^2 + X` with `N = 16 = 2^4 = d^2`. Exceeded nowhere.
- **Orbit tail at n = 131.** 4 / 0 / 0 orbit-carrying candidates at
  `n' = 33 / 44 / 66`; upper-tail probability 0.1190 at `n' = 33`, above the
  0.01 line, so H2 is not refuted at any cell.
- **Maximum tail.** Largest ratio over all cells and arms: **1.0**, at (7, 3),
  `lambda = X^2 + X`, `N = 8`, bound 8. Largest `N` at `n = 131`: **132**, at
  `n' = 33`, `lambda = X^7 + X^2`, bound 2401, orbit sizes `[1, 131]`, slack 0.
- **Slack tail.** Per-cell maxima in M8 above; the largest anywhere is 63, at
  (7, 3).
- **Null tail.** Largest `N` in the C5 arm per cell: 6, 5, 6, 5, 5, 4 against
  bounds 9, 25, 49, 9, 25, 49.

---

## 4. Discrepancies against the pre-registered exact values

The contract's `preregistered_prediction.formula` lists exact values quoted
from the pre-compute audit as CONTEXT, to be reproduced from scratch. They are
two computations of the same quantity; a mismatch is a discrepancy to be
localised, never a falsification and never silently reconciled.

| pre-registered value | this run measured | agrees? |
|---|---|---|
| M1 <= 0.52 at (11, 6) | 0.52 | yes |
| M1 <= 0.56 at (13, 7) | 0.56 | yes |
| M1 = 1.00 at (7, 3) | 1.00 | yes |
| M1 <= 0.25 at (11, 4) | 0.25 | yes |
| M1 <= 0.25 at (13, 5) | 0.25 | yes |
| complete splittings ONLY at (7,3), (7,4), (31,5), (31,6) | exactly those four cells | yes |
| 356 near-complete rows | 356 | yes |
| 65 complete splitters | 65 | yes |
| 0 violations | 0 | yes |
| Stage 3 max N = 132 at n' = 33 | 132 | yes |
| histogram `{0:62, 1:118, 2:60, 132:4}` at n' = 33 | identical | yes |
| the four N = 132 candidates | identical, same four polynomials | yes |
| max N = 2 at n' = 44 and n' = 66, histogram `{0:62, 1:122, 2:60}` each | identical | yes |
| M2 = 0 | 0 | yes |
| M6 = (64, 8, 32768, 4) | (64, 8, 32768, 4) | yes |

**NO NUMERIC DISCREPANCY WAS FOUND against any pre-registered exact value.**

Three **non-numeric** observations, recorded rather than reconciled:

1. **`(7, 4)` attainment, plural vs singular.** The attainment tail check says
   the bound is attained at (7, 4) "by the `d = 4` complete splitters with
   `N = 16`". This run finds exactly **one** complete splitter of degree 4 at
   (7, 4) — `X^4 + X^2 + X` — and it does attain the bound. The other two
   complete splitters there have `d = 6` and `d = 8`, so their bounds are 36
   and 64 and their ratios are below 1. The tail check is satisfied; the plural
   is the only thing that does not match, and the count (3 complete splitters
   at (7, 4), of which 1 has `d = 4`) is what the run measured.
2. **Cost profile inverted.** `budget.note` estimates Stage 3 as "the dominant
   cost ... of order one hour" and Stages 1/1b/2 as "a few minutes each". This
   run measured Stage 3 at **143.8 s** and Stage 2 at **1099.1 s**. The
   estimate described a different implementation (the pre-compute audit's,
   which is not this experiment's); the measured figures are M10. Not a
   discrepancy against any pre-registered *result*.
3. **14 near-complete Stage 2 candidates were not put through I3**, under the
   cap declared in `AMD-20260917-001` before the run: their `deg D` is
   2097152 (10 candidates), 14348907 (2) and 43046721 (2). Their `N` rests on
   I2 alone. The amendment predicted exactly this exclusion set from the
   contract's own cell definitions, and the realised set matches it.

---

## 5. Falsification branches reached

**None. F0, F1, F2, F3, F4, F5 and F6 were all not reached.** Stated without
interpretation, branch by branch, with what was measured:

- **F0** (Stage 0 fails): not reached. Every identity re-derived; the (4, 3)
  hand counts (1 with slack 0; 0 with slack 2) agree with all three instruments.
- **F1** (a non-degenerate candidate above the bound, certified): not reached.
  0 candidates above `max(d^{q+1}, 2^{n'-r})` in Stage 1 (1260), Stage 1b
  (1200), Stage 2 (42244) or Stage 3 (732). No degenerate candidate (`D = 0`)
  was encountered at any cell of any stage.
- **F2** (a complete splitter with beta below the exact corollary): not
  reached. 0 of 65, with minimum `beta - exact = 0.000000` (equality at two
  splitters) and minimum `beta - conservative = 0.21875`.
- **F3** (C2 or C4 returning the right count but not attaining the bound): not
  reached. C2 attains `8 = max(2^3, 2^2)`; C4 attains `4 = max(2^2, 2^1)`.
- **F4** (a Stage 4 draw above the conjectured rational bound): not reached.
  0 of 400 draws above 14.
- **F5** (instrument disagreement, or a fixture off its forced count): not
  reached. 0 disagreements in Stage 1 (1260 x 3 instruments), Stage 1b, Stage 2
  (10444 I1-vs-I2, 342 I3-vs-I2), the C6 cross-check (1200 linearized
  candidates), and the Stage 4 brute cross-check (200 draws). All four forced
  fixtures returned their forced values.
- **F6** (timeout, crash, memory cap, budget exhaustion): not reached. No run
  timed out, crashed or was killed by a resource cap; peak RSS 70.5 MiB against
  4 GB. `RUN-QSP-33b442-S2` was terminated **by the Executor** after diagnosing
  an implementation defect — that is `implementation_error`, not `F6`, and it
  is recorded as such.

---

## 6. Stage 4 obligation — (D)(ii) is recorded as **WITHDRAWN AS STATED**

`stage_4.obligation` admits exactly two outcomes: the pole bookkeeping of
`H-QSP-5540d7` (D)(ii) is **written out** as a derivation note, or the
extension is **recorded as WITHDRAWN**. There is no third outcome, and a
fixture that passes without the bookkeeping written out leaves the extension
conjectural.

**The Executor records (D)(ii) as WITHDRAWN AS STATED.** The bookkeeping is a
derivation, and writing a new derivation is not this task's authority; the
fixture passing on 400 of 400 draws does not discharge the obligation. (A) and
(B) are untouched by this, exactly as `stage_4.obligation` says.

For the Coordinator's convenience only, and explicitly **not** the required
bookkeeping and **not** relied on by anything above: the shape a bookkeeping
would have to take is a bound on the set of `x` meeting a pole along the chain
— at step `k` the `k`-th iterate of a degree-`d` rational map has numerator and
denominator of degree at most `d^k`, so the `x` whose step-`k` denominator
vanishes number at most `d^k`, and `sum_{k=1}^{q} d^k <= q d^q` for `d >= 1`.
What that sketch does **not** do, and what a real bookkeeping must, is handle
the coefficient twists along the chain, verify that the denominator degree
bound survives them, and verify that no cancellation makes numerator and
denominator non-coprime at an intermediate step. Until someone does that, the
extension stays conjectural.

---

## 7. Closure block (`docs/inventor-protocol.md` section 4)

Filled from **this run's own numbers**, with the scope stated exactly. This is
a record of what was measured, not a verdict; section 4 closure status is the
Coordinator's to assign.

**Named obstruction.** The `K`-rational fibre of the quasi-subfield relaxation
is bounded by the degree of the difference polynomial
`D(Y) = Lambda_{q+1}(Y) - Y^{p^{n'-r}}`: every `K`-root of
`L = X^{p^{n'}} - lambda(X)` is a root of `D`, so the root set that would serve
as a factor base has at most `max(d^{q+1}, p^{n'-r})` elements whenever
`D != 0`.

**Argument.** (Stage 0, hand-re-derived and archived; numerically checked here,
not proved here.) Frobenius is a ring homomorphism, so
`f(z)^{p^k} = f^{(k)}(z^{p^k})`; iterating along `L` gives
`x^{p^{(k+1)n'}} = Lambda_{k+1}(x)` for every root `x`; for `x in K`,
`(q+1)n' = n + (n'-r)` collapses the left side to `x^{p^{n'-r}}`, so
`D(x) = 0`; comparing degrees gives the bound; and complete splitting with
`r >= 1` forces `d^{q+1} >= p^{n'}`, hence `beta >= n/(n + n' - r) > 1/2`.
What this run adds to the argument is **certification and refutation-seeking**,
not proof: 1260 exhaustive toy candidates under three instruments that agreed
on every one; 42244 swept candidates with 65 complete splitters, none below
either corollary and two at exact equality; 1200 seeded `K`-coefficient draws,
none above the bound; and 732 exact, independently re-verified counts at
`n = 131`, the largest of which is 132 against a ceiling of 2401.

**Scope, stated exactly and not exceeded.** `p = 2` in every numerical cell;
the move to general `p` is by the derivation and **never** by measurement.
The Stage 3 certificates certify exactly the **732 enumerated lambda**
(3 cells x 244 non-linearized `F_2`-coefficient lambda of exact degree 3..7);
every other lambda in `F_{2^131}[X]` at those `n'` is covered by the
derivation, not by a list. The Stage 1b arm covers `K`-coefficient lambda only
at `n in {11, 13}`, `d in {3, 5, 7}`, 200 draws per cell — powered to detect a
1.5% per-draw violation rate at 0.951 per cell and 0.25% at 0.950 jointly, and
nothing smaller. Stage 2 covers prime `n <= 31`, `n' <= 15`, `d <= 8` only.
**No statement about any deployed curve follows from any number here. No
attack was run, no curve, point or group was constructed, and no exponent
moved.** The closure reading (E) of `H-QSP-5540d7` stays conditional on the
unvalidated H1 whatever these numbers are.

**Forward guidance — what remains open.**
1. `n' | n` (Diem's subfield family), where the bound is vacuous by
   construction — at `n = 131` only `n' in {1, 131}`. C1 measured the vacuity
   at (12, 6): forced 64, bound 64.
2. Correspondence shapes of conjugate degree `>= 2` (`IDEA-20260916-a17f43`),
   which are not root sets of a single `X^{p^{n'}} - lambda`.
3. Factor bases that are not root sets of any such `L`.
4. **H1 itself**, which this contract does not test and whose route
   (`IDEA-20260916-b84e2d`) is blocked by a recorded engine impediment (no
   Groebner or resultant engine in this container — re-confirmed by this run's
   `environment.json`, which records `sage`, `magma`, `macaulay2`, `singular`,
   `msolve`, `ntl_or_flint` all absent).
5. The rational-lambda extension (D)(ii), recorded WITHDRAWN AS STATED in
   section 6.
6. **A sub-quadratic `GF(2)[X]` reduction**, which is the one tooling item this
   run's own measurements identify: 14 near-complete Stage 2 candidates
   (`deg D` up to 43046721) could not be put through I3 for that reason alone.

---

## 8. Obstruction block (`templates/research-records.md`)

```yaml
obstruction:
  statement: >-
    The K-rational fibre of the quasi-subfield relaxation is bounded by the
    degree of the difference polynomial D(Y) = Lambda_{q+1}(Y) - Y^{p^{n'-r}}:
    for lambda polynomial with n' not dividing n, the root set
    {x in K : x^{p^{n'}} = lambda(x)} has at most max(d^{q+1}, p^{n'-r})
    elements, so at n = 131 it is at most d^{q+1}, i.e. at most 2401 / 343 / 49
    at n' = 33 / 44 / 66. This is a claim about the OBJECT -- the root set of
    X^{p^{n'}} - lambda -- and not about any attempt to search it.
  quantity: >-
    N_K(L), the number of DISTINCT K-roots of L = X^{2^{n'}} + lambda(X),
    measured exactly, and its ratio to max(d^{q+1}, 2^{n'-r}).
  value: >-
    At n = 131 (exact counts, no estimator, no error bars -- these are integer
    counts of a finite set, each carrying an independently re-verified root
    list): max N = 132 at n' = 33 (ratio 0.054977 of the ceiling 2401), max
    N = 2 at n' = 44 (ratio 0.074074 of 27) and max N = 2 at n' = 66 (ratio
    0.222222 of 9), over 244 candidates per cell. A factor base at n' = 33
    needs 2^33 elements; the largest root set found among the 244 enumerated
    non-linearized lambda has 132, i.e. 26 binary orders of magnitude short.
    Over the toy arms: the ratio N / max(d^{q+1}, 2^{n'-r}) never exceeded 1 on
    1260 exhaustive, 1200 seeded and 42244 swept candidates, and equalled 1 at
    two of them. Over 65 complete splitters, beta - n/(n + n' - r) >= 0
    everywhere, with minimum exactly 0.
  measured_by:
    - RUN-QSP-33b442-S1      # 1260 exhaustive F_2 candidates, three instruments, M2 = 0
    - RUN-QSP-33b442-S1B     # 1200 seeded K-coefficient draws (control C5)
    - RUN-QSP-33b442-S2B     # 42244-candidate sweep, 356 near-complete, 65 complete
    - RUN-QSP-33b442-S3      # the 732-candidate n = 131 census, 546 re-verified certificates
    - RUN-QSP-33b442-S4      # 400 rational-lambda draws
    - EXP-QSP-33b442
  scope: >-
    p = 2 in every cell. Exhaustive arms: (n, n') in {(11,6), (13,7), (7,3),
    (11,4), (13,5)}, every lambda in F_2[X] of exact degree 2..7. Sweep: n
    prime in {7,11,13,17,19,23,29,31}, 2 <= n' <= 15 with n' < n and n' not
    dividing n, 2 <= d <= min(8, 2^{n'}-1). Census: n = 131 over
    F_2[z]/(z^131+z^13+z^2+z+1), n' in {33,44,66}, every NON-LINEARIZED lambda
    in F_2[X] of exact degree 3..7 (244 per cell) -- linearized lambda are
    excluded and decided by Proposition 2 instead. K-coefficient arm: n in
    {11,13} only, d in {3,5,7}, 200 seeded draws per cell. Rational arm:
    (11,6) and (23,12), deg a, deg b <= 3. The obstruction is claimed NOWHERE
    ELSE: not at n' | n, not for factor bases that are not root sets of a
    single X^{p^{n'}} - lambda, not for general p by measurement (only by the
    derivation), and not for the 14 Stage 2 candidates whose deg D exceeded
    the AMD-20260917-001 cap, whose N rests on I2 alone.
  resource_check:
    examined: true
    reading: >-
      The check ran, and it found a reading. Read the other way round, the
      measured quantity is a CONSTRUCTION BUDGET rather than a wall: the four
      candidates at n' = 33 with N = 132 are explicit, certified,
      non-linearized degree-7 lambda over F_2 whose root set is a full
      Frobenius orbit plus an F_2 point in F_{2^131}, with slack 0 (every
      K-root of D is a root of L). Anything that needs a small, exactly-known,
      Frobenius-stable subset of F_{2^131} defined by one low-degree polynomial
      condition -- a test-vector set, a structured-input fixture, an
      orbit-reduction benchmark, or the null object of a later census -- can
      take those four root lists off the shelf from
      RUN-QSP-33b442-S3/certificates/. A second reading: the SLACK column is a
      measured calibration of how loose (A) is (max 63 at (7,3), identically 0
      across all 252 candidates at (13,5)), which is exactly the quantity a
      later sharpening of (A) would have to attack, and it is now recorded per
      candidate rather than having to be re-measured. A third, weaker reading:
      the 14 uncomputed near-complete candidates price a concrete tooling gap
      (no sub-quadratic GF(2)[X] reduction in this container) that several
      other lanes would also pay.
    spawned_ids: []      # the Executor does not create IDEA-*/H-* records;
                         # the three readings above are offered to the
                         # Coordinator, which owns that decision
```

---

## 9. What is MEASURED and what is ARITHMETIC

**MEASURED** — produced by this experiment's own runs from exhaustive
enumeration, gcd, and certified root extraction, with no model and no estimator
between the number and the quantity: **M1, M2, M3, M4, M5, M6, M8, M9, M10** —
every per-candidate count, every ratio, every agreement cell, every complete
splitter and its two corollary values, every `n = 131` root list, every slack,
every histogram, and every resource figure in sections 0 and 1.

**ARITHMETIC / MODELED** — computed in closed form from the derivation and from
cited published results, **not measured here**, printed in section 2 so it
cannot be read as a measurement: **M7 in its entirety** (the beta table at
`n = 131`, the Proposition 8 exponents at `kappa = 4.876`, the comparison
against rho's `2^60.9`). Also modeled: H2's Poisson reference distribution used
in the orbit tail checks of M9 — the *observed* orbit counts (4, 0, 0) are
measured, the Poisson mean 1.8626 and the tail probabilities 0.1190 / 1.0 / 1.0
are computed from the model.

**NOT PRESENT AT ALL:** any cost formula standing in for a measured
decomposition cost. H1 is not measured here.

**Declaration.** No number in this report, in `metrics.json`, or in any
`raw-result.json` of this experiment was taken from
`analysis/qsp-ecc2k130/explore/`. Every one was computed by
`experiments/EXP-QSP-33b442/implementation/` during the runs listed in
section 0.
