# report_route_i2.md — ROUTE-I2: genuinely independent second route for `lam1n`/`hkz`

    task            TASK-20260813-415c21
    goal / batch    GOAL-MLKEM-005 / BATCH-7033ee
    role            executor
    policy          executor-implementation, independent_session_required: true
                    (see run_manifest.yaml for the model that actually answered
                    and whether that policy was honoured without fallback)
    claim tier      TOY — toy-scale (d <= 40) lattice measurement throughout.
                    Never crypto-scale ML-KEM evidence. No claim above TOY is
                    made anywhere in this report.
    certificate     kind: none — no discrete-log solve, no factor-base
                    relation is claimed or produced. The logdet-invariance
                    self-check and the per-index violation diagnostic below
                    are INSTRUMENT CHECKS on this script's own reduction,
                    never certificates in the sense of `docs/claims-and-verification.md`.

Governed by `coordination/goals/GOAL-MLKEM-005/batches/BATCH-7033ee/tasks/TASK-20260813-61dab8/prereg.md`
(PREREG-4, sha256 `b781b8c1aef9463642a1740bac4093bf22fcae0fe75a3389b5be7a4c826d4f7e`,
notarized at commit `e40098f4f9c41be88a7e1c4970e39444247a4c53`, verified
`is_ancestor_of_HEAD: true` at run time). PREREG-4 is frozen; no success
criterion, threshold, or termination clause was altered after seeing an
outcome.

---

## R-B-OUT-0 — RC-3 carried verbatim (PREREG-4 §1)

The following text is **quoted, not recomputed**, attributed to PREREG-4
section 1. No cell's `D_route` was recomputed and `measure_c3lane.py` was
not re-run.

> BATCH-fbb639's R-C-OUT-0 coverage table is corrected at four hkz
> cells, per the Red Team's probe_coverage_beta_mismatch_output.json
> (TASK-20260813-6ab893), read directly and carried without recomputation:
>
> 1. hkz/L9_b15 and hkz/L11_b20 are restated as genuinely
>    UNCOVERED, not COVERED. Beta 15 (L9) and beta 20 (L11) are the
>    *middle* beta of each lattice's three-point grid and are not
>    REL1-pair endpoints in results_am4.json -- am4_has_a_genuine_value_
>    at_this_beta: false for both, confirmed against that file's own
>    declared beta_lo/beta_hi fields (L9: lo=7, hi=22; L11: lo=10,
>    hi=30). The value measure_c3lane.py read and reported as this cell's
>    ROUTE-I comparison was in fact the beta_lo comparison of a
>    different beta, silently substituted with no genuine second-route
>    value existing for the cited beta.
> 2. hkz/L9_b22 and hkz/L11_b30 are restated with the corrected TRUE
>    beta_hi-based D_route source. Both cells *are* genuine REL1-pair
>    endpoints (beta_hi), but measure_c3lane.py's check reads only
>    am4_row['X_lo'] unconditionally, so the reported D_route for these
>    two beta_hi cells was in fact computed against the wrong endpoint
>    of the pair (the beta_lo value, not the beta_hi value the cell
>    itself is at). The corrected, genuinely-beta_hi-sourced comparison is:
>
>    | cell | am4 X_hi | relvar X (basis 0) | true D_route |
>    |---|---|---|---|
>    | hkz/L9_b22  | -0.11249180258058367 | -0.11249180258058367 | 0.0 |
>    | hkz/L11_b30 | -0.13095122117764646 | -0.13095122117764646 | 0.0 |
>
>    D_route is numerically unchanged at exactly 0.0 for both cells
>    under the corrected source -- this is a provenance-labelling
>    correction (which stored value was cited as the cell's comparison), not
>    a correction that changes any reported number or verdict.
>
> Corrected coverage fraction. lam1n's 9 cells are unaffected by this
> correction (all remain COVERED at 9/9, per the beta-independence
> argument above). hkz's corrected coverage is 7 of 9 cells (L7 b5/b10/
> b15; L9 b7, b22; L11 b10, b30), with hkz/L9_b15 and hkz/L11_b20
> restated UNCOVERED. The corrected total across lam1n + hkz is 16 of
> 18, not 18 of 18 as BATCH-fbb639 reported (rawtail's coverage --
> ROUTE-W only, never counted -- is untouched by this correction).
>
> This supersedes BATCH-fbb639's R-C-OUT-0 coverage table at exactly
> these four cells and its "18 of 27" coverage-fraction statement wherever
> quoted without this correction in the same sentence. It does not change
> results_c3lane.json's D_route value at any cell, and it does not
> change the fired termination branch.
>
> EFFECT ON THE FIRED TERMINATION BRANCH -- STATED, NOT RE-ARGUED. Per the
> Red Team's own probe output, T-C3LANE-OPEN-PARTIAL still fires after this
> correction: 16 genuinely-covered cells (all 9 lam1n cells plus hkz's 7
> genuinely-covered cells) still show EXCEEDS, SOME-EXCEEDS still holds
> over the corrected COVERED set, and the -PARTIAL suffix was already
> applicable at 18/27 and remains applicable at the corrected, smaller
> coverage count. This correction narrows and corrects the coverage table;
> it does not overturn the branch, and this document does not re-litigate
> that conclusion -- it is carried here as background so RC-3's scope is
> clear, and restated as committed, citable text by this batch's ledger
> archive exactly as PREREG-3 3.7 required for RC-1/RC-2.
>
> NO RE-RUN IS REQUIRED, AND NONE IS PERMITTED HERE. measure_c3lane.py,
> results_c3lane.json and report_c3lane.md are immutable committed
> artifacts (TASK-20260813-7b3039, archived at TASK-20260813-7ac7cd) and
> are not edited, not re-run, and not vendored. The lead producer of this
> batch carries the frozen text above into its own report by quotation,
> attributed to PREREG-4 section 1, and does not recompute anything for RC-3.

