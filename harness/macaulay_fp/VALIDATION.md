# harness/macaulay_fp — validation note (TASK-20260903-ba41aa)

Tooling prerequisite for EXP-PFDR-fd901a / -5726af / -cbdefb / -20ee58 /
-4bfc6f. Zero experiment runs: this note reports TESTS of an instrument, not
evidence about any hypothesis. Nothing here supports, refutes, or closes any
`H-*` record.

Approval basis read before starting: `ledger/decisions/DEC-20260903-93862f.yaml`
committed at `c5742969` ("approve(DEC-20260903-93862f): six PFDR contracts
approved ..."), which names this handoff in `target_ids`.

## 1. Deliverables (all under the declared write scope)

| path | role | sha256 |
|---|---|---|
| `harness/macaulay_fp/__init__.py` | public API | `3f1ed1fc59f8b059fab94ba4f61716dcacefbda26f5598ec3aef79818b28630f` |
| `harness/macaulay_fp/poly.py` | ring shape, (mask, exps) monomials, exact F_p polynomial arithmetic | `0490eb22e944872c2214eb7a10fd37d0641346aefdf392786533e1c66756af1e` |
| `harness/macaulay_fp/linalg.py` | exact row echelon (int bitsets at p = 2, dict rows at p > 2), fall basis | `9f77e14f5264878ef490f1d4b4d534f04c32880733b5c1c859995997c6accd1a` |
| `harness/macaulay_fp/columns.py` | column space, pre-flight size gate | `b9725c1c2ac51ddd1ef250f7608047d0bc4d5e441c48ae667c3ebec037a75a62` |
| `harness/macaulay_fp/series.py` | semi-regular series prediction, D_reg, growth of an extra generator | `ae1d5a333782b6c29c6dfb84923c9e1f24290ca0d1709f231d8b1d1496b0288c` |
| `harness/macaulay_fp/koszul.py` | explicit Koszul / Frobenius counts | `fdf94aaedc0c3de3e7b96a3d13835227f40d8be8d782ce81b03f4c1498b5cbfa` |
| `harness/macaulay_fp/macaulay.py` | layers, rank profile, fall_dim, syzygy_dim, deficits, profiles | `d1ba2f75e1f479549d6e10a03b6fefb882446c957eecba0250945fe14d31937f` |
| `harness/macaulay_fp/localization.py` | EXP-ALPF-013 localization / shrink bit | `97be3005d955cb1be9079864276feba6c3542c72a6b01a5dae6b042a1dab62ea` |
| `harness/macaulay_fp/nulls.py` | histogram-matched, support-matched, block-factored nulls; coefficient scramble; DREG `boolean_null` port | `07121755f8d85d5c2bf9851276833614d45a3cfd9a7a8957874e9495e51c81be` |
| `harness/macaulay_fp/presentations.py` | direct / digit presentations, f_V, membership generators | `d846300dd70893013fd6a93593d3073436555104a25598f6839d801025f47db1` |
| `harness/macaulay_fp/fixtures/gf2_chained_builder.py` | pure-Python reconstruction of the EXP-DREG-001 GF(2) chained builder | `805790da8fda86c72a710515ed279ebfb4a8d04645151ad1ad900f80ab9477a3` |
| `harness/macaulay_fp/fixtures/chained_gf2_n12_t3_seed2026.json` | the p = 2 known-answer fixture (n = 12, k = 4) | `62d89109f94ef658885ddb5289504df159de01ee4341852b34349d01724bf8e5` |
| `tests/test_macaulay_fp.py` | test suite (52 tests) | `2bff30a4c4720542971062ddc15fd28794e05a5153580ebd6d7ae5e035096b34` |
| `harness/macaulay_fp/VALIDATION.md` | this note | (self) |

Dependencies: Python 3.11 standard library only for the meter. `sympy` 1.14
is used by the TESTS as an independent rank oracle (`DomainMatrix` over
`GF(p)`); `numpy` is not used. No Sage, no floating point anywhere in a rank.

## 2. Test results as run locally

Host: Linux 6.18.44-fc-v24 x86_64, 4 cores, Python 3.11.15, sympy 1.14.0,
numpy 2.4.6 (present, unused). Repository HEAD when the task started:
`c57429694af615f64d2e691a0df25e1b131f4875` (clean tree); HEAD when the note
was written: `6e38a5b07c03b59c573cea9ca90892c28337f957` (moved by another
session while this task ran; the working tree then showed only the two
untracked deliverable paths `harness/macaulay_fp/` and
`tests/test_macaulay_fp.py`, nothing else modified).

Command and verbatim summary line (run from the repository root):

```
python3 -m pytest tests/test_macaulay_fp.py -q
....................................................                     [100%]
52 passed in 2.38s
```

The final confirmation run after this note was written is recorded in §11.

## 3. Implementation note: ported unchanged, generalised, added

Ported UNCHANGED in semantics from `experiments/EXP-SBRG-60c55e/driver/macaulay.py`
(read-only; nothing in that file was touched):

- `GF2Basis` → `linalg.Echelon` at p = 2 (same int-bitset rows, same
  highest-bit pivot rule, same XOR loop, same zero-row accounting).
- `multiply_by_monomial` (bitwise OR = reduction a^2 → a with cancellation on
  collision) → `Ring.mul_monomial` at p = 2.
- `all_monomials_exact/upto`, `ColumnSpace` (degree-ascending column order),
  `layer_rows` (multipliers of degree exactly D − deg f_i, zero-product rows
  kept), `analyze_layer` metrics (`row_count, top_rank, full_rank, fall_dim =
  full − top, syzygy_dim = rows − full, zero_product_rows, nnz_total, nnz_top`),
  `analyze_degrees`, `degree_histogram`, `random_matched_polynomial` (support
  sampling AND the planted-root swap procedure), `random_matched_system`,
  `first_nonzero_fall`, `first_excess_fall`.
- `analyze_batch_reuse` was NOT ported (batch row-space reuse is not a
  battery requirement); its test is re-asserted against the port's layer rank.

GENERALISED:

- Polynomials: `frozenset[int]` → `dict[(mask, exps), coeff]` with coefficients
  in [1, p−1]; squarefree variables keep the bitmask, free variables carry an
  exponent tuple. Total degree = popcount(mask) + sum(exps).
- Elimination: p > 2 uses dict rows with normalised pivots; residues reduced
  mod p at every axpy. Python ints give word-size arithmetic below 2^62 and
  arbitrary precision above transparently (handoff item 8); tested at the
  P-256 prime against the sympy oracle.
- `fall_dim` and `top_rank` come from ONE elimination: with top-degree columns
  at the highest indices and highest-column pivots, echelon rows with a pivot
  in the top block are independent after top projection and the others have
  zero top projection, so `top_rank = #top-pivot rows` and the lower-pivot
  rows are a basis of the fall space (used for the planted-fall content
  check). The two-elimination route of macaulay.py is kept as
  `verify_layer_two_eliminations` and the identity is tested at p = 2, 4099,
  65537 in all three modes.
- Nulls: histogram-matched carried to F_p (uniform nonzero coefficients on the
  sampled support; at p = 2 bit-identical to macaulay.py's unplanted output,
  tested); planted root at p > 2 by one coefficient correction (support and
  histogram unchanged).

ADDED (handoff items 2–9):

- Three ring modes (`Ring(p, n_sq, n_free)`): squarefree/digit
  (`n_free = 0`), ordinary (`n_sq = 0`), mixed (both; the battery uses
  exactly one free variable u, any number is accepted).
- Cumulative convention (`convention="cumulative"`): multipliers of degree
  ≤ D − deg f_i, zero-product rows dropped — EXP-DREG-001's `macaulay_rows`.
- Series prediction (`series.py`) with the Boolean Frobenius factor
  1/(1 + z^d) or the naive factor (1 − z^d); `koszul_series = rows − pred`,
  `deficit_series = pred − rank`, `D_reg`, `growth_of_extra_generator`.
- Explicit first-order counts (`koszul.py`): pairwise Koszul multiples plus,
  at p = 2 in the pure squarefree ring under the cumulative convention, the
  Frobenius relations f_i^2 = f_i.
- `deficit_profile`: DREG's degree-resolved table (`deficit_cumulative`,
  `deficit_graded`, `deficit_pairwise`, `koszul_*`).
