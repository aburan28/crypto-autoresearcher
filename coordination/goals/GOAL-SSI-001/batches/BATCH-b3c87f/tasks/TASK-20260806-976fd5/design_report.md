# Design report — TASK-20260806-976fd5

**Deliverables frozen:** `ledger/hypotheses/H-SSI-7fe2bf.yaml`,
`experiments/EXP-SSI-697354/specification.yaml` (status `approved`,
`frozen: true`).
**Source proposal:** `IDEA-20260803-48e258`.
**Nothing was run. No goal status changed. Nothing was promoted to `knowledge/`.
No commit was made.**

---

## 1. What the object actually is

`p*(w)` — the prime size at which the corrected `p^{1/3+o(1)}` cost curve
crosses the matched Delfs–Galbraith / previous-methods `p^{1/2}` curve, as a
function of available memory `w`. It is emitted as a **curve over a
rectangle**, not a number: `log2 p ∈ [256, 768]` solved for, `log2 w` swept
over 14 declared values, under 160 pre-declared scenario tuples per
memory-charging convention.

Because a crossing need not exist inside a bounded window, the contract defines
four outcomes per cell, all first-class and all reportable:
`numeric p*` · `NO_CROSSOVER_IN_WINDOW` (with both endpoint signs and values) ·
`INFEASIBLE_AT_MEMORY` · `MULTIPLE_ROOTS`. A curve that is categorical in part
of the rectangle is the honest answer there, and the contract forbids
extrapolating a root past the window to manufacture a number
(`ROOT_OUTSIDE_WINDOW` is reported without a value).

## 2. Inputs, by path and row count

| Input | Path | Extent |
|---|---|---|
| **T1** per-entry table | `coordination/goals/GOAL-SSI-001/batches/BATCH-046/tasks/TASK-20260804-55952a/implementation/cost_measurements.json` | `$.scaling_summary`, **8 rows**, columns `log2_p` and `avg_mults_per_entry` |
| **T2** paper anchor | `inputs/P13-WESOLOWSKI-2026/paper_fulltext.md` lines **234–238** | **5 rows**: `log2 p`, time lower bound, memory lower bound, previous-methods time |
| T2 independent transcription | `coordination/tasks/TASK-20260724-P13-VAL/repro/experiments/EXP-P13VOW-001/cost_model.py` lines 60–66 | cross-check only |
| **T3** declared scalars | `red_team_concrete_cost.yaml`, `concrete_cost_analysis.md`, `EV-SSI-59f7a2`, `EV-WESO-001` | each value bound to a quoted source |

Every row is re-extracted at run time and compared to literals frozen in the
spec; a mismatch invalidates the run as input drift.

**The single most useful thing found while reading the inputs:** the paper's own
Section 4.1 bullets carry a *previous-methods* column (`2^128, 2^192, 2^256,
2^288, 2^384`), which equals `2^{log2 p / 2}` at all five rows. That is the
matched baseline, committed verbatim. It means the absolute locus is computable
without the bibliographic subtask that `IDEA-20260803-48e258` flagged as
**BLOCKING** — the proposal's `F5` degradation route does not fire. The honesty
cost is stated rather than hidden: this is *the paper's own rounding*, not an
independently transcribed Delfs–Galbraith constant, and `KN-TECH-050` says
plainly that the corpus is "insufficient to state what the matched baseline
costs". So `log2 k_DG = 0` is carried as **HEUR-XO-2**, the ratio form is the
primary object, and `d(p*)/d(log2 k_DG)` is reported at every `w`.

## 3. Cost functions, exactly

