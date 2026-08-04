# Red Team Report — TASK-20260802-314 (RT-20260802-314)

Independent adversarial review of frozen amendment
`PA-IT-001-v3-rc43-repair-3` (EXP-IT-001), snapshot commit
`9f3b2a7ad534a261f0d258f00486dbef4bc197b6`, BATCH-043, GOAL-ECDLP-001.

Claim under review: whether `PA-IT-001-v3-rc43-repair-3` closes
RT-20260802-244 findings B1..B3 and M1..M3 **without residual Executor
discretion, anomalous cost-model inversion, or Pareto honesty failure**, so a
later toy Executor batch could be admitted against this contract.

Claim ceiling for this task: **design review only.** No experiment was run, no
measurement was taken, no hypothesis or goal status is changed, and no run,
timing, or statistic is asserted. All numbers below are arithmetic on the
*frozen constants already written in the contract* — they are contract
consistency checks, not experimental results.

## Verdict: REVISE

RT-244 M1, M2, M3 and the wording bar of B2 and B3 are closed. **B1 is not
closed**: the overlay replaced the field-DLP formula with a linear Smart-scale
formula whose disclosed constant is large enough to re-invert `R_xfer` at four
of the five frozen bit cells — the same model-inversion class
(RT-146-O1 / RT-130-O4) that B1 exists to kill. Fixing B1 this way also
introduced two new contract-consistency defects (a silent conflict with the
frozen spec-v3 anomalous charge, and a silent change of the frozen density
abscissa) that themselves reopen the discretion concern. These are repairable
in a superseding overlay, hence REVISE rather than FAIL.

---

## Blocking findings

### RT-314-B1 — anomalous pass threshold still inverts `R_xfer` (RT-244-B1 NOT closed; RT-146-O1 / RT-130-O4 class reopened)