- Leading-form option (`leading_forms=True`): EXP-ALPF-013's phi_D on top
  forms; `first_nontrivial_syzygy` = ALPF's d_ff; `localization_gate` with
  DIRECT (kernel dims) and SHRINK (nontrivial counts) readings, each in the
  pairwise and the series reading.
- Support-matched (identical support) null, block-factored null
  (H-PFDR-4148b8 / IDEA-20260903-e1e38b), coefficient-scramble primitive,
  DREG `boolean_null` verbatim port.
- Pre-flight gate (`columns.preflight`): row/column counts by binomial
  arithmetic before any allocation; `PreflightAbort` carries the counts.
- Presentations (`presentations.py`): direct f_V and digit presentations of
  IDEA-20260830-84cdb7 with the s = 1 identification.

## 4. Conventions chosen (recorded in every `LayerResult`)

1. **Degree of a row after multilinear reduction**: the degree of the reduced
   product. A per-layer row m·f_i with deg m = D − deg f_i may have degree
   < D after a^2 → a collapse; it is kept and counts as a fall (macaulay.py's
   behaviour). Zero products: kept in `row_count` under per-layer (macaulay.py;
   they then count in `syzygy_dim`), dropped under cumulative (DREG);
   `zero_product_rows` always reports the number so either reading can be
   recovered; `keep_zero_rows` overrides.
