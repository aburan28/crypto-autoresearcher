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