- **Frozen clauses:**
  - `experiments/EXP-IT-001/amendments/PA-IT-001-v3-rc43-repair-3.yaml#cost_model.C_special_smart`
    (`C_special = ceil(c_smart * log2(p))`, `c_smart = 64`)
  - `...#predictions[0]` ("CTRL-ANOMALOUS-TRACE1 passes with R_xfer < 0.7 when
    C_special_smart is used …")
  - `...#test_boundary` (`bits in {16,18,20,22,24}`)
  - baseline: `experiments/EXP-IT-001/specification.v3.yaml#experiment.inputs.cost_ledger.matched_rho`
    (`0.886 * sqrt(N)`) and
    `#preregistered_prediction` / `#heur_iso_1_decision_rule.rate_band`
    (`R_xfer < 0.7` is the transfer-win threshold)

- **Finding.** For an anomalous trace-1 plant the frozen detector is
  `#E(F_p) == p` (spec v3
  `special_family_detectors.anomalous_trace_eq_1.boolean`), so the group order
  `N` equals the prime `p`: `h = 1` and `log2(p) = bits` exactly. The pass
  metric is `R_xfer = (C_path + C_special + C_pullback) / matched_rho` with
  `matched_rho = 0.886 * sqrt(N) = 0.886 * 2^(bits/2)`. The anomalous positive
  control passes only if `R_xfer < 0.7`.

  Substituting the overlay's own frozen constant `C_special_smart =
  ceil(64 * bits)` and ignoring the strictly-positive `C_path` and
  `C_pullback` (i.e. the most attack-favorable case), the special charge
  **alone** already exceeds the pass threshold at all but one cell:

  | bits | matched_rho = 0.886·2^(bits/2) | 0.7·matched_rho | C_special_smart = 64·bits | C_special_smart / matched_rho | anomalous control |
  |------|-------------------------------:|----------------:|--------------------------:|------------------------------:|-------------------|
  | 16   | 226.8                          | 158.8           | 1024                      | 4.51                          | **FAIL**          |
  | 18   | 453.6                          | 317.5           | 1152                      | 2.54                          | **FAIL**          |
  | 20   | 907.3                          | 635.1           | 1280                      | 1.41                          | **FAIL**          |
  | 22   | 1814.5                         | 1270.2          | 1408                      | 0.78                          | **FAIL**          |
  | 24   | 3629.1                         | 2540.3          | 1536                      | 0.42                          | possible (0.28 headroom before C_path + C_pullback) |

  Only `bits = 24` can satisfy `R_xfer < 0.7`, and only after `C_path +
  C_pullback` consume less than the remaining `0.28 · matched_rho ≈ 1004`
  group-op equivalents. At the four other frozen cells the anomalous
  positive control cannot pass **by construction of the frozen constant**,
  regardless of how cheap the true Smart attack or the isogeny path is. The
  overlay's own prediction (`R_xfer < 0.7` on the anomalous arm) is therefore
  structurally false across the majority of its own frozen bit set.

  This is exactly the RT-244-B1 failure mode. B1 required charging the
  anomalous arm at genuine Smart scale so that a real trace-1 plant with tiny
  true attack cost passes; the overlay instead swapped the field-DLP formula
  `ceil(2*sqrt(N*))` for `ceil(64·log2 p)` — asymptotically smaller, but with a
  constant chosen large enough (`c_smart = 64`) that the inversion survives at
  toy scale. The number `64` is asserted, not derived from any Smart-algorithm
  operation count or bound (the target-result-profile requires per-entry
  constants justified by a bound). Smart's linear-time solve on an anomalous
  curve is a handful of field operations, not `64·bits` group operations; the
  constant is the entire mechanism of the surviving inversion.

- **Cheapest falsification (no run required).** Take the spec-designated plant
  cell `bits = 20` (spec v3 `CTRL-NULL-IT-PLANT.injection` designates
  `seeds[0]`, first curve of `bits = 20`). Then
  `C_special_smart = 64·20 = 1280` while `0.7·matched_rho = 0.7·0.886·2^10 =
  635`. Since `1280 > 635`, `R_xfer ≥ 1280/907 = 1.41 ≥ 0.7` before any path or
  pullback cost is added — the anomalous positive control fails on the constant
  alone. Pure arithmetic on the frozen contract; no experiment, seed, or timing
  is needed.

- **Narrowest supported statement.** As frozen, `C_special_smart` closes B1
  *only* at `bits = 24`. For the anomalous positive control to hold across the
  frozen bit set, `c_smart` (or the whole `C_special_smart` form) must be
  recalibrated so that `C_special_smart + min(C_path + C_pullback) <
  0.7·0.886·2^(bits/2)` at every cell the anomalous control is evaluated on,
  with the constant justified by an explicit Smart-attack operation count.

### RT-314-B2 — two frozen anomalous charges and an unpinned plant bit size leave the pass/fail outcome to Executor discretion (RT-244-B1 / B3 residue)

- **Frozen clauses:**
  - overlay `#cost_model.C_special_smart` (`ceil(64·log2 p)`, linear)
  - spec `experiments/EXP-IT-001/specification.v3.yaml#experiment.inputs.cost_ledger.C_special.anomalous_trace_eq_1`
    (`C_special_anomalous = ceil(20 * (log2 N)^2)`, quadratic)
  - overlay `#cost_model` (defines no `C_rho` / `matched_rho`; the denominator
    lives only in the spec)
  - overlay `#test_boundary`, `#cost_model.anomalous_curve_requirement` (no
    bit size pinned for the anomalous plant)

- **Finding.** The overlay is a `repair_overlay` on the frozen spec v3, but it
  introduces a **second, different** anomalous cost formula without a
  supersession clause. Spec v3 freezes `C_special_anomalous =
  ceil(20·(log2 N)^2)` (quadratic); the overlay freezes `C_special_smart =
  ceil(64·log2 p)` (linear). The overlay's `forbidden_formulas` /
  `c_special_mov_decision_note` only ban the field-DLP `ceil(2*sqrt(N*))` and
  MOV `ceil(0.886*sqrt(p^k))` forms — they are **silent** on the spec's own
  quadratic anomalous charge. An Executor implementing `run_bounded_toy.py`
  against "spec v3 as amended" faces two live, contradictory frozen numbers for
  the same charge and must choose one. That choice determines pass/fail (both
  currently fail at `bits = 20`: linear → 1.41, quadratic → 8.82), so B3's
  "no Executor discretion" guarantee is not actually met for the cost model —
  it was met only for the *command surface*.
  Compounding this, the overlay never restates `matched_rho`/`C_rho`; the pass
  metric's denominator is defined only in the parent spec, so the overlay is
  not self-contained about the very ratio it gates on.
  Separately, the anomalous plant bit size is not pinned anywhere in the
  overlay, so even under a single formula the one viable cell (`bits = 24`)
  vs the failing cells (`16/18/20/22`) is Executor-selectable.

- **Cheapest falsification (no run required).** Diff
  `spec.v3#…cost_ledger.C_special.anomalous_trace_eq_1` against
  `overlay#cost_model.C_special_smart`: two distinct frozen formulas
  (`20·(log2 N)^2` vs `64·log2 p`) with no clause in the overlay stating which
  supersedes. Evaluate both at `bits = 20`: 8000 vs 1280 group-op equivalents —
  a contradiction the frozen contract does not resolve.

### RT-314-B3 — overlay silently changes the frozen density abscissa (preregistration integrity)

- **Frozen clauses:**
  - overlay `#test_boundary` / `#predictions[4]` / `#repairs[R3-FIX-PRESERVE-DENSITY]`
    (`bits in {16,18,20,22,24}`)
  - spec `experiments/EXP-IT-001/specification.v3.yaml#experiment.inputs.density_universe.bits`
    (`[20, 24, 28]`) and `#claim_ceiling` ("20/24/28-bit prime-order
    subgroups") and `#heur_iso_1_decision_rule.density_freeze` (rho_special and
    `F_hit` table frozen for `bits in {20,24,28}` "before any path search")

- **Finding.** The overlay's density scan and bit set are `{16,18,20,22,24}`:
  it **adds** `16, 18, 22` and **drops** `28` relative to the frozen spec-v3
  density universe `[20,24,28]`, with no supersession clause and no
  recomputation of the preregistered `rho_special(bits)` / `F_hit_table` at the
  new cells. Spec v3 requires those density quantities frozen before sampling
  (`density_freeze`) and lists editing preregistered density as a protocol
  violation. The overlay's `R3-FIX-PRESERVE-DENSITY` claims to *preserve* the
  rc36 CI protocol while actually shifting its abscissa. The direction of the
  change is adversarially notable: the three added low-bit cells (`16, 18`) and
  (`22`) are precisely where RT-314-B1's cost inversion is worst, and the
  dropped cell (`28`) is where the linear Smart charge is most favorable to the
  anomalous arm. This is not alleged intent — but the contract must justify a
  change to a frozen preregistered abscissa, and this one is unjustified.

- **Cheapest falsification (no run required).** The spec requires
  `HEUR_ISO_1_report.json` to embed the `F_hit` table at frozen
  `rho_special(bits)` for `bits in {20,24,28}` before path search; the overlay
  density scan at `bits in {16,18,22}` has no frozen `rho_special` to compute
  against, so the report is either undefined at those cells or silently
  redefines a preregistered quantity.

---

## Major (non-blocking) findings

### RT-314-D1 — density scan has no stated decay direction and no null-object control

Per inventor-protocol §3, a reported signal is an artifact until measured
against a null object of the same shape, and one must name the parameter that
destroys the signal. The overlay's density scan reports per-bit Wilson CIs but
states no expectation that `rho_special` must **decay** as `bits` increases,
and adds no null-object control (density of special-family hits under a random
graph / random `j`-map of the same degree API). The spec's `F_hit` model and
`NULL-IT-ISOGENY-TRANSFER` object partially supply this, but only at the
frozen `{20,24,28}` cells — not at the overlay's added low-bit cells.
**Cheapest control:** at each bit, compute the identical special-density
statistic on the frozen `NULL-IT` random-graph object and confirm the special
density decays with `bits` on the real graph and stays at the null rate on the
random object; a real density that does not decay with `bits` is the canonical
artifact tell.

### RT-314-D2 — "single command string" (B3) is satisfied by an entrypoint, not literally one string

The overlay binds one entrypoint (`run_bounded_toy.py`, `.sage` dropped, no
CLI-adjust language — B3 wording closed) but freezes **two** command strings
(`smoke`, `measure`) and the note reads "exactly these strings (or the
smoke/measure pair as written)," which is mildly redundant. This removes flag
discretion and is acceptable, but the parenthetical should be tightened so
"these strings" unambiguously means the frozen pair and nothing else.