2. **Top-degree projection in mixed mode**: the columns of TOTAL degree
   exactly D (squarefree count + free exponents). u^2·a_1·a_2 has degree 4.
3. **Boolean series factor** (`frobenius`): defaults to True exactly when
   p = 2 and the ring is pure squarefree (every f satisfies f^2 = f there);
   False at p > 2 (counterexample f = a_1 + a_2: f^2 = f + 2 a_1 a_2, tested)
   and in mixed mode. Always recorded as `frobenius_factor`.
4. **Which deficit is "the" deficit**: `deficit_series = pred − rank` is
   KN-FIND-006's `pred[D] − rank(D)`; `deficit_pairwise = rows − rank −
   koszul_pairwise` is the handoff's `rows(D) − rank(Mac_D) − koszul(D)` with
   the explicit first-order count. Both are reported; they coincide below the
   first second-syzygy degree (they do on the known answer: 78 = 78 at D = 4).
   The per-degree KN-FIND-006 numbers are `deficit_graded` (cumulative
   convention). `top_deficit_series = pred_graded − top_rank` is ALPF-013's
   `nontrivial(D)` for per-layer leading forms.
5. **Localization bit**: `nontriv_full − nontriv_fb` (shrink), computed in
   both the pairwise and series readings, plus ALPF's uncorrected DIRECT test
   `ker_full > ker_fb` (which is True whenever a Koszul pair passes through
   the subset — ALPF-013 evaluates it only at a firing degree; tested).
6. **Nulls**: histogram-matched draws DISTINCT monomials per degree from the
   whole ring; block-factored forms are homogeneous with coefficients uniform
   in F_p (zero allowed) unless `nonzero_coefficients=True`; the support-
   matched null at p = 2 is the identity and is flagged `degenerate_at_p2`.
7. **Series truncation**: HF is read until its first non-positive
   coefficient (DREG); `D_reg` is that degree (ALPF-013). Predictions past
   D_reg are truncated and deficits there are not meaningful.

## 5. Fixture provenance and the p = 2 known answer (G2)

**Archived builder**: `experiments/EXP-DREG-001/runs/RUN-DREG-001-VALIDATE-N12-A/code/h012_peel_rank.py::build_system(n=12, t=3, ti=0, seed=2026)`
(sha256 `c46c871b…`) over `code/semaev_tree.py` (sha256 `e9f1681b…`, byte-
identical to `src/semaev_tree.py`), which requires Sage. The archived run
recorded `system_hash = c47d17c3fd70d5d81127e8d37e21441883f720ca10187f57a3aeb47bfe3ba818`
(`monosets_hash` of the ordered generators), nb = 24, 12 quadrics + 12 cubics,
and at D = 5: nrows 31512, ncols 46717 (realised support), pred 29418, rank
28096, deficit 1322.

**Sage is absent on this host**, so the fixture was regenerated by a pure-Python
reimplementation of the same construction:

```
python3 harness/macaulay_fp/fixtures/gf2_chained_builder.py --root-order int \
    --out harness/macaulay_fp/fixtures/chained_gf2_n12_t3_seed2026.json