This carry does not change any `D_route_independent` value or verdict
reported below; it is background establishing RC-3's scope, exactly as
PREREG-4 §1 requires.

---

## Obligation 0 — `ROUTE-P` coverage verification (R-B-OUT-1)

Read directly from
`coordination/goals/GOAL-MLKEM-005/batches/BATCH-9e3584/tasks/TASK-20260809-cda2f6/results_relvar.json`
(sha256 `c5b2918dccf1b58261eed1e9d221f1074ae6143f2a8fc5c0f42ff475646ccd6d`),
its `G_REL2` block, path pattern
`G_REL2.<cand>.<pair>.<beta>.per_basis[i].X_a`.

| check | result |
|---|---|
| cells expected (2 candidates x 3 lattices x 3 betas) | 18 |
| cells with confirmed full 8-basis `ROUTE-P` coverage | 18 |
| gaps found | 0 |

**Path-label discrepancy, disclosed rather than silently worked around:**
PREREG-4 §2.1 states the fibre-dispersion path as
`results_relvar.json.per_candidate.<X>.per_cell.<L>_<b>.float_sd`, but the
committed file has no top-level `per_candidate` key — the real key is
nested under `G_VAR.per_candidate.<X>.per_cell.<L>_<b>.float_sd`. This was
verified by direct read of the file (PREREG-4 §2.3's instruction to verify
rather than trust the prose) and is a path-label discrepancy in the
pre-registration's prose, not a data gap: the `s_c^fib` values themselves
are present and were used as reported below.

**Conclusion: `ROUTE-P` fully covers all 18 cells with no gap.** Obligation
0 is satisfied before `ROUTE-I2` was built, per the task card's ordering.

---

## Independence self-certification (PREREG-4 §2.2)

**Grep of the delivered script for the literal forbidden-import strings**,
run as the completion gate requires:

```
$ grep -n "measure_am4\|measure_relvar\|replicate_l7l8\|fpylll\|import sage\|import flint" measure_route_i2.py
32:  build_basis, hkz_profile or gram_int from measure_am4.py / measure_relvar.py
33:  / replicate_l7l8.py, and does NOT import fpylll AT ALL -- this environment
34:  has no fpylll, sage or flint installed at dispatch time (declared gap G-5),
43:  from measure_relvar.py's fpylll-default ~0.99) followed by a progressive,
93:# levels, exactly the resolution measure_relvar.py's own comment records
137:LLL_DELTA = 0.999          # PREREG-4 2.2(2): a DIFFERENT delta from fpylll's
320:    recurrence above -- no fpylll IntegerMatrix/GSO.Mat/LLL.Reduction call
347:    a plain generator (no fpylll Enumeration object anywhere)."""
365:    Genuinely different code path from fpylll's Enumeration class: no
514:    fpylll. Every accepted insertion is verified against the exact logdet
612:    hkz_profile's hkz_violation (which used fpylll's Enumeration class and a
702:    fpylll_present = False
704:        import fpylll  # noqa: F401
705:        fpylll_present = True
707:        fpylll_present = False
714:        "fpylll_present_but_NOT_imported_by_this_script": fpylll_present,
716:        "declared_gap_G5": ("this environment has no fpylll, sage or flint "
```