### RT-314-D3 — `c_smart` and unit conversion undisclosed against the profile

`c_smart = 64` is disclosed as a value but carries no operation-count
justification, and `C_special_smart` is charged in "group-op equivalents"
without stating the field-op → group-op conversion. The target-result-profile
requires per-entry constants and unit conversions to be explicit and justified.
This is the mechanism behind RT-314-B1 and should be fixed there; flagged
separately so a recalibration does not merely swap `64` for another unjustified
number.

---

## Closure ledger vs RT-244

| RT-244 id | Requirement | Status under `PA-...-rc43-repair-3` |
|-----------|-------------|-------------------------------------|
| B1 | Anomalous arm charged at Smart scale so a real trace-1 plant passes; never field-DLP | **NOT closed** — linear formula but `c_smart=64` re-inverts `R_xfer` at bits 16/18/20/22 (RT-314-B1) |
| B2 | Quantitative / explicit `not_applicable` three-axis `sota_delta` + `dominated_by` + non-solver scope | Closed at wording (present in amendment, artifact-and-cost-plan, rationale). Future run must still carry BSGS + specialized comparator rows; spec already lists `matched_BSGS`. |
| B3 | Exactly one binding entrypoint, no CLI discretion | Command surface closed; **cost-surface discretion remains** via dual anomalous formulas + unpinned plant bits (RT-314-B2). Minor RT-314-D2. |
| M1 | start nonspecial + reverse-of-planted + end nonspecial + pullback + relation reverified | Closed (`control-matrix.yaml#CTRL-TRANSFER-NONSPECIAL`, `R3-FIX-M1`) |
| M2 | `recompute_null_plant_from_ledger.py` in archive manifest; absence invalidates | Closed as path-declared (`implementation_archive_manifest`, `R3-FIX-M2`) |
| M3 | Ban MOV formula only as pass threshold; allow labeled comparator | Closed (`c_special_mov_decision_note`, `R3-FIX-M3`) |