# -> sha256 62d89109f94ef658885ddb5289504df159de01ee4341852b34349d01724bf8e5
```

Field F_{2^12} = F_2[x]/(x^12 + x^7 + x^6 + x^5 + x^3 + x + 1) (the Conway
polynomial, COMPUTED from its definition by the builder); curve
y^2 + xy = x^3 + x^2 + α; V = span(1, α, α^2, α^3); rng = `random.Random(2038)`
(= 2026 + 1000·0 + 12); 11 candidate factor-base points; sampled
P_list = [(1, 1742), (5, 729), (15, 3560)] (integers = polynomial-basis
bit-vectors), R = (1875, 2298), R_X = 1875; two chained S_3 equations
Weil-descended to 24 generators (12 quadrics, 12 cubics). The builder is
deterministic (the test rebuilds and compares hashes) and the planted
decomposition is verified to be a common root of all 24 generators.

**DEVIATION D1 — not bit-exact.** The reconstruction's `system_hash` is
`18e0fc8b9746342ab8433ce4b3c87487ea7b86e05a8670ae78618340c67aea80`, which is
NOT the archived `c47d17c3…`. Attempts, all negative: five root-order
conventions for `lift_x`; every R from up to three (multiset) factor-base
points (102 distinct R_X); generator-order variants (per-equation reversal,
equation swap, interleave) × coordinate relabelings (reversed indices within
blocks) — 1020 hashes. The residual difference is therefore in a Sage
representation detail that could not be derived here (the archived run used
Sage 10.9 / Python 3.14.3). What DOES match the archive, exactly: nb = 24,
degree histogram {2: 12, 3: 12}, and at D = 5 the realised support column
count 46717, the row count 31512, pred 29418, rank 28096 and cumulative
deficit 1322 (§7). The known-answer test is therefore on a SAME-CONSTRUCTION
fixture whose every archived invariant is reproduced, not on the byte-exact
archived polynomials; KN-FIND-006 states the integers hold "for every full
system (n ≥ 12)", and the test does not depend on the particular R.

**The convention was established from the DREG artifacts, not chosen by
matching**: `characterization/deficit_by_degree.py` uses `macaulay_rows`
(multipliers of degree ≤ D − deg f, zero products dropped) and
`semireg_rank_pred`, whose in-place update `a[j] -= a[j-d]` divides by
(1 + z^d) — the Bardet–Faugère–Salvy BOOLEAN series — although the prose in
`DREG_DEFICIT_CLOSED_FORM.md` writes the naive product ∏(1 − z^{d_i}) (a
finding about that record's prose, reported here; the code is the
authoritative convention and its pred[5] = 29418 is reproduced). Both
conventions' outputs are recorded below in full.

**Known-answer cell values obtained** (cumulative convention, Boolean series):

| D | rows | cols | rank | pred | koszul (pairwise = series) | deficit_cum | deficit_graded |
|---|---|---|---|---|---|---|---|
| 2 | 12 | 301 | 12 | 12 | 0 | 0 | 0 |
| 3 | 312 | 2325 | 311 | 312 | 0 | **1** | **1** |
| 4 | 3912 | 12951 | 3802 | 3834 | 78 | **32** (= 8k) | **31** (= 8k − 1) |

Null arms at both degrees: DREG `boolean_null` (RNG state continued after the
builder's `sample`) → deficit 0, 0; port's histogram-matched null at seeds 7
and 11 → 0, 0. (The handoff's phrase "support-matched null must return 0" is
KN-FIND-006's name for this histogram-matched construction; the IDENTICAL-
support null is the identity at p = 2 and is flagged, not used, there.)

Recorded, not matched (the other convention / the other series):

| convention | series | D=3 deficit_cum | D=4 deficit_cum | D=4 pred | D=4 koszul_series |
|---|---|---|---|---|---|
| cumulative | naive (1 − z^d) | 1 | 44 | 3846 | 66 |
| per-layer | Boolean | 0 | −67 | 3522 | 78 |
| per-layer | naive | 0 | −55 | 3534 | 66 |

(Per-layer rows 12 / 300 / 3600; per-layer numbers are a different object —
the graded series does not predict per-layer ranks of inhomogeneous
generators — and are listed only so no convention is silently discarded.)

## 6. Planted controls (G3)

Planted-syzygy control (IDEA-20260903-afa56b): base f_1, f_2 random
quadratics; k redundant generators g_j = u_j f_1 + v_j f_2 with random
homogeneous u_j, v_j so deg g_j = D*; cumulative convention; the extended
sequence's Hilbert function at D* is asserted positive (so the series is not
truncated there). Recovery = Z_{D*}(extended) − Z_{D*}(base), by BOTH routes
(`deficit_series` and `deficit_pairwise`):

| mode | ring | D* | k = 1 | k = 2 | k = 4 | k = 8 |
|---|---|---|---|---|---|---|
| squarefree | p = 4099, 10 digit variables | 3, 4 | 1 | 2 | 4 | 8 |
| ordinary | p = 4099, 5 free variables | 3, 4 | 1 | 2 | 4 | 8 |

All exact; the planted rows add zero rank. A mixed-degree variant (one
planted cubic and one planted quartic, D = 3..5) matches the sequential
semi-regular increments at every degree (the F5-equivalent count: every
multiple of a redundant generator reduces to zero).

Planted fall (EXP-PFDR-cbdefb's closure known answer): g = u f_1 + v f_2 + h
with deg h = deg g − 1, per-layer at D = deg g = 4, ordinary and squarefree
modes: `fall_dim` rises by exactly 1, `fall_content_contains(h)` is True for
the extended system and False for the base, and the extended fall space is
the base fall space plus span(h).

## 7. Additional checks recorded (not part of the pass/fail suite)

D = 5 on the fixture, cumulative, Boolean series (6.4 s, single elimination
of 31512 int-bitset rows): realised support columns 46717, rank 28096, pred
29418, cumulative deficit 1322 — all four equal to the archived
RUN-DREG-001-VALIDATE-N12-A values. Explicit trivial count at D = 5:
300 Frobenius + 1650 quadric-pair + 144 quadric–cubic Koszul = 2094 =
31512 − 29418.

## 8. Mod-2 agreement (G4) and coverage (G5)

Every assertion of `experiments/EXP-SBRG-60c55e/tests/test_macaulay.py` is
re-asserted against the port at p = 2, per-layer (`test_mod2_*`), including
the batch-reuse total ranks; additionally the port's unplanted histogram
null is bit-identical to `random_matched_system`'s for three seeds, and four
random 6-variable systems agree layer by layer on all eight layer integers
at D = 2..4 plus `first_nonzero_fall`.

Exercised by at least one test each: squarefree mode (known answer, planted
controls), ordinary mode (planted controls, ALPF controls, P-256, s = 1
slice), mixed mode (total-degree grading, two-elimination identity, oracle,
`LayerResult` record); per-layer and cumulative conventions; `fall_dim`,
`syzygy_dim`, `koszul_pairwise` / `koszul_series`; the localization bit
(POS-A: d_ff = 4, nontriv 3, D_reg 7; NEG-1: no fire, D_reg 4; NEG-2: no
fire, D_reg 7; synthetic gate-POS: nontriv_full 3 > nontriv_fb 1 — the
EXP-ALPF-013 table values); histogram-matched, support-matched and
block-factored nulls plus the scramble primitive; arbitrary precision at the
P-256 prime (planted 256-bit dependency detected, ranks equal to the sympy
`GF(p)` oracle); the pre-flight gate (counts 31512 / 55455 / 42504 at D = 5,
abort before allocation with the counts, counts exact against the realised
layer).

## 9. Stage 0 instrument map (IDEA-20260903-399a18) at this port's state

A FLOOR at HEAD `6e38a5b0`, not a finding. Column C1 (gated d_ff /
localization bit) and C2 (deficit at D = 3, 4) of the 399a18 table now have a
TEST-COVERED F_p instrument for every row whose presentation is expressible
in the three ring modes: the direct f_V presentation (ordinary mode), the
digit presentation of IDEA-20260830-84cdb7 (squarefree, d = 2; ordinary with
membership generators, d > 2), the e-ring of EXP-PFDR-4bfc6f (ordinary mode,
free e_1, e_2, e_3, leading forms, localization) and the chained tree of
EXP-PFDR-20ee58 (mixed mode, one free u, cumulative deficit with Koszul
count). This falsifies 399a18's P1 floor "exactly 0 for C1 and C2 over F_p"
only in the sense that record itself anticipated (F1: "a test-covered F_p
Macaulay deficit meter exists ... the instrument map is corrected with the
path"); the path is `harness/macaulay_fp/`. Not provided here: C3 (yield
counter), C4 (solver cost) for any row, and any instrument for R5's lattice
arm and R4's FFT arm — 399a18's P2 floor "at least 2 rows with no solver
instrument" is unchanged by this task. The table's other cells were not
re-derived.

## 10. Deviations from the handoff and other disclosures

- **D1** Fixture not bit-exact to the archived Sage system (§5); every
  archived invariant reproduced; fallback foreseen by the task text.
- **D2** The handoff's "never run git": read-only `git rev-parse`, `git
  status`, `git log`, `git ls-files` were run to verify the approval commit
  and record the commit / dirty state that the runtime contract requires;
  no git write of any kind was made; nothing was committed.
- **D3** Terminology: the handoff item (7) "support-matched null (identical
  support)" and KN-FIND-006's "support-matched null" (histogram-matched
  random monomials) are different objects; both exist in the port, the
  known-answer null test uses KN-FIND-006's, and the identical-support null
  is flagged degenerate at p = 2.
- **D4** Test-authoring corrections made during development, none of which
  touched an expected value that comes from a record: (i) the explicit
  Koszul count for degrees [2, 2, 4] at D = 8 in three free variables was
  mis-derived by hand as 12 and corrected to 35 + 10 + 10 = 55 from the
  definition; (ii) the planted-syzygy control's rings were enlarged (6 → 10
  squarefree variables; 3 → 5 free variables) after the first runs showed the
  extended sequence's series truncating at D* (D_reg = 4 for two quadrics in
  6 squarefree variables; HF(3) = 10 − 6 − 8 < 0 for 8 planted cubics in 3
  free variables), and the precondition is now asserted; (iii) the NEG-2
  localization expectation was corrected: ALPF-013's DIRECT kernel test is
  not Koszul-corrected and is True at D = 6 through the two Koszul pairs on
  generator 0 while the shrink bit is 0, which is now what the test asserts.
- **D5** `analyze_batch_reuse` not ported (§3).
- **D6** The DREG prose/code series discrepancy (§5) is reported as a
  finding about `DREG_DEFICIT_CLOSED_FORM.md`; no record was edited.
- **D7** HEAD moved from `c5742969` to `6e38a5b0` during the task by another
  session; the deliverables are unaffected (untracked paths only).
- No run directory, `manifest.yaml`, `raw-result.json`, curve, or Semaev
  instance beyond the named fixture was created. `__pycache__` directories
  created by the test run are gitignored and were removed from
  `harness/macaulay_fp/`.

## 11. Inference block

```yaml
inference:
  requested_policy: executor-implementation
  requested_reasoning_effort: medium
  adapter_resolution: "python3 -m orchestration.adapter resolve --role executor -> anthropic:claude-sonnet-5 (effort=medium)"
  runtime_reported_model: claude-fable-5-1
  model_verified: false
  model_verified_note: >-
    The adapter binding (claude-sonnet-5) and the model identifier reported by
    the running session (claude-fable-5-1) differ; the executing agent cannot
    verify its own binding from inside the session. Reported as-is for the
    orchestrator to adjudicate; no claim of "no fallback" is made.
  fallback_used: unknown
  degraded: false
  independent_session: true
```

Final confirmation run (after this note was written):

```
python3 -m pytest tests/test_macaulay_fp.py -q
....................................................                     [100%]
52 passed in 2.31s
```

(HEAD move in D7 identified: `6e38a5b0 runs(EXP-PFDR-c04716): STATIC-001
zero-run static derivation package (TASK-20260903-c7166d)`, committed by the
orchestrating session; it touches no path of this task.)