Every occurrence is either a **comment/docstring naming what is deliberately
avoided**, or the **single presence-check `try: import fpylll` at line 704**
inside a `try/except`, used only to record `fpylll_present_but_NOT_imported_
by_this_script` in the environment block below — `fpylll` is never called,
never used for GSO/LLL/BKZ/Enumeration, and the check's own result is
`False` on this host (no `fpylll` is installed at dispatch time, declared
gap `G-5`). There is **no** `from measure_am4 import ...`, **no**
`from measure_relvar import ...`, **no** `from replicate_l7l8 import ...`,
**no** `exec()` of any of those files' source, and no copy-pasted
`make_A`/`build_basis`/`hkz_profile`/`gram_int` body anywhere in
`measure_route_i2.py`.

1. **Basis construction** re-implements PREREG-4 §2.1's mathematical
   specification directly: `numpy.random.default_rng([1, d, k, i]).integers(
   0, q, size=(k, d-k), dtype=np.int64)` for `A_i`, then the block matrix
   `[[I_k, A_i], [0, q*I_{d-k}]]` assembled with `numpy` integer array ops,
   written fresh in this script rather than imported from `make_A`/
   `build_basis`. Per PREREG-4 §2.1, producing a bit-identical `B_i` this
   way is expected and is **not** itself evidence of code-sharing.
2. **Reduction/enumeration is a from-scratch pipeline with no `fpylll`
   dependency at all** — this environment has no `fpylll`, `sage`, or
   `flint` installed at dispatch time (declared gap `G-5`, confirmed by the
   presence check above), so a from-scratch implementation, explicitly
   licensed as sufficient at `d <= 40` by the goal record's `next_action`
   and by PREREG-4 §2.2(1), was written: a hand-rolled Gram-Schmidt/LLL
   routine, a recursive Schnorr-Euchner-style DFS enumerator with its own
   zig-zag ordering and node cap, and a fixed-pivot size-reduction insertion
   step — none of which is `fpylll`'s `IntegerMatrix`/`GSO`/`LLL.Reduction`/
   `BKZReduction`/`Enumeration` call sequence.

### The named genuine algorithmic difference (PREREG-4 §2.2(2))

`hkz_profile`'s pipeline (`measure_relvar.py`, carried from
`measure_am4.py`) runs **one `fpylll` `BKZReduction` pass at
`block_size = d`** (full-dimension BKZ, `max_loops = 1`), then explicit
per-index HKZ sweeps using `fpylll`'s `Enumeration` class for exact SVP at
each projected sublattice index.

`ROUTE-I2`'s pipeline (`measure_route_i2.py`, this script) differs in **at
least three independent, explicitly named ways**:

1. **A different LLL delta.** `LLL_DELTA = 0.999` is used for this script's
   own from-scratch LLL routine (`lll_reduce_inplace`), explicitly chosen to
   differ from `fpylll`'s own default (`~0.99`, noted in this script's
   comments at the point of the constant's definition). `hkz_profile` never
   sets an explicit LLL delta at all — it runs `BKZReduction` directly at
   `block_size = d`, so there is no comparable "LLL step" in its own
   pipeline to match deltas against.
2. **A progressive, capped block-enumeration schedule instead of one
   full-dimension BKZ pass.** `ROUTE-I2` sweeps increasing local-block
   widths (`BLOCK_SCHEDULE_CAP = {"L7": 20, "L9": 30, "L11": 28}`, i.e. up
   to full width at L7/L9 and a capped width below `d` at L11) with a
   bounded-node recursive DFS enumerator (`ENUM_NODE_CAP = 200_000` nodes)
   at each block position, repeated across multiple outer sweeps until
   convergence or the time/node caps bind — a genuinely different loop
   structure from `hkz_profile`'s single `max_loops = 1` full-width
   `BKZReduction` call followed by separate exact-enumeration HKZ sweeps.
