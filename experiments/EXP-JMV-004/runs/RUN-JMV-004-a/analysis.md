# analysis.md — RUN-JMV-004-a

## C1 STATUS: PENDING

**This banner applies to every section of this document, without
exception.** The four source statements this run's model depends on
(Theorem 1.1's `m`-formula, Sec 4.3's `k`-approximation, Lemma 4.1's
`c`-bound and normalization, Proposition 3.1's walk-length inequality) are
archived in `source_statements.md` **UNCHECKED-AGAINST-SOURCE**: no agent in
this program has read arXiv:math/0411378v3, and specification.yaml's own
control C1 documents a demonstrated nonzero digit-level corruption rate
elsewhere in the same held plain-text artifact (the K-163 row in a related
scouting exercise). A single transcription error in any of these statements
would flip the sign of `log(k/c)`, which is this run's headline quantity.

**Per specification.yaml's stopping_rules and this task's binding
constraints: this document draws NO conclusion about vacuity or
non-vacuity of the proven eigenvalue separation, about whether Corollary 1.2
is concretely proven at any evaluated size, or about whether a crossover
"exists" in any normative sense.** Everything below is a factual report of
what the model in `cost_model.md`, evaluated at the stated parameters,
outputs -- nothing more. That judgement is reserved for the separate,
not-yet-dispatched C1 review (a digit-level check against the actual paper
by a reviewer who did not produce this transcription) and the evidence
review that follows it.

**C1 STATUS: PENDING.**

---

## 1. What this run computed (recap)

- Grid: the full `(q bit size, delta, log convention, per-step cost
  variant)` grid from specification.yaml's `inputs` block --
  `q_bit_sizes = [64, 96, 128, 160, 192, 224, 256, 320, 384, 512]`,
  `delta_values = [0.25, 0.5, 1.0, 2.0]`, `log convention in {bits,
  natural}` -- PLUS an additional sensitivity sweep over the unpinned
  Lemma 4.1 constant `C in {0.5, 1, 2, 4, 8}` (5 values), PLUS both degree
  conventions computed side by side at every cell (E2). Total:
  `10 x 4 x 2 x 5 = 400` cells, all present in `raw.json` and
  `crossover.csv` (400 data rows; `wc -l crossover.csv` = 401 including
  header). Six per-step-cost variants (3 algorithms x 2 `l`-choices) are
  reported per cell wherever `sign_half = positive` makes `r` finite.
- Precision: `mpmath`, 60 decimal digits throughout (`mp.mp.dps = 60`); zero
  cells flagged `INDETERMINATE_AT_PRECISION` (threshold `|log(k/c)| <
  10^-40`, far above the ~`10^-60` working-precision floor). See
  `manifest.yaml`'s `environment.arbitrary_precision_settings`.
- Branch (b) / EXP-JMV-003: NOT executed, NOT consumed anywhere in this
  computation. `lambda_2` throughout is exclusively the branch (a) proven,
  GRH-conditional Lemma 4.1 bound (with its constant `C` swept, never
  measured). Confirmed by direct code inspection of `compute_grid.py`: no
  reference to `experiments/EXP-JMV-003/` anywhere.

## 2. Sign of `log(k/c)` -- both conventions, both degree conventions (raw data)

`sign_half` (PRIMARY degree convention, `k = Li(m)/2`) and `sign_full` (ALT,
`k = Li(m)`) are reported per cell in `raw.json` / `crossover.csv`
(`sign_log_kc_half_PRIMARY`, `sign_log_kc_full_ALT`). Aggregate counts over
all 400 cells, reported as data:

- **Degree-convention flips** (PRIMARY vs ALT sign differs at the same
  `bits, delta, log_convention, C`): **37 of 400 cells**
  (`stderr.txt`: "degree-convention sign flips (half vs full), count: 37";
  flagged per-cell via `degree_convention_flip` in `crossover.csv`).
- **Log-convention flips** (PRIMARY sign differs between `bits` and
  `natural` at the same `bits, delta, C`): **16 of 200 `(bits, delta, C)`
  triples** (`raw.json`'s `log_convention_flips`; `stderr.txt`:
  "log-convention sign flips (bits vs natural), count: 16"; flagged
  per-cell via `log_convention_flip_bits_vs_natural`).

Per condition E2-CONVENTION, **every one of those flip cells is reported in
`crossover.csv` as CONVENTION-DEPENDENT and is not treated as a directional
result anywhere in this document.** Only cells where both the degree
convention and the log convention agree in sign are reported below as
non-convention-dependent data points.

## 3. Non-flip-cell data at q = 2^256 (both conventions, PRIMARY degree convention)

For the four grid `delta` values, at `C = 1.0` (the middle of the swept
range; other `C` values are in `crossover.csv` in full), `sign_half` at
`bits = 256`:

| delta | bits convention | natural convention | convention-dependent? |
|---|---|---|---|
| 0.25 | negative | negative | no (agree) |
| 0.5  | negative | negative | no (agree) |
| 1.0  | negative | negative | no (agree) |
| 2.0  | positive | positive | no (agree) |

(Source: `raw.json`, cells `bits=256, C='1.0'`, both `log_convention` values,
all four grid `delta`.) These four cells do not flip between logarithm
conventions at `C = 1.0`; this is a data observation about this particular
`C` slice, not a claim that no `C` value anywhere in the swept range
produces a flip at `bits = 256` -- the full 400-cell table in
`crossover.csv` is the complete record, and readers should consult it
directly rather than this table alone.

**`smallest_delta_with_positive_sign_at_bits_256`** (from `raw.json`,
computed directly over the grid's four `delta` values, per `(log_convention,
C)`):

| log convention | C=0.5 | C=1.0 | C=2.0 | C=4.0 | C=8.0 |
|---|---|---|---|---|---|
| bits | 1.0 | 2.0 | 2.0 | 2.0 | none in grid |
| natural | 2.0 | 2.0 | 2.0 | 2.0 | none in grid |

"none in grid" means no `delta` value in `{0.25, 0.5, 1.0, 2.0}` produces
`sign_half = positive` at `bits = 256, C = 8.0`, under either logarithm
convention -- reported as the stopping_rules require: "not_completed" for
that region of the grid, not extrapolated or estimated beyond it.

## 4. Modelled overhead and its ratio to sqrt(n) -- per-step variants

Where `sign_half = positive` (finite `r_half`), `crossover.csv` reports the
total modelled cost and `cost_over_rho` (ratio to `rho = 2^(bits/2)`,
Pollard rho) for all 6 per-step variants (3 algorithms x typical/best-case
`l`). All values are present in `crossover.csv`'s `cost__*` /
`cost_over_rho__*` / `cheaper_than_rho__*` column triples; none are
summarized further here beyond pointing at the file, per the same
convention-dependence and no-conclusion discipline as above -- a numeric
`cost_over_rho` value is itself just a ratio (data), and this document
draws no directional statement ("comparable," "dominant," "negligible" as a
finding) from it, leaving that characterization to the C1-gated review.

## 5. Crossover bit size (per convention, per per-step variant, WITHIN the declared grid delta values only)

Per specification.yaml's metric definition, computed strictly over the
declared grid `delta in {0.25, 0.5, 1.0, 2.0}` and `bits in
{64,...,512}` (NOT the continuous delta sweep used by the supplementary,
non-required `crossover_summary.csv` -- see section 7 below for that file's
scope caveat). At `C = 1.0`, PRIMARY (`phi_l`, typical-`l`) per-step
variant, for each grid `delta`, the smallest grid `bits` at which
`sign_half = positive` AND `total_cost < rho`:

| log convention | delta=0.25 | delta=0.5 | delta=1.0 | delta=2.0 |
|---|---|---|---|---|
| bits    | no crossover within grid | no crossover within grid | no crossover within grid | 192 |
| natural | no crossover within grid | no crossover within grid | no crossover within grid | 192 |

"no crossover within grid" here means: no grid `bits` value produces
`sign_half = positive` for that `delta` at `C = 1.0` (see section 3's
`smallest_delta_with_positive_sign_at_bits_256` table -- at `C=1.0`, `delta
in {0.25, 0.5, 1.0}` never reach a positive sign anywhere in the grid, at
either `bits = 256` or, by the same computation restricted to other `bits`
values, at any grid bit size), NOT a statement that no crossover would ever
occur outside the grid or at unswept `C`. This is the explicit
no-crossover statement specification.yaml's success_criterion permits as a
successful outcome in place of a crossover bit size.

Full per-`C` and per-per-step-variant data for this same computation is
reproducible directly from `raw.json` / `crossover.csv`; this table reports
one representative `C` slice (`C=1.0`) for readability. **No aggregate
"the" crossover bit size is asserted for the model as a whole** -- condition
E2 requires reporting per convention and per per-step variant, which
frequently disagree (see section 7's caveat on the wider
`crossover_summary.csv` sweep, where varying `C` alone moves the reported
crossover from 64 bits to "no crossover in grid" depending on `C` and
per-step variant).

## 6. Precomputation term (E4)

Stated explicitly in `cost_model.md` section 3. Summary: `Phi_l` storage is
NOT assumed free. At `bits=256, delta=1.0, C=1.0` (bits convention),
`m = 16777216 ~= 2^24`, and the modelled per-step storage order is
`m^2 ~= 2^48` coefficients (`phi_l_storage_coeffs_order` in `raw.json`/
`crossover.csv`) -- the full generating-set storage order (all distinct
split-prime `Phi_l` for `l <= m` cached at once) is
`k_half * m^2 ~= 2^30 * 2^48 = 2^78` coefficients at that same cell. Both
figures are reported per cell; no field-operation or byte conversion is
asserted for these coefficient counts (no per-coefficient bit-size formula
is held in this program's corpus -- flagged
`NOT_COMPUTABLE_WITHOUT_CITATION` in `constants_table.csv`).

## 7. Deviations and scope caveats

- **DEV-1** (carried from `manifest.yaml`): Corollary 1.2's own equation-level
  statement is not held verbatim anywhere in this program's corpus; only
  narrative references to it ("polylog(q) oracle queries") exist. See
  `source_statements.md`'s dedicated section. Does not block this run's
  model/grid computation, which uses only Thm 1.1 / Sec 4.3 / Lemma 4.1 /
  Prop 3.1.
- **DEV-2** (carried from `manifest.yaml`): `/usr/bin/time -v` unavailable
  for instrumented peak-memory measurement; wall-clock measured via shell
  timestamps instead. Memory certain to be far under the 2 GB cap by
  construction (400-cell closed-form sweep, no large data structures).
- **DEV-3** (new, this task): the supplementary, NON-required artifact
  `crossover_summary.csv` (inherited from the prior interrupted session)
  computes a "cheapest admissible delta" crossover bit size using a
  CONTINUOUS delta sweep (step 0.05 from 0.05 to 6.0) that extends beyond
  the frozen grid's four declared `delta_values`, and its generation
  script was not archived in this run directory (produced by ad-hoc
  inspection commands per `manifest.yaml`'s own note). It is retained as
  supplementary sensitivity context only, is NOT reproduced or relied upon
  in section 5 above (which uses the strictly-in-grid computation instead),
  and should not be read as satisfying specification.yaml's grid-crossover
  metric on its own -- `crossover.csv` and section 5 of this document are
  the grid-faithful record.

## 8. Confirmations

- No claim_tier other than `not_applicable` appears anywhere in this run's
  artifacts (type `theoretical`, proof_status `derivation`).
- Branch (b) was not executed; no EXP-JMV-003 value was consumed anywhere
  in this computation (confirmed by direct code inspection of
  `compute_grid.py`).
- Both logarithm conventions and both degree conventions are reported side
  by side for every cell; flip cells are reported as CONVENTION-DEPENDENT
  only.
- The precomputation term is stated explicitly (section 6, `cost_model.md`
  section 3); no cost silently assumes free precomputation.
- Every constant used is listed in `constants_table.csv` with source,
  statement number, and governing hypotheses; `C` and `eps` are the two
  without a held numeric citation and are swept/declared, never invented.
- EXP-JMV-005 (the toy sanity anchor) is not reported as attempted,
  passing, or failing anywhere in this run -- it does not exist.
- This document asserts nothing about GRH, ECDLP hardness, attack cost, or
  the D1/BAR-AMORT-D2 barriers.
- **No statement anywhere above asserts that the proven eigenvalue
  separation is vacuous or non-vacuous, that Corollary 1.2 is or is not
  concretely proven at any evaluated size, or that a crossover does or does
  not exist in any normative sense.**

## C1 STATUS: PENDING (restated)

This document stops at the model, the grids, and the constants table, per
specification.yaml's stopping_rules. The conclusion -- if any -- is written
only after the C1 (source-transcription-fidelity) review completes, by a
reviewer who did not produce this transcription.

---

## COORDINATOR ADDENDUM (2026-09-07) -- C1 STATUS: PASSED (VAL-20260907-b0832b)

**This addendum supersedes every "C1 STATUS: PENDING" banner above for
purposes of drawing a conclusion. It does not alter, delete, or edit any of
the Executor's original content above, which remains exactly as archived.**
Everything below is written by the Coordinator after control C1 completed,
per specification.yaml's own gate ("Conclusions are written only after the
C1 review completes") and stopping_rules. No number below is recomputed or
invented; every figure is read directly from `crossover.csv` (400 rows) or
`crossover_summary.csv`, cited by its exact `(bits, delta, log_convention,
C)` cell, or from `VAL-20260907-b0832b.yaml`.

### C1 outcome

`experiments/EXP-JMV-004/reviews/VAL-20260907-b0832b.yaml` is an independent
digit-level check, by a reviewer who did not produce this run's
transcription, of all five transcribed source statements against the
actual retrieved, sha256-pinned PDF (`inputs/JMV-0411378-20260907/`).
**Verdict: passed.** Four of five statements (Theorem 1.1, Corollary 1.2's
completeness gap, Lemma 4.1, Proposition 3.1) match the source exactly or
as closely as the source itself permits. The fifth, Section 4.3's
`k`-formula, is a **partial match**: the held numeric value (`k = Li(m)/2`)
is asymptotically consistent with the source's own formula
(`lambda_triv ~ pi(m)/e ~ m/(e log m)`) for **every cell this run's grid
actually evaluates**, because this run's own `|D| = 4q` convention (every
`q` in the grid is `>= 2^64`) always satisfies the source's own stated
condition (`|disc(O)| > 4`) for the unit-count constant `e` to equal 2 --
but the held transcription's stated *mechanism* for the `/2` ("a split
prime contributes one generator") is the opposite of what the source
actually says (a split prime contributes **two** ideals of norm `p`; the
`/2` comes from dividing by `e`), and `e` itself is absent from
`source_statements.md` and `constants_table.csv`. **This is numerically
inert for every cell in this run's own grid and does not change any
already-computed value in `crossover.csv`** (verdict_scope). It is a
transcription/reconciliation inaccuracy on this program's own side, not a
source-side error, and is handled by a separate correction record,
`CORR-20260907-b7e0f3` (see below) -- `source_statements.md`,
`cost_model.md`, and `constants_table.csv` are NOT edited by this addendum
or by that correction; they remain immutable as committed.

### Sign of log(k/c) at q = 2^256, PRIMARY convention (k = Li(m)/2), both logarithm conventions, full C-sweep

Read directly from `crossover.csv` rows `bits=256, delta in {0.25, 0.5,
1.0, 2.0}, log_convention in {bits, natural}, C in {0.5, 1, 2, 4, 8}`
(20 rows total for `delta` fixed at each value; 5 rows per
`(delta, log_convention)` pair):

- **delta = 0.25**: `sign_log_kc_half_PRIMARY = negative` at every one of
  the 5 swept `C` values, under BOTH `bits` and `natural` log conventions
  (10/10 cells negative, zero flips of either kind anywhere in this slice).
  **Robust vacuity.**
- **delta = 0.5**: identical pattern -- `negative` at every swept `C`,
  both log conventions, zero flips. **Robust vacuity.**
- **delta = 1.0**: NOT a clean directional result at low `C`.
  - `C = 0.5`: `bits` gives `positive` (`degree_convention_flip=False,
    log_convention_flip_bits_vs_natural=True`); `natural` gives `negative`
    (`degree_convention_flip=True, log_convention_flip=True`). This cell
    flips between the two logarithm conventions -- per condition
    E2-CONVENTION this is CONVENTION-DEPENDENT and is NOT a directional
    result in either direction.
  - `C = 1.0`: `bits` gives `sign_half=negative, sign_full=positive,
    degree_convention_flip=True` -- a degree-convention flip, also
    CONVENTION-DEPENDENT. `natural` gives `sign_half=negative,
    sign_full=negative`, no flip -- a clean negative under `natural` alone.
  - `C in {2.0, 4.0, 8.0}`: `negative` under both conventions, no flips.
    Clean vacuity at these three `C` values.
- **delta = 2.0**: robust and non-vacuous for most of the sweep.
  - `C in {0.5, 1.0, 2.0, 4.0}`: `sign_half = positive` AND
    `sign_full = positive` (no degree flip) under BOTH `bits` and `natural`
    (no log flip). **Fully convention-robust non-vacuous result** (8/8
    cells agree in sign across both axes of convention).
  - `C = 8.0`: `sign_half = negative` under BOTH `bits` and `natural`
    (no log-convention flip), but `sign_full = positive` in both -- a pure
    **degree-convention flip**. Per E2-CONVENTION this specific cell is
    CONVENTION-DEPENDENT and is not reported as a directional `negative`
    result under the PRIMARY convention alone, even though the two
    logarithm conventions themselves agree with each other here.

### Non-vacuity of the proven separation at q = 2^256 (evaluation of the model, not a measurement on any curve)

Under this run's stated PRIMARY convention, restricted to cells that are
**convention-robust** (agree under both logarithm conventions AND both
degree conventions, per E2-CONVENTION's requirement that a flipping
conclusion is reported as convention-dependent, not as a result):

- **Robustly VACUOUS** (`log(k/c) <= 0`) at `delta in {0.25, 0.5}` across
  the entire swept `C in {0.5, ..., 8}` range, and at `delta = 1.0` for
  `C in {2, 4, 8}`.
- **Robustly NON-VACUOUS** (`log(k/c) > 0`) only at `delta = 2.0`, and
  only for `C in {0.5, 1, 2, 4}` (4 of the 5 swept values of the unpinned
  Lemma 4.1 constant). At `delta = 2.0, C = 8.0` the result is
  convention-dependent (degree-convention flip) and not counted as a
  directional finding either way.
- `delta = 1.0` at `C in {0.5, 1.0}` yields no convention-robust
  conclusion in either direction and is reported as CONVENTION-DEPENDENT.

Per specification.yaml's own `claim_boundary`: at every `(q=2^256, delta,
C)` cell found vacuous above, the only correct statement is that
Corollary 1.2's concrete walk-length guarantee is **asymptotically sound
but concretely UNPROVEN at this deployed field size**, under the branch-(a)
proven bound and the cited/swept constants -- never that Corollary 1.2 is
false, and never that the JMV reduction fails in practice. This is an
evaluation of the stated cost model's arithmetic at `q = 2^256`, nothing
about ECDLP hardness, attack cost, or GRH's truth (CTRL-GRH, C2).

### Smallest delta for which log(k/c) > 0 at q = 2^256

The smallest grid `delta` value producing a **convention-robust** positive
sign at `bits = 256` is `delta = 2.0` -- the LARGEST value in this run's
swept grid `{0.25, 0.5, 1.0, 2.0}` -- and even then only for `C <= 4`. The
individual-convention entries in section 3's own already-computed table
(`smallest_delta_with_positive_sign_at_bits_256`, reproduced there per
`(log_convention, C)`) show a `bits`-only positive at `delta = 1.0, C=0.5`,
but that specific cell fails the E2-CONVENTION robustness requirement
(natural log gives `negative` there) and is therefore excluded: it is
CONVENTION-DEPENDENT, not a finding. At `C = 8.0` no grid `delta` value
produces a positive sign under either convention ("none in grid", per
section 3's own table). Both readings satisfy the induced-`m`/typical-`l`
reporting requirement of specification.yaml's own primary metric: at
`delta=2.0, bits=256`, `m = 4294967296.0 ~= 2^32` (`bits` convention) or
`m = 991429199.18... ~= 2^30` (`natural` convention), with typical
`l ~ Theta(m)` in each case (`crossover.csv`, same rows cited above).

### Crossover bit size (modelled reduction overhead = sqrt(n))

Since `r_half`/total cost is defined only where `sign_half` is positive
(`cost_model.md` section 6), a PRIMARY-convention crossover can only occur
inside the `delta = 2.0` region identified above. Verified directly against
`crossover.csv` at `delta = 2.0, C = 1.0, log_convention = bits`, PRIMARY
per-step variant (`phi_l O(l^3)`, typical `l ~ Theta(m)`):

| bits | cost_over_rho (phi_l, typical l) | cheaper_than_rho |
|---|---|---|
| 160 | 4152.618... | False |
| 192 | 0.6103178... | True |
| 224 | 0.0000637392... | True |

The crossover bit size for this `(log_convention=bits, C=1.0, phi_l
typical-l)` slice is **192** -- the smallest grid `bits` value where
`sign_half=positive` AND `cost < rho` -- reproducing analysis.md section
5's own already-computed table now stated as a conclusion. Section 5's
table shows the identical crossover bit size (192) reported for the
`natural` log convention at the same `(delta=2.0, C=1.0)` slice. Below 192
bits (within the `delta=2.0` regime that is itself needed for
non-vacuity), the modelled PRIMARY reduction cost EXCEEDS `rho`
(sqrt(n)); at and above 192 bits it falls BELOW `rho`. **No crossover
exists anywhere in the grid for `delta in {0.25, 0.5, 1.0}` at `C=1.0`**,
because `sign_half` never reaches positive there at any grid `bits` value,
so total cost is `NA_ratio_not_positive` throughout (matching section 5's
own "no crossover within grid" statement, now given as a conclusion rather
than a bare fact).

For the OPTIMISTIC/CAVEATED per-step-cost variants (`velu O(l)`,
`sqrt_velu O(sqrt l)`, and `phi_l` best-case `l=2`) -- which
`constants_table.csv`'s own applicability caveat states are not
realistically available for a uniformly random split prime (which
generically lacks cheap rational `l`-torsion) -- the modelled cost is
**already** below `rho` at `bits=160`, the smallest grid bit size where
`sign_half` first turns positive for `delta=2.0, C=1.0`: `cost_over_rho`
values there range from `~1.18e-22` (`phi_l` best-case `l=2`) to
`~9.67e-15` (`velu`, typical `l`) to `~2.95e-23` (`sqrt_velu`, typical
`l`), all `cheaper_than_rho=True`. Their crossover, within this slice,
therefore occurs no later than 160 bits -- but per the applicability
caveat this cheaper figure must NOT be read as the load-bearing one; the
`phi_l`/typical-`l` crossover at 192 bits is the applicable figure per
specification.yaml's own method item 4.

### Falsification criterion (specification.yaml)

NOT satisfied: specification.yaml's falsification_criterion requires
`log(k/c) > 0` at EVERY tested `(q >= 2^128, delta >= 0.25)` cell under
both logarithm conventions, which fails immediately at, e.g.,
`bits=256, delta=0.25` (negative under both conventions, every swept `C`).
The paper's practical reading is therefore NOT vindicated under this
stated model at this grid, and this research line does not close via the
falsification route.

### H-JMV-002's own three quantitative predictions, checked against this grid

1. *"at least one (q >= 2^128, delta <= 1) cell has log(k/c) <= 0 under
   BOTH logarithm conventions"* -- **SATISFIED**, e.g. `bits=256,
   delta=0.25, C=1.0`: `negative` under both `bits` and `natural` (many
   other cells also satisfy this).
2. *"ratio of overhead/sqrt(n) >= 1 at some tested q >= 128 bits"* --
   **SATISFIED**: `bits=160, delta=2.0, C=1.0, bits, phi_l typical-l`:
   `cost_over_rho = 4152.618...`, and this cell has no degree- or
   log-convention flip.
3. *"delta required for log(k/c) > 0 at q=2^256 strictly greater than the
   smallest tested delta (0.25)"* -- **SATISFIED**: the smallest
   convention-robust delta is 2.0 (the grid's largest value); even the
   individual-convention entries are all `>= 1.0`.

All three predictions are borne out by this grid, strictly scoped to:
branch-(a)'s proven, GRH-conditional bound; the stated cost model
(Proposition 3.1 walk length x `phi_l O(l^3)` per-step cost, typical
`l ~ Theta(m)`, as the load-bearing variant); the swept
`C in {0.5,...,8}` and `delta in {0.25,...,2.0}` grid; both logarithm
conventions; zero curve instances at any size (`claim_tier:
not_applicable`, permanently). Nothing above asserts, or is to be read as
asserting, anything about ECDLP hardness, attack cost, real-world attack
feasibility, or GRH's truth.

**C1 STATUS: PASSED (VAL-20260907-b0832b). This addendum is the conclusion
specification.yaml's stopping_rules reserved for after that review.**
