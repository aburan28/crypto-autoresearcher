# EXP-VOLC-9f5571 -- implementation note

Task `TASK-20260810-a431bd`, goal `GOAL-ENDO-001`, batch `BATCH-d7e255`, from
Coordinator. Snapshot commit at dispatch: `a9028dcd1`. Run-of-record commit
(recorded in the final run's manifest): `b56fe67db1a39ebe3860ee65294829d90fff4013`,
tree clean at run time.

This note records HOW the frozen contract was executed and WHERE execution
departed from it. It reports observations and deviations, not interpretation.
It does not state a level verdict (SR6) and does not conclude a heuristic
supported or refuted (HEUR-VOLC-1, HEUR-VOLC-2).

## 1. Code

All new code is in two new modules under this task's write_scope (not under
`harness/`, which is outside the declared `write_scope` for this dispatch and
is shared with the concurrently-dispatched `EXP-JINV-bd141d`):

- `experiments/EXP-VOLC-9f5571/runs/_source/volc_graph.py` -- the new Velu
  ell-isogeny graph builder: a dedicated ell=2 formula (`velu2`/`velu2_image`,
  needed because `harness.isogeny_class.velu_odd` refuses ell=2 by design,
  CORR-20260807-3ee25d), a general odd-ell rational-subgroup enumerator
  (`ell_subgroup_generators`, reusing `harness.isogeny_class.velu_odd` per
  subgroup), the isomorphism test `(a,b) ~ (u^4 a, u^6 b)` used to resolve a
  Velu image to a vertex in the enumerated class, and the graph-level/BFS
  level-assignment algorithm (leaf-prune to the 2-core = crater, then BFS
  distance).
- `experiments/EXP-VOLC-9f5571/runs/_source/volc_driver.py` -- the run
  driver, executed standalone (`python3 <path>`, not `python3 -m harness.X`)
  specifically so its source lives inside `runs/` and the dispatch's
  write_scope is honoured literally.

`harness/exp_icinv.py` was **not edited** (source_constraints,
invalidation_rules); it is imported read-only, as are `harness.isogeny_class`,
`harness.toycurve` and `harness.exp_icinv_fullgroup` (`targets_B`, the
certified full-group sampler, and its supporting `build_curve_package` /
`measure_curve_all_arms` / `stratified_stats` / `nullb` machinery, all reused
rather than reimplemented). Every executed source file is pinned by sha256 in
the run manifest (`harness/runner.py:source_provenance`); `all_pinned: true`
on the run of record.

## 2. Objects computed, and the two defects found and repaired before this run
was reported

**`velu2`, first draft, wrong.** The first draft doubled the Velu `v_Q` term
for the ell=2 kernel point exactly as the odd-ell code does for a +/- pair
(`v = 2*(3x0^2+a)`), which is correct only when a distinct `-Q` is paired with
`Q`. A 2-torsion point is its own negative, so it contributes once, not
twice: `v = 3x0^2+a` (no factor of 2). Caught immediately, before touching
any other stage, by testing the very first Velu-2 image against the trace it
should have preserved (30) -- it returned trace -15. Fixed in
`volc_graph.velu2`/`velu2_image`; SR1 then reproduced the committed p=4001
level distribution `{0:3, 1:9, 2:18, 3:36, 4:72}` exactly, with zero unmatched
Velu images out of 270 directed edges.

**Two seed-coverage defects in the SR3/SR4 measurement stage**, found and
superseded across three run ids (immutability discipline: none deleted, each
superseded run carries a `SUPERSEDED.md` explaining the defect and pointing
to the correction):

1. `RUN-VOLC-sr1-sr5-plus-t5-gate` -- SR4's null-fires determination called
   `harness.exp_icinv_fullgroup.nullb` on the **pooled** hit list across both
   declared halves, ignoring the half labels entirely: a no-op with respect
   to the split under test.
2. `RUN-VOLC-sr1-sr5-plus-t5-gate-v2` -- corrected (1) with a per-half
   `stratified_stats` own-null test, but `harness.exp_icinv_fullgroup.
   measure_curve_all_arms` reads the MODULE-LEVEL constants `fg.SEEDS`/
   `fg.TARGET_COUNTS` (the frozen EXP-ICINV-4d33aa grid) rather than the
   `seeds=`/`target_counts=` this driver passed into `build_curve_package`,
   so only the one seed (`11235813`) and two T values (`100`, `400`) common
   to both grids were ever actually scored -- 1 of this contract's 8 declared
   seeds, silently.
3. `RUN-VOLC-sr1-sr5-plus-t5-gate-v3` -- **the run of record.** Overrides
   `fg.SEEDS`/`fg.TARGET_COUNTS` to this contract's own declared grid once,
   at driver start, before any measurement call. All 8 declared seeds and
   both T values are present in every cell count (verified: `112 = 7 fb_sizes
   x 8 seeds x 2 T` cells for the f=3-arm measurement).