New defects introduced while closing B1: RT-314-B2 (formula conflict /
discretion), RT-314-B3 (abscissa change).

## Baseline comparison (Pollard-rho / BSGS / specialized)

- `dominated_by = "Pollard rho at exponent 1/2 (matched negation)"` is a
  correct, non-null generic baseline for ordinary prime-order subgroups; rho
  dominates matched BSGS (same `sqrt(N)` time, less memory), so naming rho as
  the tightest generic frontier row is defensible, and spec v3 already records
  `matched_BSGS = 2·ceil(sqrt(N))` as a comparator. The closest specialized
  baseline for the anomalous arm is Smart's linear-time solve — which is
  exactly the charge RT-314-B1 shows is mis-modeled. So the Pareto *fields* are
  honest for this design-only overlay (`sota_delta` all `not_applicable` with
  non-solver scope), but the specialized-baseline **charge** used inside the
  gate is wrong; no `sota_delta` is fabricated here (it is correctly
  `not_applicable`), so this is a B1 cost-model issue, not a Pareto-honesty
  violation.

## Scope limits (what this review does and does not conclude)

- This is a **design review of a frozen text**. It asserts no experimental
  result, no timing, no success/failure of any run, and no
  hypothesis/goal/knowledge status change. H-IT-001 stays `specified`;
  GOAL-ECDLP-001 stays `active`.
- The verdict concerns only whether this overlay closes RT-244-B1..B3 /
  M1..M3 without residual discretion or cost inversion. It does **not** conclude
  that the isogeny-transfer lane is dead, that HEUR-ISO-1 is false, or that the
  approach cannot work at toy scale — only that the frozen constants as written
  cannot support the anomalous positive control across the frozen bit set.
- All arithmetic uses constants copied from the frozen contract; if the
  Coordinator recalibrates `c_smart`, pins the plant bit size, reconciles the
  overlay with the spec anomalous formula, and restores/justifies the density
  abscissa, the same checks should be re-run against the new constants.

## Required next action (one concrete step)

Author a superseding repair overlay `PA-IT-001-v3-rc44-repair-4` that:
(1) recalibrates the anomalous charge so `C_special_smart + min(C_path +
C_pullback) < 0.7·0.886·2^(bits/2)` holds at every bit cell where
CTRL-ANOMALOUS-TRACE1 is evaluated, with `c_smart` justified by an explicit
Smart-attack operation count and unit conversion (fixes RT-314-B1, RT-314-D3);
(2) adds an explicit supersession clause stating `C_special_smart` replaces
spec v3 `C_special.anomalous_trace_eq_1` and restates `matched_rho`, and pins
the anomalous plant bit size (fixes RT-314-B2); (3) either restores the frozen
density abscissa `{20,24,28}` or justifies the new set and re-freezes
`rho_special`/`F_hit` at every scanned cell (fixes RT-314-B3). Do not admit an
Executor run against `PA-...-rc43-repair-3`.

## Non-claims

No experiment performed. No implementation performed. No run, timing, or
statistic invented. No novelty, SOTA, support, rejection, closure, or
breakthrough claimed. No official research state changed.