3. **No `fpylll` dependency of any kind** (point 2 above) — not merely a
   different call sequence within the same library, but no `fpylll` import
   at all, satisfying PREREG-4 §2.2(1)'s stronger alternative ("a different
   reduction library... or a from-scratch LLL + local-block enumeration
   routine").

Any one of these three differences is independently sufficient to
discharge PREREG-4 §2.2(2)'s naming requirement; all three are disclosed so
a reviewer can judge the independence claim on its strongest and weakest
points alike.

**Dependency/provenance disclosure (PREREG-4 §2.2(6)):** the only
third-party dependency imported and used for numerics is `numpy 2.4.4`
(array storage, integer RNG via `numpy.random.default_rng`, and
floating-point linear algebra for Gram-Schmidt coefficients). No reduction
library (`fpylll` or otherwise) is imported for use. `fpylll`, `sage`, and
`flint` are confirmed absent from this host at dispatch time (`environment`
block of `results_route_i2.json`: `fpylll_present_but_NOT_imported_by_this_
script: false`, `sage_present: false`, `flint_present: false`).

**HKZ violation/optimality diagnostic (PREREG-4 §2.2(4)):** every basis, at
every lattice, gets its own `violation_diag` (`max_violation` over checked
indices, seconds spent, `block_width_cap`, whether the full width was
checked, and how many indices were time-skipped) plus a full
`violation_per_index` array. This diagnostic differs in kind from
`hkz_profile`'s own `hkz_violation` (which used `fpylll`'s `Enumeration`
class and a 1e-6 slack) — `ROUTE-I2`'s diagnostic instead re-runs its own
bounded-node DFS enumerator at each GSO index (independent of the pipeline
that produced the basis) and reports the largest fractional shortfall
against the enumerator's own found minimum, capped by `DIAG_MAX_BLOCK`
at L11 (25) for tractability. It is reported even though it differs in
kind, exactly as PREREG-4 §2.2(4) requires.

**No reduction above `d = 40` (PREREG-4 §2.2(5)):** confirmed by inspection
— only `L7` (d=20), `L9` (d=30), `L11` (d=40) appear anywhere in
`measure_route_i2.py`; no `L1`, `L2`, `L4`, `L5`, `L8`, `L10`, `L12`.

---

## Obligation 1 — per-cell comparison (R-B-OUT-2)

All 18 cells (`lam1n` x {L7,L9,L11} x 3 betas each, `hkz` x {L7,L9,L11} x 3
betas each) were computed at all 8 fibre bases and reached `COVERED2`. No
cell is `UNCOVERED2`.

| cell | D_route_independent | s_c^fib | verdict |
|---|---|---|---|
| lam1n/L7_b5   | 1.110223e-15 | 4.339250e-02 | EXCEEDS |
| lam1n/L7_b10  | 1.110223e-15 | 4.339250e-02 | EXCEEDS |
| lam1n/L7_b15  | 1.110223e-15 | 4.339250e-02 | EXCEEDS |
| lam1n/L9_b7   | 2.664535e-15 | 8.475924e-02 | EXCEEDS |
| lam1n/L9_b15  | 2.664535e-15 | 8.475924e-02 | EXCEEDS |
| lam1n/L9_b22  | 2.664535e-15 | 8.475924e-02 | EXCEEDS |
| lam1n/L11_b10 | 4.559733e-02 | 3.884739e-02 | DOES NOT EXCEED |
| lam1n/L11_b20 | 4.559733e-02 | 3.884739e-02 | DOES NOT EXCEED |
| lam1n/L11_b30 | 4.559733e-02 | 3.884739e-02 | DOES NOT EXCEED |
| hkz/L7_b5     | 8.881784e-16 | 2.388797e-02 | EXCEEDS |
| hkz/L7_b10    | 8.881784e-16 | 1.063929e-02 | EXCEEDS |
| hkz/L7_b15    | 8.881784e-16 | 8.879737e-03 | EXCEEDS |
| hkz/L9_b7     | 8.881784e-16 | 1.288801e-02 | EXCEEDS |
| hkz/L9_b15    | 1.776357e-15 | 6.915568e-03 | EXCEEDS |
| hkz/L9_b22    | 1.776357e-15 | 3.892658e-03 | EXCEEDS |
| hkz/L11_b10   | 4.949460e-02 | 1.010944e-02 | DOES NOT EXCEED |
| hkz/L11_b20   | 4.266958e-01 | 7.206939e-03 | DOES NOT EXCEED |
| hkz/L11_b30   | 2.954816e-01 | 3.818307e-03 | DOES NOT EXCEED |

