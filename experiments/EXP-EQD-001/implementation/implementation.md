# EXP-EQD-001 — implementation note

Authored at TASK-20260801-021 (GOAL-ECDLP-001 / BATCH-023) by the Executor.

Binding contract: `experiments/EXP-EQD-001/specification.yaml`, sha256
`295d85c748cf9d1d14e2746d3067fbbbc0a7fc9ebd8b62ccbdbe021a6dc99431`, hash-bound
at commit `7792331bca3f64db9ae296fbc1465bb3912998d4`. The driver re-hashes the
specification at run time and logs the comparison; the run of record logged
`match=True`.

Driver: `experiments/EXP-EQD-001/implementation/eqd001_driver.py`
sha256 `bdb2601b195f314a4430fa80fcf8ab15ec0b605335a8386a93c2b9b3c7d7b02f`
INT-2 function source sha256 `2577139d51b010bc2a8226803b5699ad4395044bcd0ae9eaf4f55c29d53d32d1`

**This note reports what was implemented and what was measured. It states no
disposition, freezes no threshold, and interprets nothing.** RUN-EQD-001-calib
is expressly NON-EVIDENTIAL about H-EQD-001, HEUR-DS-1 and H-SMTH-001 in either
direction.

## 1. Phase A — the driver is authored complete, including the dormant real arm

ATS-1 clause 5 requires the driver to be authored complete at this task,
including the real-arm entry point that is not executed here, so that
TASK-20260801-027 executes the identical file with no edit and the Validator can
re-check the hash. The file therefore contains, in one module:

- `int2_fibre_invariants` — the frozen INT-2 map, exactly the coefficient forms
  of `fibre_invariant_map.step_2_coefficients` and the invariants of
  `step_3_invariants`.
- `Cell` — one toy field cell: `p, a, b` from
  `harness.toycurve.generate_instance(2301, bits)`, the full affine point
  multiset of `E(F_p)`, the membership array for `X_E`, `#E(F_p)` and its 2-adic
  valuation.
- The object samplers: `draw_null_factor_base` (OBJ-NULL-RFB),
  `draw_independent_pairs` (OBJ-NULL-IND), `draw_uniform_pairs`
  (OBJ-NULL-UNIF2), `plant` (OBJ-PLANT-delta).
- The statistic family STAT-EQD-1: `stat_chi` (K in {16, 64}), `stat_ks1`,
  `stat_dup`. Forms only; the module contains no threshold constant.
- The controls: `ctrl_eqd_s3` (CTRL-EQD-S3), `support_fraction`, and the range
  and count assertions of CTRL-EQD-RANGE.
- `deterministic_factor_base` — **the real object**, called by `run_real_arm`
  and by nothing else.
- `run_calibration` — CAL-1..CAL-4, executed here.
- `run_real_arm` — DV-1..DV-7, CTRL-EQD-S3 and the integrity controls for
  RUN-EQD-001-real. **Present, reachable, and not invoked at this task.**

### How the calibration is structurally prevented from seeing the real data

ATS-1 clause 2 is enforced three ways, not by instruction:

1. `deterministic_factor_base()` is the only function that touches the frozen
   deterministic factor base, and it sets the module-level tripwire
   `_REAL_DATA_TOUCHED`. `run_calibration()` records the tripwire, and `main()`
   raises if it is true at the end of a calibration run. The run of record
   recorded `ats1_clause_2_real_data_touched: false` at both cells and in the
   run payload.
2. `--mode real` refuses to start unless `--approval-receipt` points at a JSON
   file whose `APPROVAL_DETERMINATION` is the literal string `APPROVED` **and**
   `--reading-rule` points at an existing frozen reading rule. Neither exists
   yet, so the real arm cannot be started today even by accident. This refusal
   was exercised in the pre-run smoke test and produced
   `status: failed_infrastructure`, `failure_class: specification_error`, with
   the tripwire still false.
3. The calibration run package contains no OBJ-REAL sample, no deterministic
   factor-base x-list and no statistic computed from one. The only x-list
   archived anywhere in the package is the representative **OBJ-NULL-RFB** draw
   per cell, which is a random null factor base drawn from the calibration null
   stream and is labelled as such in
   `results/calib/instrument_characterization.json`.

### How the real arm gets its numbers without a code edit