Corrected per-entry law, four declared readings of T1 (all linear in `log2 p`,
which is the form of T1's own analytical counting rule):
`L1` proportional fit on all 8 rows · `L2` the transcribed headline `16.2` ·
`L3` OLS with intercept · `L4` largest-row anchor. A fifth law `L5` propagates
the committed `alpha = 1.1321` from `EV-WESO-b6ceff` / `KN-FIND-4e7a92` — which
that finding records as *never having been propagated into any margin row* — as
a declared sensitivity, outside the main band.

```
MC_P13   T_A = L_paper(P) + E(P) + S + c·√P + A − 0.5·min(log2 w, L_mem(P))
         T_B = P/2 + log2 k_DG + A                      (memoryless baseline)

MC_VOW   T_A = L_paper(P) + E(P) + S + c·√P + A         (only if log2 w ≥ L_mem(P))
         T_B = P/2 + log2 k_DG + A − 0.5·log2 w         (vOW baseline at memory w)
```

Solve `Δ(P) = T_B − T_A = 0` by a 513-point bracket scan on `P ∈ [256, 768]`
step 1.0, then bisection to `|Δ| < 1e-9` on the **first** bracketing interval,
with every sign change counted and reported.

### The finding that shaped the design

The corpus contains **two committed, incompatible chargings of the same
van Oorschot–Wiener law**, and no record reconciles them:

- `EXP-P13VOW-001` gives the memory discount to the **attack**
  (`T_w_vOW = T_full / sqrt(min(w, M))`), and `EV-WESO-001` records the
  consequence: the method "beats Delfs-Galbraith at every tested budget
  `w = 2^30..2^80` for all five sizes."
- The paper's Section 1.1 law, as quoted in `RT-20260805-92751c` OBJ-5
  (`time p^{1/2+o(1)}/(w^{1/2}·n)`), gives it to the **baseline**, and CMC-4
  records the opposite consequence: "At any feasible memory `w`, VW gives time
  `p^{1/2}/w^{1/2} ~ 2^{128}`."

They imply opposite signs for the same comparison and opposite monotonicity in
`w`. `IDEA-20260803-48e258`'s own instrument guard asserts the second
("more memory helps the vOW baseline and pushes `p*` UP"); the campaign's
committed model implements the first. **A contract that picked one silently
would be manufacturing the sign of its own answer.** So the convention is an
explicit two-valued axis, both branches traceable to committed artifacts, and
`H-SSI-7fe2bf` H2 predicts the convention — not the estimator correction —
controls the sign. `SANITY-1` additionally audits `MC_P13` against physical
coherence and reports `MODEL_PATHOLOGY` if the committed formula implies the
attack gets cheaper as memory shrinks.

## 4. The three mandatory controls, and how each can fail

**(1) Reproduction gate `RG-1..RG-5` — blocking.** Recovers `EV-SSI-59f7a2`'s
bracket at the parameters that record used (`log2 p = 256`, unbounded memory,
memoryless baseline).

- `RG-1` **derives** the low endpoint: `106.5 + log2(a·256)` must land in
  `[118.25, 118.75]` under all four laws. Design-time hand computation gives
  `[118.461, 118.569]` — a 0.5-bit window around a 0.11-bit spread. A misread
  column, a wrong JSON pointer, a transposed row, a wrong anchor row, or a wrong
  fit form moves it out. **This can fail.**
- `RG-2/RG-3` place the upper endpoint using the declared surcharge `S = 3.0`
  and the committed hardware factor `alpha = 3`, reproducing `2^{121.5}` and
  `2^{120}–2^{123}`.
- `RG-4` requires the **unit of each endpoint** of the committed `[118.5, 123]`
  bracket to be reported, and whether they differ. The reconstruction suggests
  the low endpoint is in `F_{p²}`-operations and the high endpoint in
  AES-equivalents. Either outcome passes; *failing to report which* fails the
  gate.
- `RG-5` requires the scenario grid to cover the committed 6–11 bit
  gap-below-target interval, and to report its own span where that is wider.

Honesty flag carried in the spec: `S_struct = 3.0` is **not re-derived** — the
committed record does not decompose it. So the gate is deliberately split: `RG-1`
derives, `RG-2` only checks placement. Presenting `RG-2` as a derivation would
have been a fabricated reproduction.

**(2) Null object — non-blocking, three distinct failure modes.** The *same
procedure*, same code path, with `E(·)` swapped for the **superseded**
one-operation-per-entry convention (`N0`, `E = 0`) and for the superseded
Vélu estimator (`N1`, `E = 9.8`, superseded by OBJ-3). Pre-registered:
`min D_null0 ≥ 11.9` bits, `D_null1 ∈ [1.5, 4.0]` at `P = 256`, and
`D_null1 < D_null0` at every `P`. Fails if the correction moves nothing
(< 1.0 bit, proposal `F4`), if the two nulls order wrongly (`F6`), or if the
displacement is nonzero but not the one `EV-SSI-59f7a2` performed.

The displacement is measured on the **margin surface**, not only on the locus.
That is deliberate: if every cell turns out categorical, a locus-only null
control would have no resolution and would pass by having nothing to say. The
surface always has resolution.

**(3) Monotonicity in `w` — blocking, five limbs.**
`MONO-1` slopes (`+0.5 / 0` under `MC_P13`, `−0.5` under `MC_VOW`);
`MONO-2` the **clamp kink** must sit exactly at the committed `L_mem(P)` values
`92.5 / 138.6 / 181.3 / 206.0 / 272.2` — dropping the `min()` is the single most
likely wiring defect and produces no kink at all;
`MONO-3` direction of `p*(w)`, reporting `NOT_EVALUABLE(n=…)` rather than `pass`
when fewer than two numeric loci exist;
`MONO-4` the two conventions must differ somewhere;
`MONO-5` a **data** check on the committed table — `L_paper(P) − P/3` strictly
increasing in `[21.0, 47.0]`, `L_mem(P) − P/3` non-decreasing. `MONO-5` is not
implied by any formula in the contract; it is the only in-corpus handle on the
superpolynomial `o(1)` term that `docs/claims-and-verification.md` requires be
characterised.

This directly targets the failure mode named in the batch's red-team card
(`KN-TECH-1a5b7e`: 33 consecutive batches of controls that all passed because
none could fail). Every control names the concrete input that would make it
return a negative, and `MONO-3` is explicitly forbidden from passing vacuously.

## 5. Executability — checked, not assumed

`requirements-dev.txt` pins only PyYAML, sympy, pytest. A committed validation
receipt (`coordination/tasks/TASK-20260724-P13-VAL/validation_report.yaml`
lines 74, 98) records the managed runtime as Python 3.12.13 with numpy 2.4.4 and
scipy/mpmath absent. A committed merge digest
(`coordination/events/main/f12e21b55a8d.yaml` line 42) records that a working
SageMath/g6k environment had to be *requested*, and `EXP-P13-NC36` was never
executed for that reason. Two committed records therefore disagree about this
container's package set across time.

**The contract resolves that structurally rather than by trusting either
reading: the primary path is Python 3 standard library only** — a strict subset
of "numpy alone", so it cannot be blocked by either. numpy appears exactly once,
in optional cross-check `XCHK-2`, whose absence is recorded `NOT_RUN` and
changes no reported number. Sage, g6k, fpylll, scipy, mpmath and network access
are forbidden, and step 0 of the run must record `find_spec` for each.

The Dickman-ρ / B-optimisation machinery that would have needed numpy is
**not on the primary path at all**: `L_paper` and `L_mem` come from the paper's
5-row table directly. `XCHK-2` re-derives them only as a cross-check, and its
tolerance is the *committed observed* 3.51-bit deviation from `EV-WESO-001`, not
the 0.75-bit tolerance that script declares internally.

## 6. Carrying the input's uncertainty honestly

`IDEA-20260803-48e258` says the **sign** of the margin is robust and the
**magnitude** is not. A contract producing one confident curve would contradict
its own input. So every output is a band with its composition disclosed:
4 per-entry laws × 2 structural surcharges × 4 AES-equivalence models
× 5 overhead scenarios × 2 memory conventions, plus an `L5` extrapolation
sensitivity, plus a `log2 k_DG` sensitivity, plus an explicitly reported
adversarial corner (smallest `E`, `S = 0`, pure-RAM `alpha = 0.3`, `c = 0`,
`MC_P13`) against which any headline must survive.

Two guards against reading the band as more than it is: the spread of four
readings of **one** 8-row table at **one** implementation is not a confidence
interval and may never be reported as error bars; and a band without its
categorical counts (`n_numeric`, `n_no_crossover_*`, `n_infeasible`) is
incomplete by contract.

The `18` measured-gamma readings and the `c` bracket `[1.327077, 1.576444]` are
**deliberately not used**: they sit outside this task's read scope, and the
proposal forbids citing `c` as a number rather than as a bracket with eight
attachments this task cannot enumerate. The overhead axis instead uses the
scenario form `2^{c·√(log2 p)}` named in `EV-WESO-001`, at `c = 0` (which that
record calls "the most attack-favorable corner, not a neutral default") and
`c ≈ 1.8` ("a defensible calibration"), extended by three values from the
committed `OVERHEAD_C` grid — declared in the spec as a read-scope extension.

## 7. Affected-vs-safe scope, and a correction to the batch card's phrasing

The handoff asked that the contract note "NIST-III/V retain margin under every
tested overhead scenario". That phrase traces to `EV-WESO-001` and to
`analysis/SSI-ECDLP-SYNTHESIS-20260803.md` line 171 — **and under the committed
paper table it is true on only one of three axes.** The contract therefore
computes all three separately and forbids the unqualified sentence:

- **SCOPE-A — advantage over the matched baseline.** Predicted to *increase*
  with level (the `p^{1/2} − p^{1/3}` spread grows with `p`). The source
  sentence in `EV-WESO-001`'s red-team observation ("NIST-III/V margins survive
  all tested scenarios") sits in a context — "shrinks the NIST-I margin to ~2.3
  bits" — where "margin" means the *attack's advantage*. On this axis NIST-III/V
  are more exposed, not less.
- **SCOPE-B — gap below the level's own target** (`2^128 / 2^192 / 2^256`).
  Design-time arithmetic on the committed table: **≈ 9.5 / 22 / 39 bits** at
  `S = 0, A = 0, c = 0`. The gap *grows* with level. NIST-III/V are not safer on
  this axis either, in the unbounded-memory model.
- **SCOPE-C — memory feasibility.** Required table: `2^{98.5} / 2^{144.6} /
  2^{187.3}` bytes at 64 B/entry, against `~2^{73}` bytes of recorded global
  storage. Infeasible at all three levels, **infeasibility increasing with
  level. This is the only axis on which NIST-III/V retain more margin**, and any
  safety statement must name it.

Smoothing A and B into "NIST-III/V retain margin" would have laundered a false
safety claim into a frozen contract. Stating it by axis costs nothing and is
checkable.

**Affected (conditionally, in-model):** supersingular Isogeny/EndRing/OneEnd-based
constructions at `log2 p ∈ [256, 768]`, the SQIsign family named — only in the
unbounded-memory model, only conditional on Heuristic 1 and HEUR-XO-1..3, only
as a cost model.
**Out of range:** CSIDH and other group-action or torsion-based constructions
(`EV-WESO-001` boundary).

## 8. WHAT THIS EXPERIMENT CANNOT CONCLUDE

This section is binding on every artifact produced under `EXP-SSI-697354`.

1. **It cannot conclude anything about SQIsign's security.** It may not assert
   that SQIsign, or any SQIsign parameter set, is broken, weakened, or unsafe.
   It costs a model. No attack is executed; no isogeny, curve, field element,
   walk or table is constructed at any scale.
2. **It cannot validate Heuristic 1, and cannot substitute for that pairing.**
   NC-3/NC-6 is `failed_infrastructure` (`EV-WESO-b6ceff`), which under AGENTS.md
   rule 5 is evidence in *neither* direction. `KN-FIND-d1c853` records this as
   the dominant open uncertainty. Every emitted curve is conditional, and if
   Heuristic 1 is later refuted or repaired the curves are **recomputed, not
   defended**.
3. **It cannot make a crypto-tier claim.** The load-bearing measured input tops
   out at `p = 2^40`; the mechanical rule in `docs/claims-and-verification.md`
   caps this at `medium`. Every number at `log2 p ∈ [256, 768]` is an
   extrapolation of `6.4×`–`19.2×` beyond the fit window (HEUR-XO-1) and is
   stamped as such per cell. It is never crypto-scale validation (rule 7).
4. **It cannot decide which memory-charging convention is physically correct.**
   It makes the dependence explicit and carries both. The successor it names —
   a derivation note deriving the vOW law for *both* sides from one cost model —
   is the highest-value cheap follow-up this design identifies.
5. **It cannot pin the baseline constant `k_DG`.** `KN-TECH-050` and
   `EV-WESO-b6ceff` both say the corpus cannot. The ratio form is primary; the
   absolute locus is emitted at the paper's own convention with
   `independently_transcribed: false` and a reported sensitivity.
6. **It cannot repair the `ell`-range mismatch.** T1 exercises only
   `ell ∈ {2,3,5}` while `RT-20260805-92751c` OBJ-1 states the operating `ell`
   at NIST-I is far larger, and that the linear extrapolation approximates the
   FFT figure only because two errors partially cancel. This is the largest
   modelling weakness and it is *carried*, not resolved.
7. **It cannot characterise the `o(1)` term.** It measures the committed table's
   `o(1)` signature (`MONO-5`) and treats the term as fixed over the plotted
   range. That is the largest modelling gap for a crossover locus at large `p`.
8. **It cannot conclude that a model crossover is a practical crossover.**
   Implementation constants, parallelism, memory hierarchy and batched
   evaluation are outside the model entirely.
9. **It cannot produce a confidence interval.** The scenario grid is a set of
   readings of one table at one implementation. Reporting its spread as error
   bars is a claim-tier violation.
10. **A vacuously satisfied bound concludes nothing.**
    `IDEA-20260803-48e258`'s pre-registered bound (`p*(w) > 2^512` for
    `w ≤ 2^40`) is expected to be satisfied *vacuously*, because
    `L_mem(256) = 92.5 > 40` makes the method memory-infeasible across that
    entire `w` range. The contract requires those exact words and forbids
    presenting it as substantive confirmation.