Full per-curve support certification (`targets_B` support == enumerated
`E(F_p)`) was run and passed on every one of the 79 measured curves (42 in
the f=3 arm, 37 in the f=107/T5 class) in every superseded and superseding
run; that part of SR3 was never wrong.

## 3. The mid-run discovery that dominates this run's terminal state

The matched-order family fixes `N = #E(F_p) = 19507`, which the design
document (`analysis/endomorphism-isogeny-decomposition/MATCHED-ORDER-DESIGN.md`
sec 3) states is prime and this run's own Stage 1 re-derives as prime. By
Lagrange's theorem, `E(F_p)` then has **zero points of order `ell`** for any
`ell != N`, in particular for `ell = 3` and `ell = 107` -- the two
conductor-arm isogeny degrees `level_construction` specifies (`N mod 3 = 1`,
`N mod 107 = 33`, both re-derived here, not assumed).

Verified empirically (`kernel_rationality_check` stage, not just cited): an
exhaustive liftable-`x` scan for points of order 3 on every one of the 42
f=3-arm curves, and of order 107 on every one of the 37 f=107/T5-class
curves, found **zero** rational order-`ell` subgroups anywhere in either
class (`kernel-rationality-check` block inside every run's `raw-result.json`;
also written standalone in `volcano-graph.json`).

Consequence, stated precisely rather than worked around: Velu's classical
formulas, as implemented here (and as available anywhere in this harness),
require an explicit rational kernel point. A Galois-stable-but-not-pointwise-
rational subgroup of order `ell` can still define a genuine `F_p`-rational
isogeny (as a morphism), but building it needs either (a) arithmetic over a
field extension of `F_p` to represent an actual kernel generator -- which
`harness.toycurve.EllipticCurve` (F_p only) does not provide -- or (b) the
classical modular polynomial `Phi_ell(j(E), Y)` and its root count in `F_p`,
which is not available in this harness for `ell = 3` (small, but not
implemented) let alone `ell = 107` (a degree-108 bivariate polynomial). Both
paths were judged out of this dispatch's scope and budget to implement
correctly and independently-verifiably; the risk of a silently wrong isogeny
graph was judged worse than an honest UNREACHED (AGENTS.md rule 5, rule 9).

This blocks, for BOTH conductor-arm classes: the explicit within-class Velu
graph, the per-level vertex counts and everything downstream of them (the
chi-square detection floor tied to actual per-level counts, the r-by-level
contingency table's level column), T5 branch (i) (a walk on a graph that does
not exist here) and branch (ii) (the local test, for the reasons above), and
the T1 transport certificate (needs a real graph edge). All are recorded
`UNREACHED` with this same cited reason, not imputed and not silently
omitted.

## 4. What WAS executed, with real numbers

- **SR1 (Velu gate):** PASS. `{0:3, 1:9, 2:18, 3:36, 4:72}` reproduced
  exactly on the rebuilt p=4001 2-volcano, 270 directed edges, 0 unmatched.
- **SR2 (family + census):** family re-derivation reproduces the design
  document's own numbers exactly: 59 total candidate classes at N=19507, 51
  at f=1, 7 at f=3, 1 at f=107 (t=211, p=19717, matching the document's cited
  class exactly). Chosen f=3 arm: **t=-173, p=19333, D0=-5267**, selected by
  the disclosed rule "smallest total class size among the f=3 candidates, for
  tractability" (42 curves; the other six candidates range 45-70 curves).
  Class census (Hurwitz-Kronecker weighted count) agrees exactly on both
  chosen classes; `#E(F_p) = 19507` verified per curve on all 42 + 37 curves.
- **SR3 (support gate) + rate measurement:** `targets_B` support certified
  equal to the enumerated `E(F_p)` on every one of the 79 measured curves,
  zero failures. Decomposition rates (`rate_m3`, `rate_m2`) measured via arm
  B only (`targets_uniform` never called; `self_audit_no_null_c`-style
  discipline: `permutation_null`/NULL-C never called anywhere in this
  module), swept over 7 factor-base sizes (`[4,6,8,10,13,17,22]`), all 8
  declared seeds, T in `{100, 400}`. `r = #{x: x^3+ax+b=0}` is **0 on every
  curve in both classes**: `N = 19507` is odd (prime), so `E(F_p)` has no
  rational 2-torsion at all on any curve of this order (a direct consequence
  of the same family design, re-derived here, not assumed) -- the
  contingency table therefore has exactly one row, reported as such rather
  than padded.