The calibrated thresholds, the certified delta, the certifying statistic and
the retained-statistic set do not exist yet and must never be edited into this
file. `run_real_arm` reads them at run time from
`experiments/EXP-EQD-001/reading_rule.yaml` via `load_reading_rule`, which
requires this shape (TASK-20260801-023 owns the file and its numbers; the shape
is stated here so that the freeze and the driver meet without an edit):

```yaml
reading_rule:
  retained_statistics: [STAT-CHI-16, STAT-CHI-64, STAT-KS1-E1, STAT-KS1-E2]
  thresholds:
    16: {STAT-CHI-16: <float>, STAT-CHI-64: <float>, STAT-KS1-E1: <float>, STAT-KS1-E2: <float>}
    20: {STAT-CHI-16: <float>, STAT-CHI-64: <float>, STAT-KS1-E1: <float>, STAT-KS1-E2: <float>}
  dup_band:
    16: [<lo>, <hi>]
    20: [<lo>, <hi>]
  certified_delta: <float>
  certifying_statistic: STAT-CHI-16 | STAT-CHI-64
```

The bit-size keys are integers. `retained_statistics` is the mechanism by which
a statistic excluded under CAL-STOP-1 `second_stop_leg` is dropped without
touching the driver: the real arm computes every statistic and applies the
reject test only to the retained ones. The driver records DV values and reject
booleans; **it selects no branch of RR-EQD-1 and states no disposition.**

## 2. Frozen forms, implemented exactly

| Contract item | Implementation |
| --- | --- |
| n per sample set | `N_PER_SAMPLE_SET = C(512, 2) = 130816`, from `np.triu_indices(512, k=1)`, strictly `i < j` |
| Resolution ladder | `RESOLUTION_LADDER_K = (16, 64)`. K = 256 is absent, per POW-EQD-1 |
| Binning rule | `(lift(e) * K) // p` on each coordinate |
| Delta ladder | `(0.005, 0.01, 0.02, 0.05, 0.10)` |
| M_PAIRS / R_REPS | 200 / 20 |
| Master seed | 2301; streams `2301 + {10000,20000,30000,40000} + bits`; the real-arm stream `2301 + 50000 + bits` is defined but not consumed |

Nothing was added, dropped, retuned or substituted.

### The diagonal is excluded by construction, not counted and then dropped

`upper_triangle_indices` enumerates `i < j` only, and the null and independent
samplers guarantee distinct x-coordinates, so `c_2 = (x_i - x_j)^2` is never
zero. `int2_fibre_invariants` counts `c_2 == 0` and returns the count *without
inverting*; every caller raises on a nonzero count. The measured
`degenerate_draw_count` is **0** at both cells over all 1242 sample sets of the
run of record (621 null-factor-base draws + 20 independent-pair draws per cell,
plus the uniform-pair draw which involves no curve arithmetic). The sample count
is declared at 130816 and every arm recorded exactly 130816 pairs.

### The one permitted redraw

`draw_null_factor_base` rejects and redraws on an x-collision to maintain 512
distinct x-coordinates, and counts the rejections. Measured totals over 621
draws per cell: **3484 at bits 16** (mean 5.6 per draw) and **206 at bits 20**
(mean 0.33 per draw). No other redraw exists anywhere in the driver.

## 3. Implementation readings that the frozen form did not fully determine

These are declared rather than left implicit. None of them is a choice among
alternatives that could move a decision; each is recorded so the Reviewer and
Validator can check it.

1. **STAT-DUP is the count of colliding index pairs.** "The count of exactly
   repeated (e_1, e_2) values within a single arm" is implemented as
   `sum_v C(multiplicity(v), 2)`. This is the reading the contract's own stated
   idealised expectation `n**2 / (2 * S)` identifies, since that is the birthday
   pair count. The alternative reading (`n` minus the number of distinct values)
   differs only when a value occurs three or more times.
2. **"Uniformly at random from E(F_p)" means uniform over the affine points.**
   A point is drawn uniformly from the multiset of affine points of `E(F_p)`,
   i.e. an x-coordinate carries weight 2 when it lifts to two points and weight
   1 when `y = 0`; the point at infinity has no x-coordinate and is excluded.
   OBJ-NULL-IND uses the same sampler.
3. **Plant replacement count** is `int(round(delta * 130816))`, giving 654,
   1308, 2616, 6541 and 13082 replaced pairs. It is recorded per replicate as
   `n_replaced`.