11. **Infrastructure outcomes conclude nothing.** A missing module (including
    numpy), an unreadable path, a parse failure or budget exhaustion is
    infrastructure signal. `UNREACHED` is distinguished in the artifacts from
    `INFEASIBLE_AT_MEMORY` and `NO_CROSSOVER_IN_WINDOW`, which are substantive.
12. **A completed run is not evidence until it is archived and independently
    reviewed.** The contract requires Validator re-derivation of `RG-1..RG-5` by
    an independently written implementation and a Red Team pass on the
    convention treatment and on whether any emitted sentence licenses a claim
    the model cannot support.

## 9. Expected value, and how it could be worthless

**Best case:** the campaign gets three things for zero compute — a reproduction
of its own committed bracket from raw tables (which has never been done), a
demonstration that an *unstated modelling choice*, not overhead magnitude,
controls the sign of its headline comparison, and a practitioner-facing
rectangle with its band composition disclosed. It also propagates the committed
`alpha = 1.13` excess for the first time, closing an open qualification named in
`KN-FIND-4e7a92`.

**Worthless case, named in advance:** if `F5` fires (the two conventions agree
in sign everywhere) *and* `F2` fires (the locus band is proportionally no
narrower than the margin band), the reconditioning thesis is dead and the
deliverable is the negative. If `F4` fires (`min D_null0 < 1.0` bit), the
BATCH-046 correction is not load-bearing for this object and the record must be
re-described. Both are publishable negatives and neither is a reason to have
skipped the run.