(`lam1n` is beta-independent per PREREG-4 §2.1, so its three betas per
lattice share one identical `D_route_independent`/`s_c^fib` pair, exactly
as expected of the observable's own definition — not a computation bug.)

**Observation, recorded as it stands, without editorializing further than
PREREG-4 licenses:** at `L7` (d=20) and `L9` (d=30), `D_route_independent`
sits at or near binary64 machine epsilon (`~1e-15` to `~1e-16`), four to
five orders of magnitude below the smallest `s_c^fib` reported anywhere in
scope. At `L11` (d=40), `D_route_independent` is between `4.6e-2` and
`4.3e-1` — comparable to, or larger than, `s_c^fib` itself at every L11
cell. Per-basis diagnostics for L11 (below) show incomplete HKZ convergence
within budget at this dimension, which is the most likely proximate cause
of this gap; PREREG-4's own frozen clause (§2.6) reads this as
`T-INDEP-UNDERMINES` at these specific cells regardless of cause, and this
report does not substitute a different threshold or explanation for that
frozen reading.

### Per-basis reduction diagnostics (summary; full per-index detail in `results_route_i2.json`)

| lattice | basis i | reduce time (s) | sweeps | converged | `max_violation` | `logdet_drift_from_lll` |
|---|---|---|---|---|---|---|
| L7  | 0 | 1.57 | 4 | True | 0 | 0.00e+00 |
| L7  | 1 | 1.42 | 3 | True | 0 | 0.00e+00 |
| L7  | 2 | 1.79 | 6 | True | 0 | 1.42e-14 |
| L7  | 3 | 1.32 | 3 | True | 0 | 0.00e+00 |
| L7  | 4 | 1.58 | 4 | True | 0 | 0.00e+00 |
| L7  | 5 | 1.52 | 6 | True | 0 | 0.00e+00 |
| L7  | 6 | 1.72 | 7 | True | 0 | -1.42e-14 |
| L7  | 7 | 1.44 | 4 | True | 0 | -1.42e-14 |
| L9  | 0 | 22.98 | 7 | True | 0 | 0.00e+00 |
| L9  | 1 | 20.10 | 9 | True | 0 | -2.84e-14 |
| L9  | 2 | 18.95 | 5 | True | 0 | 0.00e+00 |
| L9  | 3 | 24.51 | 9 | True | 0 | 2.84e-14 |
| L9  | 4 | 26.39 | 8 | True | 0 | 0.00e+00 |
| L9  | 5 | 22.75 | 7 | True | 0 | 2.84e-14 |
| L9  | 6 | 19.19 | 5 | True | 0 | -2.84e-14 |
| L9  | 7 | 16.98 | 5 | True | 0 | -2.84e-14 |
| L11 | 0 | 267.12 | 10 | True | 0.9780 | 1.99e-04 |
| L11 | 1 | 340.09 | 7 | **False** (time-capped) | 1.0000 | 1.61e-04 |
| L11 | 2 | 340.07 | 13 | **False** (time-capped) | 0.9950 | 2.27e-04 |
| L11 | 3 | 251.61 | 9 | True | 0.9988 | 8.98e-05 |
| L11 | 4 | 205.96 | 13 | True | 0.9726 | 9.40e-05 |
| L11 | 5 | 340.32 | 6 | **False** (time-capped) | 1.0000 | 2.22e-04 |
| L11 | 6 | 340.34 | 11 | **False** (time-capped) | 1.0000 | 1.32e-04 |
| L11 | 7 | 150.53 | 6 | True | 0.8988 | 7.82e-05 |

**Disclosed limitation, stated plainly rather than smoothed over:** at
`d = 40` (L11), `max_violation` (this script's own per-index HKZ
optimality diagnostic, capped at `DIAG_MAX_BLOCK = 25` for tractability at
that dimension) stays large (0.90 to 1.00 — i.e. some projected-sublattice
index is found up to ~2x longer than the enumerator's own reported
minimum) even where the reduction loop reports `converged: True` (a sweep
completed with no further accepted insertion within the per-attempt caps,
which is a **local-convergence** signal, not a claim of true HKZ
optimality). Several L11 bases additionally hit the 340-second per-basis
reduce time cap without their outer-sweep loop itself converging
(`converged: False`). Both are budget/tractability limits of this
from-scratch implementation at `d = 40` within the task's 7200-second
global cap, honestly reported per PREREG-4 §2.2(4), never smoothed over or
treated as evidence for or against the underlying observables. Every
accepted basis transformation was nonetheless verified against the
log-determinant invariant (a unimodular change of basis must preserve
`logdet`) before being committed; insertions that violated this invariant
beyond a `1e-6`-relative tolerance were rejected rather than applied
(`logdet_invariant_breaks` counters, e.g. 1305 rejected insertions for
L11 basis 0), so the reported `r_j` profile is always a genuine basis of
the same lattice, even when short of full HKZ convergence.

---

## Obligation 2 — aggregate comparison and summary statistics (R-B-OUT-3)

| aggregate | value |
|---|---|
| COVERED2 | 18 / 18 |
| UNCOVERED2 | 0 |
| n_EXCEEDS | 12 |
| n_DOES_NOT_EXCEED | 6 |
| D_route_independent (max over COVERED2) | 0.42669575965725226 |
| D_route_independent (median over COVERED2) | 2.220446049250313e-15 |
| s_c^fib (max over covered cells) | 0.0847592417001852 |
| s_c^fib (median over covered cells) | 0.03136768036779794 |
| smallest s_c^fib anywhere in scope | 0.003818306775026579 |

**Direct per-cell comparison against `PREREG-3`'s own `D_route` (`0.0` at
every genuinely-covered `PREREG-3` cell, per RC-3 above):** the 12
`EXCEEDS` cells above show `D_route_independent` at or near machine epsilon
— `same_order_near_machine_epsilon: true` for every one of them — matching
`PREREG-3`'s already-archived `D_route = 0.0` figures at the same scale.
The 6 `DOES NOT EXCEED` cells (all `L11`, both `lam1n` and `hkz`, all three
betas each) show `D_route_independent` one to two orders of magnitude
**larger** than `PREREG-3`'s `D_route`, and larger than `s_c^fib` itself at
every one of those six cells — `same_order_near_machine_epsilon: false`.
Two of the six (`hkz/L9_b15`, which is genuinely `hkz/L11_b20` in this
column per RC-3's restated coverage — see note below) and `hkz/L11_b20`
have no genuine `PREREG-3` `D_route` to compare against at all, since RC-3
restates them `UNCOVERED` under `PREREG-3`; this is recorded as
`prereg3_D_route: null` with an explicit note in `results_route_i2.json`,
never defaulted to `0.0`.

---

## Termination branch (R-B-OUT-4, PREREG-4 §2.6)

**`T-INDEP-UNDERMINES`** fires (no `-PARTIAL` suffix, since `|COVERED2| =
18 = 18`, full coverage).

> Quoted clause fired, PREREG-4 §2.6: *"a single cell firing UNDERMINES's
> condition is sufficient to fire T-INDEP-UNDERMINES and prevents
> T-INDEP-CONFIRMS from being read over the whole COVERED2 set."*

The condition that fired at each of the six flagged cells is the **scale**
condition (`D_route_independent >= 0.1 * s_c^fib`), independently
sufficient per §2.6; the alternative sufficient condition (verdict flip
from `EXCEEDS` to `DOES NOT EXCEED` relative to `PREREG-3`'s reported
verdict) is also true at every one of these six cells, since `PREREG-3`
reported `EXCEEDS` at all of them (per RC-3, where a genuine comparator
exists) and `ROUTE-I2` reports `DOES NOT EXCEED`.

**What this means, stated at exactly the scope PREREG-4 §2.6 licenses, no
further:** at these six specific `L11` (d=40) cells, the disagreement
between `ROUTE-P` and this genuinely independent `ROUTE-I2` implementation
is itself comparable in scale to (or larger than) `lam1n`/`hkz`'s own
measured fibre dispersion, so `BATCH-fbb639`'s `EXCEEDS` verdict at these
six cells was, at minimum, not distinguishable from a same-code-comparison
artifact once independent implementation error is accounted for. **This
does not extend to** `rawtail` (no `ROUTE-I2` was built for it); does not
extend to any cell outside these six; does not support or refute
`A-1`/ML-KEM/FIPS-203/attack-cost claims of any kind; and does not close,
pause, or complete `GOAL-MLKEM-005`. At the twelve `L7`/`L9` cells, the
independent-route disagreement stays at machine epsilon, matching
`PREREG-3`'s own figures — those twelve `EXCEEDS` verdicts are not disputed
by this measurement.

---

## Revisit list (R-B-OUT-5, PREREG-4 §2.7)

Six cells are flagged per the revisit condition carried verbatim from
`ledger/goals/GOAL-MLKEM-005.yaml`'s `next_action`: `D_route_independent`
grew toward `s_c^fib`'s scale under genuine independence, so each cell's
`EXCEEDS` verdict from `BATCH-fbb639` **must** be flagged as
methodologically unsupported in a superseding record, and no successor may
cite it without that flag. Per PREREG-4 §2.7, **this does not retroactively
change `T-C3LANE-OPEN-PARTIAL`**, which remains `BATCH-fbb639`'s own,
correctly-read, frozen-clause outcome.

| cell | D_route_independent | s_c^fib | fired condition |
|---|---|---|---|
| lam1n/L11_b10 | 0.04559732640744896 | 0.0388473945796316  | scale (D_route_independent >= 10% of s_c^fib) |
| lam1n/L11_b20 | 0.04559732640744896 | 0.0388473945796316  | scale (D_route_independent >= 10% of s_c^fib) |
| lam1n/L11_b30 | 0.04559732640744896 | 0.0388473945796316  | scale (D_route_independent >= 10% of s_c^fib) |
| hkz/L11_b10   | 0.04949460165186714 | 0.010109435646034129 | scale (D_route_independent >= 10% of s_c^fib) |
| hkz/L11_b20   | 0.42669575965725226 | 0.007206938942361495 | scale (D_route_independent >= 10% of s_c^fib) |
| hkz/L11_b30   | 0.29548163373524705 | 0.003818306775026579 | scale (D_route_independent >= 10% of s_c^fib) |

(Note: `results_route_i2.json`'s stored `fired_condition` string contains a
literal doubled `%%` from the script's own printf-style formatting
(`"scale (D_route_independent >= 10%% of s_c^fib)"`); reproduced verbatim
above as a single `%` for readability in this narrative report — this is a
cosmetic string-formatting artifact of the JSON emitter, not a change to
any reported number, and both files agree on every numeric value.)

---

## Infrastructure note (never read as a route disagreement)

No infrastructure gap blocked any cell: `fpylll`/`sage`/`flint` were
confirmed absent from this host at dispatch time (declared gap `G-5`), so a
from-scratch reduction pipeline was written and run entirely within the
7200-second global budget (total measured wall clock: 2444.61 s, well
inside budget; per-basis reduce time capped at 340 s and per-basis
diagnostic time capped separately, both of which bound individual step
cost, not global coverage). All 18 cells reached `COVERED2`; `T-INDEP-NODATA`
does not apply.

---

## Artifacts written by this task (all seven declared paths, no more, no fewer)

All paths below are repository-relative to
`coordination/goals/GOAL-MLKEM-005/batches/BATCH-7033ee/tasks/TASK-20260813-415c21/`:

1. `measure_route_i2.py` — the one re-executable script implementing `ROUTE-I2` from scratch.
2. `results_route_i2.json` — RC-3 carry (R-B-OUT-0), `ROUTE-P` verification (R-B-OUT-1), per-cell comparison (R-B-OUT-2), aggregate verdict (R-B-OUT-3), termination branch (R-B-OUT-4), revisit list (R-B-OUT-5).
3. `report_route_i2.md` — this document.
4. `command.txt` — the exact invocation used.
5. `stdout.log` — captured stdout of the run.
6. `stderr.log` — captured stderr of the run (empty: no warnings or errors were emitted).
7. `run_manifest.yaml` — schema-complete run manifest with input hashes, model/adapter binding, and certificate declaration.

No file outside this task's `write_scope` was written, edited, or staged.
Nothing was committed by this task; the Coordinator's archival task
(`TASK-20260813-5d1920`) is responsible for the snapshot commit.