4. **Which stream supplies the CAL-2 base and comparison draws.** The plant
   stream supplies the replaced indices and the replacement `e_1` values, as the
   contract says. The OBJ-NULL-RFB draw that is planted, and the fresh
   independent OBJ-NULL-RFB draw it is compared against, both come from the
   calibration null stream, whose draw index advances monotonically across
   CAL-1, CAL-2, CAL-3 and CAL-4 in that fixed order (621 draws per cell). Every
   draw is therefore independent of every other and individually addressable.
5. **Stream hash definition.** Each draw index `k` yields
   `draw_seed = int(sha256("<seed>:<name>:<k>")[:16], 16)`, and the recorded
   `seed_sequence_sha256` is sha256 over the newline-joined
   `"<name>:<seed>:<k>:<draw_seed>"` records actually consumed, in consumption
   order. Any single replicate can be regenerated without replaying the others.
6. **CTRL-EQD-S3 is checked symmetrically rather than by root-finding.** Instead
   of solving the quadratic, the control verifies
   `e_1 == x(P+Q) + x(P-Q) (mod p)` and `e_2 == x(P+Q) * x(P-Q) (mod p)`, which
   is equivalent to root-multiset equality because `(e_1, e_2)` are the
   elementary symmetric functions of that multiset. The point arithmetic goes
   through `harness.toycurve.EllipticCurve` and does not reuse the coefficient
   formula.
7. **Square roots** use the `p ≡ 3 (mod 4)` fast path; both frozen primes
   (46663 and 767551) satisfy it. A slow sympy fallback exists for generality
   and was not taken.
8. **int64 vectorisation.** All arithmetic is exact: operands are reduced mod
   `p < 2^31`, so products stay below 2^62. `_assert_int64_safe` raises above
   that bound.

## 4. Declared additions and deviations

- **ADDITION (declared, non-decisional): CTRL-EQD-S3 was run inside the
  calibration**, on the representative OBJ-NULL-RFB draw of each cell. The
  contract attaches this control to the real arm; running it here on a *null*
  object costs nothing, touches no real data, and checks that INT-2 as
  implemented really is the intermediate before any real arm is authorized.
  Result: **1000 of 1000 verified at bits 16 and 1000 of 1000 at bits 20.** It
  is an instrument check and is not evidence about anything.
- **ADDITION (declared, non-decisional): the admissible-support fraction of the
  representative OBJ-NULL-RFB draw** is recorded alongside the CAL-4 figure.
  Both are 1.0.
- **REPORTED-BUT-NOT-FROZEN NUMBERS.** `results/calib/power_curve.json` and the
  CAL-3 block of `instrument_characterization.json` report detection /
  exceedance rates obtained by *mechanically evaluating the frozen THR-EQD-1
  order-statistic form* (the 199th ascending order statistic of the same run's
  200 CAL-1 replicate values) against the measured CAL-2 / CAL-3 values. This is
  required to produce CAL-2's declared output at all. It is a measurement
  report, not a freeze: every raw replicate value is archived so
  TASK-20260801-023 can recompute independently, no threshold is written
  anywhere as a threshold, **the CERT-EQD-1 predicate is not evaluated and no
  certified delta is declared here.**
- **No other deviation from the approved protocol.** No parameter was retuned,
  no statistic added or dropped, no reading rule applied, no branch selected, no
  hypothesis touched.

## 5. What the package deliberately does not contain

No factorization, no largest prime factor, no smoothness indicator, no Dickman
evaluation, no u ladder, no search arm, no relation harvest, no claw table, no
charged unit, no cost identity, no R, no timing decision variable.
`wall_seconds` appears for budget accounting only. AP-1 was not touched: no
EXP-DS-001 or EXP-SMTH-001 file was read-modified, imported, edited or staged.

## 6. Budget and reproduction

Wall clock 59.19 s against the 3600 s budget; peak RSS 175,636,480 bytes
(0.164 GiB) against the 4 GiB budget; one run of record. Re-executing the
recorded command at the same revision into a scratch directory reproduced all
three result files **byte-for-byte identical** (sha256 of each file equal). That
verification run is a determinism check, not a second run of record, and its
output was discarded rather than selected from — it was identical, so there was
nothing to select.