- **SR4 (matched null, written before any real level contrast -- and none
  was reachable):** two null instances, each on an `f=1` class from the same
  family, split by index cut (no curve property used) into sizes matched to
  the real conductor-arm classes by an **independent, non-graph** method
  (Hurwitz class-number counts `h(D0)` / `h(D0*ell^2)`, disclosed as such --
  it sizes the split, it does not identify which curves would be crater or
  floor):
  - sized to the f=3 arm (14/28, exact match): class t=35, p=19541, D0=-76939,
    h=42.
  - sized to the f=107/T5 class (1/35, one short of the real 36-vertex floor
    -- no f=1 class in this family has exactly 37 curves; disclosed, not
    reconciled): class t=-133, p=19373, D0=-59803, h=36.

  Verdict computation: per (fb_size, seed, T) cell, each declared half's OWN
  binomial-over-dispersion test (`harness.exp_icinv_fullgroup.
  stratified_stats`, the same per-stratum own-null mechanism used elsewhere
  in this codebase for EXP-ICINV-4d33aa) against its own null variance and
  degrees of freedom. Both null instances show `NULL_FIRES_OVERDISPERSION_
  DETECTED` under an "any cell, any half over-dispersed" rule: f=3-sized null
  has 3 of 96 half-tests over-dispersed (~3.1%); f=107-sized null has 4 of 48
  half-tests over-dispersed (~8.3%, all in the n=35 half -- the n=1 half can
  never produce an own-null test). Both rates are consistent with, though the
  second is somewhat above, the ~5% false-positive rate expected from
  applying a 95% acceptance band independently across many cells (no
  multiple-testing correction was applied; none is prescribed by the
  contract for this cell). **This is reported as observed, uninterpreted**:
  whether it reflects real within-class-of-this-order over-dispersion
  (consistent with the campaign's own prior committed characterisations of
  generic within-class over-dispersion, e.g. EXP-ICINV-4d33aa) or is
  multiple-testing noise at this grid size is not adjudicated here. A plain
  pooled (non-split-aware) over-dispersion statistic is also reported per
  cell (`pooled_over_dispersion_NOT_split_aware`) for contrast; it never
  fires, since neither null class shows overall over-dispersion relative to
  the pooled binomial -- consistent with the per-half signal being small and
  possibly noise-level rather than a large, obvious effect.

## 5. SR5, T5, transport, SR6

- **SR5 (floor before effect):** UNREACHED. No per-level counts exist to
  compute a floor from (section 3); recorded as such, not fabricated from
  the matched-null's per-half floors, which are a different object (sizing
  and content both differ from a real per-level floor).
- **T5 (branch i, walk; branch ii, local test; verdict):** UNREACHED for the
  same graph-construction reason. The T5 verdict is explicitly recorded as
  `UNREACHED`, NOT as `neither` -- `neither` (falsification F6) means both
  branches were evaluated and both failed, a real negative result; here
  neither branch was evaluable at all, a different and weaker claim, and
  conflating the two would misrepresent an unreached cell as a measured
  negative.
- **T1 transport certificate:** UNREACHED, same reason.
- **SR6 (blocking instrument gate):** never approached in this run. SR6
  gates reading a LEVEL VERDICT computed from real per-level data; that data
  is itself UNREACHED for the independent, prior reason in section 3, so
  SR6's own gate is moot for this run -- not satisfied, not bypassed.
  `EXP-INSTR-36c8cf` status as of dispatch (Phase A stopped at its own
  falsification criterion with no interval accepted; Phase B not run) is
  recorded verbatim in `sr6` inside every run's `raw-result.json`, per the
  handoff, without being read as though it discharged the gate.
- **Final level verdict: WITHHELD**, for two independently-recorded reasons
  (SR6, and the prior data-unreachability), never conflated into one.

## 6. Randomness

Seeds: the 8 declared in the contract's `replication.seeds`
(`[20260810, 20260811, 11235813, 20260812, 20260813, 20260814, 20260815,
20260816]`), governing target draws in `targets_B` via
`hashlib.sha256(f"{seed}:...")`, exactly as `harness.exp_icinv_fullgroup`
implements it. No other randomness is used anywhere in this run (the graph
construction, family search and census are fully deterministic; no walk was
reachable to seed).

## 7. Policy / inference

This dispatch's requested policy is `executor-implementation`
(`fallback_allowed: false`, `degraded_allowed: false`); it was honoured by
this Claude Code executor session (model: Claude Sonnet 5, `claude-sonnet-5`)
with no fallback or degradation. Every individual run's own `inference` block
in its manifest reads `resolved_model_id: "none (deterministic harness
execution)"` -- correctly: the runs themselves are deterministic Python with
no model in the decision loop, which is `harness/runner.py`'s own documented
distinction between the agent that executed the task and the (absent) model
inside a harness run.

## 8. Budget

Total wall-clock across all four runs (`RUN-VOLC-sr1-sr5-plus-t5-gate{,-v2,
-v3}` plus the earlier standalone unit tests during development): well under
one minute of measured wall time per run (`v3`: 35.3s), far inside the
21600s per-run / 36 CPU-hour / 24-run budget. No budget event (SR8) occurred.