**Residual design risk I could not remove.** Design-time hand arithmetic
suggests a large fraction of the rectangle will be categorical
(`NO_CROSSOVER_IN_WINDOW` under both conventions at `c = 0`, in *opposite*
directions), which would push `MONO-3` and the `F2` band comparison toward
`NOT_EVALUABLE`. Adding the committed overhead axis `c` is what restores
numeric loci in a substantial part of the grid — at `c = 2` the crossing moves
inside the window and sweeps with `w`. If the Executor's arithmetic disagrees
with my hand arithmetic here, that disagreement is itself the first thing
`RG-1` and `MONO-3` will surface, which is the correct place for it to appear.

## 10. Pre-registration disclosure

All design-time expectations (`a1 = 15.576908`, `T_A(256)` per law,
`L_paper(P) − P/3`, the scope orderings, the `L5` displacement, the null
displacement bands) were computed **by hand from the committed literals at
freeze time** and are recorded in the spec under
`preregistered_prediction.frozen_reference_values`. They are **pre-registration,
not results.** They are published so a reviewer can check whether the tolerance
windows were set before or after the numbers were seen. Changing any of them
after an output is observed requires a versioned `protocol_amendment` and a new
experiment version.

## 11. Observation recorded, not acted on

`ledger/goals/GOAL-SSI-001.yaml` does not exist, and no sharded
`ledger/goals/GOAL-SSI-001/` directory exists, although `BATCH-b3c87f` names it
in a read scope and `TASK-20260806-91f36a` declares it in a write scope. Flagged
for the Coordinator running the ledger archive. Outside this task's write scope;
not acted on.
